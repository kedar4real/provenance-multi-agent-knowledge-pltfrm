"""Score each claim of an answer with the fitted calibrator; the answer's confidence is its
weakest claim's.

Signals are computed against all the evidence the answer saw, exactly as during
calibration (the judge's claims carry no citation map); scoring differently from how the
calibrator was fit would make its probabilities meaningless. Without a fitted calibrator
there is no confidence at all: an uncalibrated score shown as a probability would be the
very thing this module exists to prevent.
"""

import numpy as np
from pydantic import BaseModel

from provenance.verifier.calibration import CalibratorParams
from provenance.verifier.claims import split_claims
from provenance.verifier.signals import ClaimSignals, Entailment, claim_signals


class ScoredClaim(BaseModel):
    text: str
    cited: list[str]
    confidence: float | None
    signals: ClaimSignals


class ClaimScorer:
    def __init__(self, nli: Entailment, calibrator: CalibratorParams | None) -> None:
        self._nli = nli
        self._calibrator = calibrator

    @property
    def calibrated(self) -> bool:
        return self._calibrator is not None

    def score(
        self, answer: str, evidence: list[str], top_rerank: float | None
    ) -> tuple[list[ScoredClaim], float | None]:
        scored = []
        for claim in split_claims(answer):
            signals = claim_signals(claim.text, evidence, self._nli, top_rerank)
            confidence = None
            if self._calibrator is not None:
                row = [getattr(signals, f) for f in self._calibrator.features]
                confidence = float(self._calibrator.predict(np.array([row]))[0])
            scored.append(
                ScoredClaim(
                    text=claim.text, cited=claim.cited, confidence=confidence, signals=signals
                )
            )
        confidences = [c.confidence for c in scored if c.confidence is not None]
        return scored, (min(confidences) if confidences else None)
