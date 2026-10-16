"""The answer-quality gate: re-asks a fixed set of golden questions with the real agent and
fails on a regression in correctness, faithfulness or refusals, or on any access leak.

uv run python -m eval.answer_gate            # check against eval/answer_thresholds.yaml
uv run python -m eval.answer_gate --record   # record the baseline from the latest agent eval

Unlike the retrieval gate this calls free-tier models (Gemini and Groq keys as repository
secrets) and an LLM judge, so it is slower, noisier and rate-limited. Hence:
- a small fixed set: the first five *judged* questions of each category in the latest agent
  eval (questions there were skipped in quota order, not by difficulty), kept by id;
- tolerances wider than the retrieval gate's, a few questions' worth on each metric;
- if too few questions get answered (quota), the result is inconclusive: a warning, not a
  failure, since a rate limit says nothing about the change under review.
Floors are recorded, never tuned to make a run pass.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from glob import glob
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel

from eval.answer_eval import CASES, evaluate
from eval.schema import GoldenCase

THRESHOLDS = Path("eval/answer_thresholds.yaml")
REPORTS = Path("eval/reports")
PER_CATEGORY = 5
MIN_JUDGED = 20  # of 25: below this the run is inconclusive (quota), not a regression
TOLERANCE = {"correct": 0.15, "faithfulness": 0.05, "declines_when_it_should": 0.2}


class AnswerBaseline(BaseModel):
    recorded: str
    source: str
    cases: list[str]
    measured: dict[str, float]
    floors: dict[str, float]
    max_leaks: int = 0


def metrics(rows: list[dict[str, Any]]) -> dict[str, float]:
    answerable = [r for r in rows if not r.get("expect_abstain")]
    unanswerable = [r for r in rows if r.get("expect_abstain")]
    faith = [r["faithfulness"] for r in rows if r.get("faithfulness") is not None]
    return {
        "correct": sum(r.get("correct") == "yes" for r in answerable) / max(len(answerable), 1),
        "faithfulness": sum(faith) / max(len(faith), 1),
        "declines_when_it_should": sum(bool(r.get("declined")) for r in unanswerable)
        / max(len(unanswerable), 1),
    }


def leaks(rows: list[dict[str, Any]]) -> int:
    return sum(len(r.get("leaked") or []) for r in rows)


def record() -> AnswerBaseline:
    path = sorted(glob(str(REPORTS / "answers-agent-*.json")))[-1]
    rows = json.loads(Path(path).read_text("utf-8"))
    order = [GoldenCase.model_validate_json(x) for x in CASES.read_text("utf-8").splitlines()]
    judged = {r["case"]: r for r in rows if r.get("correct") is not None}
    taken: dict[str, int] = {}
    chosen = []
    for case in order:
        if case.id in judged and taken.get(case.category, 0) < PER_CATEGORY:
            taken[case.category] = taken.get(case.category, 0) + 1
            chosen.append(judged[case.id])
    measured = {k: round(v, 3) for k, v in metrics(chosen).items()}
    return AnswerBaseline(
        recorded=datetime.now(UTC).strftime("%Y-%m-%d"),
        source=Path(path).name,
        cases=[r["case"] for r in chosen],
        measured=measured,
        floors={k: round(max(v - TOLERANCE[k], 0.0), 3) for k, v in measured.items()},
    )


def main(do_record: bool) -> int:
    load_dotenv()
    if do_record:
        baseline = record()
        THRESHOLDS.write_text(
            "# Answer-quality gate baseline (eval/answer_gate.py). Re-record deliberately, in its\n"
            "# own commit; never edit the floors to make a run pass.\n"
            + yaml.safe_dump(baseline.model_dump(), sort_keys=False),
            encoding="utf-8",
            newline="\n",
        )
        print(f"recorded {len(baseline.cases)} cases from {baseline.source}: {baseline.measured}")
        return 0

    baseline = AnswerBaseline.model_validate(yaml.safe_load(THRESHOLDS.read_text("utf-8")))
    by_id = {
        c.id: c
        for c in (GoldenCase.model_validate_json(x) for x in CASES.read_text("utf-8").splitlines())
    }
    cases = [by_id[i] for i in baseline.cases if i in by_id]
    if sys.platform == "win32":  # psycopg's async mode needs the selector loop
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    rows = asyncio.run(evaluate(cases, "agent"))
    judged = [r for r in rows if r.get("correct") is not None]
    current = metrics(judged)

    lines = [
        "## Answer-quality gate",
        "",
        f"{len(judged)} of {len(cases)} questions judged (baseline from {baseline.source}).",
        "",
        "| check | now | floor | recorded |",
        "|---|---|---|---|",
    ]
    failed = []
    for name, floor in baseline.floors.items():
        ok = round(current[name], 3) >= floor
        failed += [] if ok else [name]
        lines.append(
            f"| {'ok' if ok else 'FAIL'} {name} | {current[name]:.3f} | {floor:.3f} | {baseline.measured[name]:.3f} |"
        )
    leaked = leaks(rows)
    lines.append(f"| {'ok' if leaked <= baseline.max_leaks else 'FAIL'} leaks | {leaked} | 0 | 0 |")
    report = "\n".join(lines) + "\n"
    print(report)
    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        Path(summary).write_text(report, encoding="utf-8")

    if leaked > baseline.max_leaks:
        print("::error::an answer contained data from outside the principal's groups")
        return 1
    if len(judged) < MIN_JUDGED:
        print(
            f"::warning::only {len(judged)} of {len(cases)} questions answered (free-tier quota); inconclusive"
        )
        return 0
    if failed:
        print(f"::error::answer quality regressed: {', '.join(failed)}")
        return 1
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", action="store_true")
    sys.exit(main(parser.parse_args().record))
