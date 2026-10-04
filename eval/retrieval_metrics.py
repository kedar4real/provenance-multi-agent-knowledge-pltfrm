"""Retrieval quality on the golden set, per configuration. Deterministic except config d.

uv run python -m eval.retrieval_metrics                  # configs a, b, c
uv run python -m eval.retrieval_metrics --configs a b c d

  a  dense only                       (embeddings)
  b  hybrid: dense + BM25, RRF        (no models beyond the embedder)
  c  hybrid + cross-encoder rerank
  d  c + LLM query rewrite            (calls the LLM; recorded in .llm_cache/)

Metrics on cases with gold passages (text, cross): Recall@1/5/10 (a gold passage in the
top k), MRR@10, nDCG@10, each with a 95% bootstrap interval. ACL check on adversarial cases:
any hit from a forbidden company is a leak, and the expected number is zero. Every query
runs as the case's principal, through row-level security, like a real request.
"""

import argparse
import asyncio
import json
import math
import os
import random
import statistics
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector_async
from psycopg import AsyncConnection

from eval.schema import GoldenCase, chunk_key
from provenance.config import Settings
from provenance.db.security import principal_sql
from provenance.llm.cache import CachedLLM, ResponseCache
from provenance.llm.factory import build_router, load_config
from provenance.retrieval.embeddings import Embedder
from provenance.retrieval.hybrid import HybridRetriever
from provenance.retrieval.rerank import Reranker
from provenance.retrieval.rewrite import QueryRewriter
from provenance.retrieval.types import Mode

CASES = Path("eval/golden/cases.jsonl")
REPORTS = Path("eval/reports")
K = 10
BOOTSTRAP_SAMPLES = 2000


@dataclass(frozen=True)
class Config:
    name: str
    label: str
    mode: Mode
    rerank: bool
    rewrite: bool


CONFIGS = {
    "a": Config("a", "dense only", "dense", False, False),
    "b": Config("b", "hybrid (dense + BM25, RRF)", "hybrid", False, False),
    "c": Config("c", "hybrid + rerank", "hybrid", True, False),
    "d": Config("d", "hybrid + rerank + rewrite", "hybrid", True, True),
}


def ranks_of_gold(retrieved: list[str], gold: set[str]) -> list[int]:
    return [i for i, key in enumerate(retrieved, start=1) if key in gold]


def recall_at(retrieved: list[str], gold: set[str], k: int) -> float:
    return 1.0 if any(key in gold for key in retrieved[:k]) else 0.0


def reciprocal_rank(retrieved: list[str], gold: set[str], k: int = K) -> float:
    ranks = ranks_of_gold(retrieved[:k], gold)
    return 1.0 / ranks[0] if ranks else 0.0


def ndcg_at(retrieved: list[str], gold: set[str], k: int = K) -> float:
    """Binary relevance. Gold sets hold near-duplicates of one passage, so the ideal ranking
    is one relevant hit at rank 1, and extra copies of the same evidence add no credit."""
    ranks = ranks_of_gold(retrieved[:k], gold)
    return 1.0 / math.log2(ranks[0] + 1) if ranks else 0.0


def bootstrap_ci(values: list[float], seed: int = 0) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    rng = random.Random(seed)
    means = sorted(
        statistics.fmean(rng.choices(values, k=len(values))) for _ in range(BOOTSTRAP_SAMPLES)
    )
    return (means[int(0.025 * BOOTSTRAP_SAMPLES)], means[int(0.975 * BOOTSTRAP_SAMPLES) - 1])


