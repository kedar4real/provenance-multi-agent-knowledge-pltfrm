"""Answer-cache safety: how often a rewording hits, and how often a different question does.

uv run python -m eval.cache_eval pairs   # build eval/golden/cache_pairs.jsonl (LLM paraphrases)
uv run python -m eval.cache_eval sweep   # embed both sides, sweep the threshold, write a report

Positive pairs: a golden question and an LLM paraphrase that keeps its companies, years and
metric ("should hit"). Negative pairs, built deterministically: the same question with the
company, the fiscal year or the metric swapped ("must not hit"): the near-misses an
embedding cache gets wrong, because one changed word barely moves the vector. The sweep
reports the hit rate and the false-hit rate per threshold, with and without the entity
guard. Pairwise, which matches a cache holding the original question.
"""

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import numpy as np
from dotenv import load_dotenv
from pydantic import BaseModel

from eval.generate import RATE_LIMIT_WAITS_S
from eval.schema import GoldenCase
from provenance.controller.cache import signature
from provenance.controller.classifier import METRICS, entities
from provenance.ingest.corpus import COMMON_NAMES, CORPUS
from provenance.llm.cache import CachedLLM, ResponseCache
from provenance.llm.errors import AllProvidersFailed
from provenance.llm.factory import build_router, load_config
from provenance.llm.types import ChatRequest, Message

CASES = Path("eval/golden/cases.jsonl")
PAIRS = Path("eval/golden/cache_pairs.jsonl")
REPORTS = Path("eval/reports")
SEEDS = {"text": 20, "sql": 15, "cross": 15}  # golden questions to build pairs from
THRESHOLDS = (0.80, 0.85, 0.88, 0.90, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99)
ROLE = "bulk"

PARAPHRASE_PROMPT = """Reword this question about SEC 10-K filings the way a different
analyst might ask the same thing. Keep the same companies, fiscal years, numbers and metric;
change the wording and sentence structure.
Return JSON: {"question": str}"""

# Metric swaps for near-misses: a different, plausible metric of the same kind.
METRIC_SWAPS = {
    "revenue": "net income", "net income": "revenue", "operating income": "revenue",
    "eps": "revenue", "gross margin": "operating margin", "capex": "R&D spending",
    "r&d": "capital expenditures", "dividend": "share buybacks", "buyback": "dividends",
    "debt": "cash", "cash": "debt", "employees": "revenue",
}  # fmt: skip
_YEAR = re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)")

Kind = Literal["paraphrase", "company", "year", "metric"]


class Pair(BaseModel):
    id: str
    case: str
    kind: Kind
    original: str
    other: str
    should_hit: bool


def seeds() -> list[GoldenCase]:
    cases = [GoldenCase.model_validate_json(x) for x in CASES.read_text("utf-8").splitlines()]
    taken: dict[str, int] = {}
    chosen = []
    for case in cases:
        quota = SEEDS.get(case.category, 0)
        if taken.get(case.category, 0) < quota:
            taken[case.category] = taken.get(case.category, 0) + 1
            chosen.append(case)
    return chosen


def swap_company(question: str) -> str | None:
    sectors = {c.ticker: c.sector for c in CORPUS}
    for ticker, name in sorted(COMMON_NAMES.items(), key=lambda t: -len(t[1])):
        match = re.search(rf"(?<![\w&]){re.escape(name)}(?![\w&])", question, re.IGNORECASE)
        if match:
            peers = sorted(t for t, s in sectors.items() if s == sectors[ticker] and t != ticker)
            if not peers:
                return None
            return question[: match.start()] + COMMON_NAMES[peers[0]] + question[match.end() :]
    return None


def swap_year(question: str) -> str | None:
    match = _YEAR.search(question)
    if match is None:
        return None
    return question[: match.start(1)] + str(int(match.group(1)) - 1) + question[match.end(1) :]


def swap_metric(question: str) -> str | None:
    for word in sorted(METRICS, key=len, reverse=True):
        match = re.search(rf"\b{re.escape(word)}\b", question, re.IGNORECASE)
        if match and METRICS[word] in METRIC_SWAPS:
            replacement = METRIC_SWAPS[METRICS[word]]
            return question[: match.start()] + replacement + question[match.end() :]
    return None


async def build_pairs() -> list[Pair]:
    llm = CachedLLM(
        build_router(load_config(Path("config/llm.yaml"))), ResponseCache(Path(".llm_cache")),
        "read_write",
    )  # fmt: skip
    pairs: list[Pair] = []
    for case in seeds():
        q = case.question
        for kind, swapped in (
            ("company", swap_company(q)), ("year", swap_year(q)), ("metric", swap_metric(q)),
        ):  # fmt: skip
            if swapped and swapped != q:
                pairs.append(Pair(id=f"{case.id}:{kind}", case=case.id, kind=kind,
                                  original=q, other=swapped, should_hit=False))  # fmt: skip
        paraphrase = await _paraphrase(llm, q)
        if paraphrase and paraphrase.strip().lower() != q.strip().lower():
            pairs.append(Pair(id=f"{case.id}:paraphrase", case=case.id, kind="paraphrase",
                              original=q, other=paraphrase, should_hit=True))  # fmt: skip
        print(f"{case.id}: {sum(p.case == case.id for p in pairs)} pairs", flush=True)
    return pairs


