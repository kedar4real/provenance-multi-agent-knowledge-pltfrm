"""Numbers and citations in answers: parse them, and check a number against evidence.

Shared by the M5 deterministic verifier and the M6 claim signals; imports nothing from
the agent, so both can depend on it.
"""

import re

# "[P1]" or a group "[P1, F2]".
CITATION = re.compile(r"\[([PF]\d+(?:\s*,\s*[PF]\d+)*)\]")
DECLINE = "INSUFFICIENT_EVIDENCE"
# Models sometimes write citations in full-width brackets (U+3010/U+3011 or U+FF3B/U+FF3D).
_WIDE_CITATION = re.compile(
    r"[\u3010\uff3b]\s*([PF]\d+(?:\s*[,\uff0c]\s*[PF]\d+)*)\s*[\u3011\uff3d]"
)


def normalize_citations(text: str) -> str:
    """Rewrite full-width citation brackets as [P1], so every reader of the answer (the
    verifier, the claim signals, the web app) parses one form."""
    return _WIDE_CITATION.sub(
        lambda m: "[" + re.sub(r"\s*[,\uff0c]\s*", ", ", m.group(1)) + "]", text
    )


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
