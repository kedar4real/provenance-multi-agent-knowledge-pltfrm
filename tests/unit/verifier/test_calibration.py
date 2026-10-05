from pathlib import Path

import numpy as np
import pytest

from provenance.verifier import calibration
from provenance.verifier.calibration import (
    auroc,
    brier,
    ece,
    fit,
    out_of_fold,
    reliability_bins,
    reliability_svg,
)  # fmt: skip


def synthetic(n: int = 400, seed: int = 1) -> tuple[np.ndarray, np.ndarray]:
    """Supported claims tend to have high entailment; the raw score is overconfident."""
    rng = np.random.default_rng(seed)
    y = rng.integers(0, 2, n)
    nli = np.clip(0.55 + 0.4 * y + rng.normal(0, 0.15, n), 0, 1)
    others = rng.random((n, 5))
    return np.column_stack([nli, others]), y.astype(float)


def test_ece_is_zero_for_perfect_calibration_and_exact_for_overconfidence() -> None:
    p = np.array([0.0, 0.0, 1.0, 1.0])
    assert ece(p, np.array([0.0, 0.0, 1.0, 1.0])) == 0.0
    # Always 0.9 confident, right half the time: the gap is 0.4.
    assert ece(np.full(10, 0.9), np.array([1, 0] * 5, dtype=float)) == pytest.approx(0.4)


def test_brier_and_auroc() -> None:
    p, y = np.array([0.9, 0.8, 0.2, 0.1]), np.array([1.0, 1.0, 0.0, 0.0])
    assert auroc(p, y) == 1.0
    assert brier(p, y) == pytest.approx(0.025)


def test_calibrating_the_overconfident_raw_score_lowers_ece() -> None:
    x, y = synthetic()
    raw = out_of_fold("raw_nli", x[:, :1], y)
    platt = out_of_fold("platt_nli", x[:, :1], y)
    assert ece(platt, y) < ece(raw, y)


def test_out_of_fold_never_scores_a_claim_with_a_model_that_saw_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    x, y = synthetic(50)
    seen: list[set[int]] = []
    real_fit = calibration.fit

    def spy(
        method: calibration.Method, xs: np.ndarray, ys: np.ndarray
    ) -> calibration.CalibratorParams:
        seen.append({int(v) for v in xs[:, 1] * 1e6})  # rows identified by a random column
        return real_fit(method, xs, ys)

    monkeypatch.setattr(calibration, "fit", spy)
    x[:, 1] = np.arange(50) / 1e6
    out_of_fold("platt_nli", x, y, folds=5)

    for k, trained_on in enumerate(seen):
        tested = set(range(50)) - trained_on
        assert tested and not (tested & trained_on), k


def test_isotonic_and_ensemble_round_trip_through_json(tmp_path: Path) -> None:
    x, y = synthetic()
    for method, cols in (("isotonic_nli", x[:, :1]), ("ensemble", x)):
        params = fit(method, cols, y)  # type: ignore[arg-type]
        path = tmp_path / f"{method}.json"
        params.save(path)
        loaded = calibration.CalibratorParams.load(path)
        np.testing.assert_allclose(loaded.predict(cols[:20]), params.predict(cols[:20]))
        assert ((loaded.predict(cols) >= 0) & (loaded.predict(cols) <= 1)).all()


def test_reliability_diagram_has_a_curve_per_method() -> None:
    x, y = synthetic()
    bins = reliability_bins(x[:, 0], y)
    svg = reliability_svg({"raw": bins, "platt": bins})

    assert sum(n for _, _, n in bins) == len(y)
    assert svg.startswith("<svg") and svg.count("<path") == 2
