"""Deterministic answer checks: citations point at real evidence, and every number the answer
states appears in the evidence it cites. Catches invented figures without an LLM call.
Calibrated, claim-level confidence is M6; this is the floor under it.
"""

from provenance.agents.types import Evidence, Verification
from provenance.verifier.numbers import (
    CITATION,
    DECLINE,
    is_small_count,
    number_derived,
    number_supported,
    numbers_in,
)

__all__ = ["CITATION", "DECLINE", "numbers_in", "verify"]


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
