"""Human spot-check of the golden set: sample cases, review them, record verdicts.

uv run python -m eval.spotcheck sample      # writes eval/golden/spot_check.md (40 cases)
uv run python -m eval.spotcheck apply       # reads your marks back into cases.jsonl

In spot_check.md, each case has a line `verdict: [ ]`. Put `x` for keep, or `bad` plus a
short reason for anything wrong (unanswerable from the evidence, ambiguous, wrong answer,
leaks the answer in the question). `apply` sets human_checked on kept cases and moves bad
ones to rejected.jsonl, and prints the agreement rate with the LLM judge, which is the
number the README reports.
"""

import random
import re
import sys
from pathlib import Path

import psycopg

from eval.generate import CASES, REJECTED
from eval.schema import GoldenCase
from provenance.config import Settings

SHEET = Path("eval/golden/spot_check.md")
SAMPLE_SIZE = 40
SEED = 7
_VERDICT = re.compile(r"^verdict: \[(?P<mark>[^\]]*)\]\s*(?P<reason>.*)$")
_HEADER = re.compile(r"^## (?P<id>\S+)")

_EVIDENCE = """
SELECT substr(c.text, 1, 1200) FROM chunks c JOIN documents d ON d.id = c.document_id
WHERE d.accession = %s AND c.section = %s AND c.char_start = %s
"""


def _load(path: Path) -> list[GoldenCase]:
    if not path.exists():
        return []
    return [GoldenCase.model_validate_json(line) for line in path.read_text("utf-8").splitlines()]


def sample() -> None:
    cases = [c for c in _load(CASES) if c.category in ("text", "sql", "cross")]
    rng = random.Random(SEED)
    chosen = rng.sample(cases, min(SAMPLE_SIZE, len(cases)))
    lines = [
        "# Golden-set spot check",
        "",
        "For each case: is the question clear and standalone, and does the evidence fully",
        "support the reference answer? Mark `verdict: [x]` to keep, or `verdict: [bad] reason`.",
        "",
    ]
    with psycopg.connect(Settings().owner_dsn) as conn:
        for case in chosen:
            lines += [f"## {case.id}  ({case.category})", "", f"**Q:** {case.question}", ""]
            lines += [f"**Reference answer:** {case.reference_answer}", ""]
            for fact in case.gold_facts:
                lines.append(
                    f"- fact: {fact.ticker} {fact.metric} FY{fact.fiscal_year} = "
                    f"{fact.value:,.2f} {fact.unit}"
                )
            if case.gold_chunks:
                accession, item, start = case.gold_chunks[0].rsplit(":", 2)
                row = conn.execute(_EVIDENCE, (accession, item, int(start))).fetchone()
                evidence = " ".join((row[0] if row else "(passage missing)").split())
                lines += ["", f"> {evidence}"]
            lines += ["", f"LLM judge: {case.filter_verdict or '-'}", "", "verdict: [ ]", ""]
    SHEET.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {SHEET} ({len(chosen)} cases)")


def apply() -> None:
    marks: dict[str, tuple[str, str]] = {}
    current = None
    for line in SHEET.read_text("utf-8").splitlines():
        if header := _HEADER.match(line):
            current = header["id"]
        elif (verdict := _VERDICT.match(line)) and current:
            marks[current] = (verdict["mark"].strip().lower(), verdict["reason"].strip())
    unmarked = [cid for cid, (mark, _) in marks.items() if not mark]
    if unmarked:
        sys.exit(f"{len(unmarked)} cases still unmarked, e.g. {unmarked[0]}")

    kept, rejected = [], []
    for case in _load(CASES):
        mark = marks.get(case.id)
        if mark is None:
            kept.append(case)
        elif mark[0] == "x":
            kept.append(case.model_copy(update={"human_checked": True}))
        else:
            rejected.append(case.model_copy(update={"filter_verdict": f"human: {mark[1]}"}))
    CASES.write_text("".join(c.model_dump_json() + "\n" for c in kept), encoding="utf-8")
    with REJECTED.open("a", encoding="utf-8") as f:
        f.writelines(c.model_dump_json() + "\n" for c in rejected)
    # Every sampled case had passed the LLM judge, so agreement = share the human kept too.
    agreement = sum(1 for m, _ in marks.values() if m == "x") / len(marks)
    print(f"kept {len(marks) - len(rejected)}/{len(marks)}; human-judge agreement {agreement:.0%}")


if __name__ == "__main__":
    {"sample": sample, "apply": apply}[sys.argv[1] if len(sys.argv) > 1 else "sample"]()
