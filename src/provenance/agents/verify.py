"""Deterministic answer checks: citations point at real evidence, and every number the answer
states appears in the evidence it cites. Catches invented figures without an LLM call.
Calibrated, claim-level confidence is M6; this is the floor under it.
"""

import re

from provenance.agents.types import Evidence, Verification

# "[P1]" or a group "[P1, F2]".
CITATION = re.compile(r"\[([PF]\d+(?:\s*,\s*[PF]\d+)*)\]")
DECLINE = "INSUFFICIENT_EVIDENCE"

# A number, optionally with $ and a scale word: "$95.4 billion", "73.6%", "1,234".
_NUMBER = re.compile(
    r"(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)\s*(?P<scale>%|percent|billion|million|thousand|bn|mn|[bmk]\b)?",
    re.IGNORECASE,
)
_SCALES = {
    "billion": 1e9, "bn": 1e9, "b": 1e9,
    "million": 1e6, "mn": 1e6, "m": 1e6,
    "thousand": 1e3, "k": 1e3,
}  # fmt: skip
# Filings print tables in thousands or millions, and answers round, so matching allows for
# both: equal at any of these scales, within this relative tolerance.
_TABLE_SCALES = (1.0, 1e3, 1e6, 1e9)
_TOLERANCE = 0.006
# Derived figures (differences, sums, ratios, % changes of two cited numbers) are allowed:
# comparing is the point of many questions. Rounded percentages get an absolute margin.
_DERIVED_TOLERANCE = 0.01
_PERCENT_MARGIN = 0.06
_MAX_PAIRED = 60  # bounds the pairwise search, and the odds of a coincidental match


def numbers_in(text: str) -> list[tuple[str, float]]:
    """(as written, value) for each number, skipping years and citation markers."""
    found = []
    for m in _NUMBER.finditer(CITATION.sub(" ", text)):
        raw = m.group("num").replace(",", "")
        value = float(raw)
        scale = (m.group("scale") or "").lower()
        if not scale and "." not in raw and 1990 <= value <= 2100:
            continue  # a year
        if scale in _SCALES:
            value *= _SCALES[scale]
        found.append((m.group(0).strip(), value))
    return found


def number_supported(value: float, evidence_values: list[float]) -> bool:
    if value == 0:
        return 0.0 in evidence_values
    for ev in evidence_values:
        for scale in _TABLE_SCALES:
            if abs(ev * scale - value) <= _TOLERANCE * abs(value):
                return True
            if abs(ev - value * scale) <= _TOLERANCE * abs(ev) and ev != 0:
                return True
    return False


def number_derived(value: float, evidence_values: list[float]) -> bool:
    values = list(dict.fromkeys(v for v in evidence_values if v != 0))[:_MAX_PAIRED]
    target = abs(value)
    for i, a in enumerate(values):
        for b in values[i + 1 :]:
            candidates = (a + b, abs(a - b), a / b, b / a, a / b * 100, b / a * 100,
                          abs(a - b) / abs(b) * 100, abs(a - b) / abs(a) * 100)  # fmt: skip
            for c in candidates:
                margin = _PERCENT_MARGIN if c < 1000 else 0.0
                if abs(c - target) <= max(_DERIVED_TOLERANCE * abs(c), margin):
                    return True
    return False


def is_small_count(written: str) -> bool:
    """'3 segments', '2 years': small whole numbers are counts, not figures to verify."""
    return written.isdigit() and int(written) < 10


def verify(answer: str, evidence: list[Evidence]) -> Verification:
    if answer.strip() == DECLINE:
        return Verification(ok=True)
    by_id = {e.id: e for e in evidence}
    cited = [c.strip() for group in CITATION.findall(answer) for c in group.split(",")]
    unknown = sorted({c for c in cited if c not in by_id})
    cited_values = [v for c in set(cited) if c in by_id for _, v in numbers_in(by_id[c].text)]
    unsupported = [
        written
        for written, value in numbers_in(answer)
        if not is_small_count(written)
        and not number_supported(value, cited_values)
        and not number_derived(value, cited_values)
    ]
    uncited = not cited
    return Verification(
        ok=not (unknown or unsupported or uncited),
        unknown_citations=unknown,
        unsupported_numbers=sorted(set(unsupported)),
        uncited=uncited,
    )
