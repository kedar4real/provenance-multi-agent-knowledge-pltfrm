"""The retrieval regression gate: runs on every PR, needs no LLM and no API keys.

uv run python -m eval.gate            # check against eval/thresholds.yaml (exit 1 on regression)
uv run python -m eval.gate --record   # re-record the baseline (a deliberate act, reviewed in the PR)

Runs configuration c (hybrid search + cross-encoder rerank) over every golden case with gold
passages, exactly as the retrieval eval does, and fails if any metric drops below its floor,
if any principal sees another sector's data, or if cases were removed (a smaller set can
flatter every metric). Floors are the recorded measurement minus a fixed tolerance for
numerical differences between machines; they are never raised or lowered to hit a target.
Re-record only when the golden set or the pipeline legitimately changes, in its own commit.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel

from eval.retrieval_metrics import CASES, evaluate
from eval.schema import GoldenCase

THRESHOLDS = Path("eval/thresholds.yaml")
CONFIG = "c"
METRICS = ("r1", "r5", "r10", "mrr", "ndcg")
TOLERANCE = 0.03  # absolute; about 4 of ~130 cases on Recall@1


class Baseline(BaseModel):
    config: str
    recorded: str
    n: int
    tolerance: float
    measured: dict[str, float]
    floors: dict[str, float]
    max_acl_leaks: int = 0


class Check(BaseModel):
    name: str
    value: float
    bound: float
    ok: bool
    note: str = ""


def means(result: dict[str, Any]) -> dict[str, float]:
    return {m: float(result["metrics"][m]["mean"]) for m in METRICS}


def make_baseline(result: dict[str, Any], tolerance: float = TOLERANCE) -> Baseline:
    measured = means(result)
    return Baseline(
        config=str(result["config"]),
        recorded=datetime.now(UTC).strftime("%Y-%m-%d"),
        n=int(result["n"]),
        tolerance=tolerance,
        measured={k: round(v, 3) for k, v in measured.items()},
        floors={k: round(v - tolerance, 3) for k, v in measured.items()},
    )


def check(result: dict[str, Any], baseline: Baseline) -> list[Check]:
    current = means(result)
    checks = [
        Check(name=m, value=round(current[m], 3), bound=baseline.floors[m],
              ok=round(current[m], 3) >= baseline.floors[m],
              note=f"recorded {baseline.measured[m]:.3f}")
        for m in METRICS
    ]  # fmt: skip
    leaks = len(result["acl"]["leaks"])
    checks.append(Check(name="acl_leaks", value=leaks, bound=baseline.max_acl_leaks,
                        ok=leaks <= baseline.max_acl_leaks, note="must be zero"))  # fmt: skip
    n = int(result["n"])
    checks.append(Check(name="cases", value=n, bound=baseline.n, ok=n >= baseline.n,
                        note="cases with gold passages; fewer can flatter the metrics"))  # fmt: skip
    return checks


def table(checks: list[Check]) -> str:
    lines = ["| check | value | bound | |", "|---|---|---|---|"]
    for c in checks:
        mark = "ok" if c.ok else "**FAIL**"
        lines.append(f"| {c.name} | {c.value:g} | {c.bound:g} | {mark} {c.note} |")
    return "\n".join(lines)


def main(record: bool) -> int:
    load_dotenv(".env")
    cases = [GoldenCase.model_validate_json(x) for x in CASES.read_text("utf-8").splitlines()]
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    (result,) = asyncio.run(evaluate([CONFIG], cases))
    if record:
        baseline = make_baseline(result)
        THRESHOLDS.write_text(yaml.safe_dump(baseline.model_dump(), sort_keys=False), "utf-8")
        print(f"recorded {THRESHOLDS}: measured {baseline.measured}, floors {baseline.floors}")
        return 0
    baseline = Baseline.model_validate(yaml.safe_load(THRESHOLDS.read_text("utf-8")))
    checks = check(result, baseline)
    report = f"## Retrieval gate (config {CONFIG}, {result['n']} cases)\n\n{table(checks)}\n"
    print(report)
    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        Path(summary).write_text(report, "utf-8")
    Path("eval/reports").mkdir(parents=True, exist_ok=True)
    Path("eval/reports/gate-latest.json").write_text(
        json.dumps({"checks": [c.model_dump() for c in checks]}, indent=2), "utf-8"
    )
    failed = [c.name for c in checks if not c.ok]
    if failed:
        print(f"GATE FAILED: {', '.join(failed)}")
        return 1
    print("gate passed")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    sys.exit(main(parser.parse_args().record))