async def run_config(
    config: Config,
    retriever: HybridRetriever,
    conn: AsyncConnection,
    cases: list[GoldenCase],
    keys_by_id: dict[int, str],
    signing_key: str,
) -> dict[str, object]:
    per_case: list[dict[str, object]] = []
    leaks: list[dict[str, object]] = []
    top_scores: dict[str, list[float]] = {"answerable": [], "unanswerable": []}
    started = time.perf_counter()
    for case in cases:
        async with conn.transaction():
            sql, params = principal_sql(case.groups, signing_key)
            await conn.execute(sql, params)
            result = await retriever.search(
                conn, case.question, k=K, mode=config.mode,
                rerank=config.rerank, rewrite=config.rewrite,
            )  # fmt: skip
        retrieved = [keys_by_id[h.chunk_id] for h in result.hits]
        if case.forbidden_tickers:
            leaked = sorted({h.ticker for h in result.hits} & set(case.forbidden_tickers))
            if leaked:
                leaks.append({"case": case.id, "leaked": leaked})
        if config.rerank and result.hits:
            bucket = "unanswerable" if case.category == "unanswerable" else "answerable"
            top_scores[bucket].append(max(h.rerank_score or 0.0 for h in result.hits))
        if not case.gold_chunks:
            continue
        gold = set(case.gold_chunks)
        per_case.append(
            {
                "case": case.id,
                "category": case.category,
                "r1": recall_at(retrieved, gold, 1),
                "r5": recall_at(retrieved, gold, 5),
                "r10": recall_at(retrieved, gold, 10),
                "mrr": reciprocal_rank(retrieved, gold),
                "ndcg": ndcg_at(retrieved, gold),
                "first_gold_rank": next(iter(ranks_of_gold(retrieved, gold)), None),
                "rewrite": result.rewrite,
                "ms": round(sum(result.timings_ms.values())),
            }
        )
    metrics: dict[str, object] = {}
    for name in ("r1", "r5", "r10", "mrr", "ndcg"):
        values = [float(c[name]) for c in per_case]  # type: ignore[arg-type]
        low, high = bootstrap_ci(values)
        metrics[name] = {
            "mean": round(statistics.fmean(values), 3) if values else 0.0,
            "ci95": [round(low, 3), round(high, 3)],
        }
    latencies = sorted(float(c["ms"]) for c in per_case)  # type: ignore[arg-type]
    return {
        "config": config.name,
        "label": config.label,
        "n": len(per_case),
        "metrics": metrics,
        "latency_ms": {
            "p50": latencies[len(latencies) // 2] if latencies else 0,
            "p95": latencies[int(len(latencies) * 0.95) - 1] if latencies else 0,
        },
        "acl": {"cases": sum(1 for c in cases if c.forbidden_tickers), "leaks": leaks},
        "top_rerank_score": {
            k: round(statistics.median(v), 3) if v else None for k, v in top_scores.items()
        },
        "wall_s": round(time.perf_counter() - started, 1),
        "per_case": per_case,
    }


def _cell(metrics: dict[str, dict[str, object]], name: str) -> str:
    v = metrics[name]
    ci = v["ci95"]
    assert isinstance(ci, list)
    return f"{v['mean']:.3f} [{ci[0]:.2f}-{ci[1]:.2f}]"


def markdown(results: list[dict[str, object]], n_cases: int) -> str:
    lines = [
        f"# Retrieval eval ({datetime.now(UTC):%Y-%m-%d %H:%M} UTC)",
        "",
        f"{n_cases} golden cases; metrics over those with gold passages. 95% bootstrap CIs.",
        "",
        "| config | n | R@1 | R@5 | R@10 | MRR@10 | nDCG@10 | p50 ms | ACL leaks |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        m, acl, lat = r["metrics"], r["acl"], r["latency_ms"]
        assert isinstance(m, dict) and isinstance(acl, dict) and isinstance(lat, dict)
        cells = " | ".join(_cell(m, name) for name in ("r1", "r5", "r10", "mrr", "ndcg"))
        lines.append(
            f"| {r['config']} {r['label']} | {r['n']} | {cells} | {lat['p50']:.0f} | "
            f"{len(acl['leaks'])}/{acl['cases']} |"
        )
    return "\n".join(lines) + "\n"


async def evaluate(config_names: list[str], cases: list[GoldenCase]) -> list[dict[str, object]]:
    settings = Settings()
    with psycopg.connect(settings.owner_dsn) as owner:
        rows = owner.execute(
            "SELECT c.id, d.accession, c.section, c.char_start FROM chunks c"
            " JOIN documents d ON d.id = c.document_id"
        ).fetchall()
        companies: dict[str, str] = dict(
            owner.execute("SELECT ticker, name FROM companies").fetchall()
        )
    keys_by_id = {r[0]: chunk_key(r[1], r[2], r[3]) for r in rows}
    missing = {k for c in cases for k in c.gold_chunks} - set(keys_by_id.values())
    if missing:
        print(f"warning: {len(missing)} gold passages no longer exist (re-chunked?)")

    embedder = Embedder(threads=os.cpu_count() or 4)
    reranker = Reranker() if any(CONFIGS[n].rerank for n in config_names) else None
    rewriter = None
    if any(CONFIGS[n].rewrite for n in config_names):
        llm = CachedLLM(
            build_router(load_config(Path("config/llm.yaml"))),
            ResponseCache(Path(".llm_cache")),
            "read_write",
        )
        rewriter = QueryRewriter(llm, companies)
    retriever = HybridRetriever(embedder, reranker, rewriter)

    results = []
    async with await AsyncConnection.connect(settings.app_dsn) as conn:
        await register_vector_async(conn)
        await conn.commit()
        for name in config_names:
            print(f"config {name}: {CONFIGS[name].label} ...", flush=True)
            result = await run_config(
                CONFIGS[name], retriever, conn, cases, keys_by_id,
                settings.rls_signing_key.get_secret_value(),
            )  # fmt: skip
            results.append(result)
            print(f"  done in {result['wall_s']}s", flush=True)
    return results


def main(config_names: list[str]) -> None:
    load_dotenv(".env")
    lines = CASES.read_text("utf-8").splitlines()
    cases = [GoldenCase.model_validate_json(line) for line in lines]
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(evaluate(config_names, cases))

    REPORTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M")
    report = markdown(results, len(cases))
    (REPORTS / f"retrieval-{stamp}.json").write_text(json.dumps(results, indent=2), "utf-8")
    (REPORTS / f"retrieval-{stamp}.md").write_text(report, "utf-8")
    print("\n" + report)
    for r in results:
        print(f"config {r['config']} median top rerank score:", r["top_rerank_score"])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs", nargs="+", choices=list(CONFIGS), default=["a", "b", "c"])
    main(parser.parse_args().configs)
