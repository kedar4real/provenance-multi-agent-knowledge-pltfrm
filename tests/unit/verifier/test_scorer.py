import numpy as np

from provenance.verifier.calibration import CalibratorParams
from provenance.verifier.scorer import ClaimScorer


class KeywordNli:
    """Entails a claim only if it mentions 'rose'."""

    def scores(self, evidence: list[str], claim: str) -> tuple[float, float]:
        return (0.95, 0.0) if "rose" in claim else (0.1, 0.6)


ANSWER = "Net interest income rose 3% in 2025 [P1]. Card balances fell sharply this year [P1]."
EVIDENCE = ["Net interest income rose 3% in 2025."]
RAW = CalibratorParams(method="raw_nli", features=["nli_entail"])


def test_without_a_calibrator_claims_have_no_confidence() -> None:
    claims, confidence = ClaimScorer(KeywordNli(), None).score(ANSWER, EVIDENCE, 0.9)

    assert [c.confidence for c in claims] == [None, None]
    assert confidence is None
    assert claims[0].signals.nli_entail == 0.95  # signals are still computed


def test_answer_confidence_is_the_weakest_claim() -> None:
    claims, confidence = ClaimScorer(KeywordNli(), RAW).score(ANSWER, EVIDENCE, 0.9)

    assert [round(c.confidence or 0, 2) for c in claims] == [0.95, 0.1]
    assert confidence == min(c.confidence for c in claims if c.confidence is not None)


def test_the_calibrator_sees_features_in_the_order_it_was_fit_with() -> None:
    ensemble = CalibratorParams(
        method="ensemble", features=["overlap", "nli_entail"], mean=[0.0, 0.0],
        scale=[1.0, 1.0], coef=[0.0, 10.0], intercept=-5.0,
    )  # fmt: skip

    claims, _ = ClaimScorer(KeywordNli(), ensemble).score(ANSWER, EVIDENCE, 0.9)

    # Weight is on nli_entail only: 0.95 -> sigmoid(4.5), 0.1 -> sigmoid(-4).
    np.testing.assert_allclose(
        [c.confidence or 0.0 for c in claims], [1 / (1 + np.exp(-4.5)), 1 / (1 + np.exp(4.0))]
    )
