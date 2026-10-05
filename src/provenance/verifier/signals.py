"""Per-claim confidence signals. Each is cheap and local; calibration learns how to combine
them into a probability that means what it says."""

import re
from typing import Protocol

from pydantic import BaseModel

from provenance.verifier.numbers import is_small_count, number_derived, number_supported, numbers_in

_WORD = re.compile(r"[a-z0-9][a-z0-9'.-]*")
_STOPWORDS = frozenset(
    [
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "has",
        "have",
        "in",
        "is",
        "it",
        "its",
        "of",
        "on",
        "or",
        "that",
        "the",
        "their",
        "this",
        "to",
        "was",
        "were",
        "with",
        "which",
        "while",
        "also",
        "than",
        "over",
        "into",
    ]
)

FEATURES = ("nli_entail", "nli_contra", "numbers_ok", "has_numbers", "overlap", "top_rerank")


class Entailment(Protocol):
    def scores(self, evidence: list[str], claim: str) -> tuple[float, float]: ...


class ClaimSignals(BaseModel):
    nli_entail: float
    nli_contra: float
    numbers_ok: float  # share of the claim's numbers found in (or derived from) the evidence
    has_numbers: float
    overlap: float  # share of the claim's content words present in the evidence
    top_rerank: float

    def vector(self) -> list[float]:
        return [getattr(self, name) for name in FEATURES]


def claim_signals(
    claim: str, evidence: list[str], nli: Entailment, top_rerank: float | None
) -> ClaimSignals:
    entail, contra = nli.scores(evidence, claim)
    evidence_values = [v for text in evidence for _, v in numbers_in(text)]
    claim_numbers = [v for written, v in numbers_in(claim) if not is_small_count(written)]
    checked = [
        number_supported(v, evidence_values) or number_derived(v, evidence_values)
        for v in claim_numbers
    ]
    return ClaimSignals(
        nli_entail=entail,
        nli_contra=contra,
        numbers_ok=sum(checked) / len(checked) if checked else 1.0,
        has_numbers=1.0 if checked else 0.0,
        overlap=_overlap(claim, evidence),
        top_rerank=top_rerank if top_rerank is not None else 0.0,
    )


def _content_words(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in _STOPWORDS and len(w) > 2}


def _overlap(claim: str, evidence: list[str]) -> float:
    words = _content_words(claim)
    if not words:
        return 0.0
    present = _content_words(" ".join(evidence))
    return len(words & present) / len(words)
