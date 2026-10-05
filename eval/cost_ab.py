"""Cost A/B: the M5 agent (always the large writer, no cache) vs the same agent behind the
M8 controller (routed tiers, escalation, abstention, answer cache).

uv run python -m eval.answer_eval --system agent
uv run python -m eval.answer_eval --system controller --paraphrases
uv run python -m eval.cost_ab

Both arms answer the same golden questions; their latest reports are compared on the cases
both answered. Cost is API-equivalent (tokens x reference list prices; the real calls are
free tier), so the routed/baseline **ratio** is the headline and doesn't depend much on the
price assumption. The controller arm also answers the cache-eval paraphrases (disclosed
share); the agent arm's cost for those is taken as its cost for the original question.
"""

import glob
import json
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPORTS = Path("eval/reports")


def latest(system: str) -> list[dict[str, Any]]:
    for path in sorted(glob.glob(str(REPORTS / f"answers-{system}-*.json")), reverse=True):
        rows = json.loads(Path(path).read_text("utf-8"))
        if rows and "usage" in rows[0]:
            return list(rows)
    raise SystemExit(f"no metered answers-{system} report yet (run eval.answer_eval first)")


def arm(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    faith = [r["faithfulness"] for r in rows if r["faithfulness"] is not None]
    tokens = [r["usage"]["input_tokens"] + r["usage"]["output_tokens"] for r in rows]
    return {
        "n": n,
        "correct": sum(r["correct"] == "yes" for r in rows) / n,
        "correct_or_partial": sum(r["correct"] in ("yes", "partial") for r in rows) / n,
        "faithfulness": statistics.fmean(faith) if faith else None,
        "declined": sum(bool(r["declined"]) for r in rows) / n,
        "tokens_per_q": statistics.fmean(tokens),
        "cost_per_q": statistics.fmean(r["usage"]["cost_usd"] for r in rows),
        "llm_s_per_q": statistics.fmean(r.get("llm_ms", 0.0) for r in rows) / 1000,
    }


def compare(agent: list[dict[str, Any]], controlled: list[dict[str, Any]]) -> dict[str, Any]:
    by_case = {r["case"]: r for r in agent}
    originals = [r for r in controlled if r["case"] in by_case]
    shared = [by_case[r["case"]] for r in originals]
    paraphrased = [r for r in controlled if r["case"].endswith("-para")]
    paired = [r for r in paraphrased if r["case"].removesuffix("-para") in by_case]
    a, c = arm(shared), arm(originals)
    result: dict[str, Any] = {
        "shared_cases": len(shared),
        "agent": a,
        "controller": c,
        "cost_ratio": c["cost_per_q"] / a["cost_per_q"] if a["cost_per_q"] else None,
        "token_ratio": c["tokens_per_q"] / a["tokens_per_q"] if a["tokens_per_q"] else None,
    }
    if paired:
        control = [r.get("control") or {} for r in paired]
        hits = sum(bool(c.get("cache") and c["cache"]["hit"]) for c in control)
        agent_cost = sum(
            by_case[r["case"].removesuffix("-para")]["usage"]["cost_usd"] for r in paired
        )
        ctrl_cost = sum(r["usage"]["cost_usd"] for r in paired)
        everything = originals + paired
        result["paraphrases"] = {
            "n": len(paired),
            "share_of_query_set": len(paired) / len(everything),
            "cache_hits": hits,
            "correct": sum(r["correct"] == "yes" for r in paired) / len(paired),
            "agent_cost_estimated": agent_cost,
            "controller_cost": ctrl_cost,
        }
        total_agent = sum(r["usage"]["cost_usd"] for r in shared) + agent_cost
        total_ctrl = sum(r["usage"]["cost_usd"] for r in everything)
        result["cost_ratio_with_paraphrases"] = total_ctrl / total_agent if total_agent else None
    return result


def report(result: dict[str, Any]) -> str:
    a, c = result["agent"], result["controller"]

    def pct(v: float | None) -> str:
        return "-" if v is None else f"{v:.0%}"

    lines = [
        f"# Cost A/B ({datetime.now(UTC):%Y-%m-%d %H:%M} UTC)",
        "",
        f"{result['shared_cases']} golden questions answered by both arms. Cost is "
        "API-equivalent: tokens x reference list prices (small = Claude Haiku 4.5, large = "
        "Claude Sonnet 4.5); every real call ran on a free tier.",
        "",
        "| | agent (always large) | controller (routed) |",
        "|---|---|---|",
        f"| correct | {pct(a['correct'])} | {pct(c['correct'])} |",
        f"| correct or partial | {pct(a['correct_or_partial'])} | {pct(c['correct_or_partial'])} |",
        f"| faithfulness | {a['faithfulness'] or 0:.2f} | {c['faithfulness'] or 0:.2f} |",
        f"| declined | {pct(a['declined'])} | {pct(c['declined'])} |",
        f"| tokens / question | {a['tokens_per_q']:,.0f} | {c['tokens_per_q']:,.0f} |",
        f"| API-equivalent $ / question | {a['cost_per_q']:.5f} | {c['cost_per_q']:.5f} |",
        f"| model time / question (s) | {a['llm_s_per_q']:.1f} | {c['llm_s_per_q']:.1f} |",
        "",
        f"**Cost ratio (controller / agent): {result['cost_ratio']:.2f}** "
        f"(tokens: {result['token_ratio']:.2f}).",
    ]
    p = result.get("paraphrases")
    if p:
        lines += [
            "",
            f"With the cache: {p['n']} paraphrased questions ({p['share_of_query_set']:.0%} of "
            f"the controller's query set) asked after their originals: {p['cache_hits']} cache "
            f"hits, {pct(p['correct'])} correct. Cost ratio over the whole query set: "
            f"{result['cost_ratio_with_paraphrases']:.2f} (the agent's cost for a paraphrase "
            "is taken as its cost for the original).",
        ]
    lines += [
        "",
        "Model time sums each call's latency; parallel calls make it an upper bound on "
        "wall-clock time.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    result = compare(latest("agent"), latest("controller"))
    REPORTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M")
    (REPORTS / f"cost-ab-{stamp}.json").write_text(json.dumps(result, indent=2), "utf-8")
    text = report(result)
    (REPORTS / f"cost-ab-{stamp}.md").write_text(text, "utf-8")
    print(text)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    main()