async def _paraphrase(llm: CachedLLM, question: str) -> str | None:
    request = ChatRequest(
        messages=[
            Message(role="system", content=PARAPHRASE_PROMPT),
            Message(role="user", content=question),
        ],
        json_mode=True,
        max_tokens=1000,  # headroom for hidden reasoning tokens
        reasoning_effort="low",
    )
    for wait_s in (*RATE_LIMIT_WAITS_S, None):
        try:
            response = await llm.complete(ROLE, request)
            return str(json.loads(response.content).get("question") or "") or None
        except AllProvidersFailed:
            if wait_s is None:
                return None
            await asyncio.sleep(wait_s)
        except json.JSONDecodeError:
            return None
    return None


def sweep(pairs: list[Pair], similarity: dict[str, float]) -> dict[str, Any]:
    guard = {p.id: signature(entities(p.original)) == signature(entities(p.other)) for p in pairs}
    rows = []
    for t in THRESHOLDS:
        row: dict[str, Any] = {"threshold": t}
        for guarded in (False, True):
            hits = {p.id: similarity[p.id] >= t and (guard[p.id] or not guarded) for p in pairs}
            positives = [p for p in pairs if p.should_hit]
            negatives = [p for p in pairs if not p.should_hit]
            tag = "guarded" if guarded else "embedding_only"
            row[tag] = {
                "hit_rate": _rate(hits[p.id] for p in positives),
                "false_hit_rate": _rate(hits[p.id] for p in negatives),
                **{f"false_hit_{k}": _rate(hits[p.id] for p in negatives if p.kind == k)
                   for k in ("company", "year", "metric")},
            }  # fmt: skip
        rows.append(row)
    by_kind = {
        k: {
            "n": sum(p.kind == k for p in pairs),
            "median_similarity": float(np.median([similarity[p.id] for p in pairs if p.kind == k]))
            if any(p.kind == k for p in pairs) else None,
            "guard_passes": _rate(guard[p.id] for p in pairs if p.kind == k),
        }
        for k in ("paraphrase", "company", "year", "metric")
    }  # fmt: skip
    return {"pairs": len(pairs), "by_kind": by_kind, "sweep": rows}


def _rate(values: Any) -> float | None:
    items = list(values)
    return round(sum(items) / len(items), 3) if items else None


def report(result: dict[str, Any], configured: float) -> str:
    lines = [
        f"# Answer-cache eval ({datetime.now(UTC):%Y-%m-%d %H:%M} UTC)",
        "",
        f"{result['pairs']} labeled pairs from golden questions (embedder: bge-small-en-v1.5).",
        "Paraphrases should hit; company / year / metric swaps must not. Pairwise.",
        "",
        "| pair kind | n | median cosine | entity guard passes |",
        "|---|---|---|---|",
    ]
    for kind, s in result["by_kind"].items():
        median = "-" if s["median_similarity"] is None else f"{s['median_similarity']:.3f}"
        lines.append(f"| {kind} | {s['n']} | {median} | {s['guard_passes']} |")
    lines += [
        "",
        f"Configured threshold: {configured} (set before this sweep).",
        "",
        "| threshold | hit rate (embedding only) | false hits (embedding only) "
        "| hit rate (guarded) | false hits (guarded) |",
        "|---|---|---|---|---|",
    ]
    for row in result["sweep"]:
        e, g = row["embedding_only"], row["guarded"]
        lines.append(
            f"| {row['threshold']:.2f} | {e['hit_rate']} | {e['false_hit_rate']} "
            f"| {g['hit_rate']} | {g['false_hit_rate']} |"
        )
    return "\n".join(lines) + "\n"


def run_sweep() -> None:
    from provenance.controller.policy import Policy
    from provenance.retrieval.embeddings import Embedder
    from provenance.security.pii import redact

    pairs = [Pair.model_validate_json(x) for x in PAIRS.read_text("utf-8").splitlines()]
    embedder = Embedder(threads=os.cpu_count() or 4)
    texts = sorted({t for p in pairs for t in (p.original, p.other)})
    vectors = {t: embedder.embed_query(redact(t)) for t in texts}
    unit = {t: v / np.linalg.norm(v) for t, v in vectors.items()}
    similarity = {p.id: float(unit[p.original] @ unit[p.other]) for p in pairs}
    result = sweep(pairs, similarity)
    configured = Policy.load(Path("config/routing.yaml")).cache.similarity
    REPORTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M")
    text = report(result, configured)
    (REPORTS / f"cache-{stamp}.json").write_text(json.dumps(result, indent=2), "utf-8")
    (REPORTS / f"cache-{stamp}.md").write_text(text, "utf-8")
    print(text)


def main(step: str) -> None:
    load_dotenv(".env")
    if step == "pairs":
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        pairs = asyncio.run(build_pairs())
        PAIRS.write_text("".join(p.model_dump_json() + "\n" for p in pairs), "utf-8")
        print(f"wrote {len(pairs)} pairs to {PAIRS}")
    else:
        run_sweep()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    parser = argparse.ArgumentParser()
    parser.add_argument("step", choices=["pairs", "sweep"])
    main(parser.parse_args().step)
