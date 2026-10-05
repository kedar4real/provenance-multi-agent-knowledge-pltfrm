"""Turn claim signals into probabilities that mean what they say, and measure how well.

"Calibrated" means: of all claims given 0.8, about 80% are actually supported. A model can
rank claims well (high AUROC) and still be badly calibrated; abstention thresholds only
make sense on calibrated scores.
"""

import json
import random
from itertools import pairwise
from pathlib import Path
from typing import Literal

import numpy as np
from pydantic import BaseModel
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression

from provenance.verifier.signals import FEATURES

Method = Literal["raw_nli", "platt_nli", "isotonic_nli", "ensemble"]
ECE_BINS = 10


class CalibratorParams(BaseModel):
    """Everything needed to score a claim at serving time, stored as JSON (no pickles)."""

    method: Method
    features: list[str]
    mean: list[float] = []
    scale: list[float] = []
    coef: list[float] = []
    intercept: float = 0.0
    iso_x: list[float] = []
    iso_y: list[float] = []

    def predict(self, x: np.ndarray) -> np.ndarray:
        x = np.atleast_2d(x)
        if self.method == "raw_nli":
            out: np.ndarray = x[:, 0].astype(float)
            return out
        if self.method == "isotonic_nli":
            iso: np.ndarray = np.asarray(np.interp(x[:, 0], self.iso_x, self.iso_y))
            return iso
        z = (x - np.array(self.mean)) / np.array(self.scale)
        logits = z @ np.array(self.coef) + self.intercept
        probs: np.ndarray = np.asarray(1.0 / (1.0 + np.exp(-logits)))
        return probs

    def save(self, path: Path) -> None:
        path.write_text(self.model_dump_json(indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "CalibratorParams":
        return cls.model_validate(json.loads(path.read_text(encoding="utf-8")))


def columns_for(method: Method) -> list[str]:
    return list(FEATURES) if method == "ensemble" else ["nli_entail"]


def fit(method: Method, x: np.ndarray, y: np.ndarray) -> CalibratorParams:
    """`x` has the columns from `columns_for(method)`; `y` is 1 for supported claims."""
    features = columns_for(method)
    if method == "raw_nli":
        return CalibratorParams(method=method, features=features)
    if method == "isotonic_nli":
        iso = IsotonicRegression(y_min=0.0, y_max=1.0, out_of_bounds="clip").fit(x[:, 0], y)
        return CalibratorParams(
            method=method,
            features=features,
            iso_x=[float(v) for v in iso.X_thresholds_],
            iso_y=[float(v) for v in iso.y_thresholds_],
        )
    mean = x.mean(axis=0)
    scale = np.where(x.std(axis=0) == 0, 1.0, x.std(axis=0))
    model = LogisticRegression(C=1.0, max_iter=1000).fit((x - mean) / scale, y)
    return CalibratorParams(
        method=method,
        features=features,
        mean=[float(v) for v in mean],
        scale=[float(v) for v in scale],
        coef=[float(v) for v in model.coef_[0]],
        intercept=float(model.intercept_[0]),
    )


def out_of_fold(
    method: Method, x: np.ndarray, y: np.ndarray, folds: int = 5, seed: int = 0
) -> np.ndarray:
    """Predictions for every claim from a model that never saw it: the only honest way to
    measure calibration when the same small dataset both fits and evaluates."""
    order = list(range(len(y)))
    random.Random(seed).shuffle(order)
    predictions = np.zeros(len(y))
    for k in range(folds):
        test = order[k::folds]
        train = [i for i in order if i not in set(test)]
        params = fit(method, x[train], y[train])
        predictions[test] = params.predict(x[test])
    return predictions


def ece(p: np.ndarray, y: np.ndarray, bins: int = ECE_BINS) -> float:
    """Expected calibration error: the sample-weighted gap between confidence and accuracy
    across equal-width confidence bins."""
    return float(sum(n / len(y) * abs(conf - acc) for conf, acc, n in reliability_bins(p, y, bins)))


def bootstrap_ece(
    p: np.ndarray, y: np.ndarray, samples: int = 2000, seed: int = 0
) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    values = sorted(
        ece(p[idx], y[idx]) for idx in (rng.integers(0, len(y), len(y)) for _ in range(samples))
    )
    return values[int(0.025 * samples)], values[int(0.975 * samples) - 1]


def brier(p: np.ndarray, y: np.ndarray) -> float:
    return float(np.mean((p - y) ** 2))


def auroc(p: np.ndarray, y: np.ndarray) -> float:
    """Probability a random supported claim outranks a random unsupported one (ties = 0.5)."""
    pos, neg = p[y == 1], p[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    wins = (pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()
    return float(wins / (len(pos) * len(neg)))


def reliability_bins(
    p: np.ndarray, y: np.ndarray, bins: int = ECE_BINS
) -> list[tuple[float, float, int]]:
    """(mean confidence, accuracy, count) per non-empty bin; the last bin includes 1.0."""
    out = []
    for lo, hi in pairwise(np.linspace(0, 1, bins + 1)):
        mask = (p >= lo) & ((p < hi) if hi < 1 else (p <= hi))
        if mask.any():
            out.append((float(p[mask].mean()), float(y[mask].mean()), int(mask.sum())))
    return out


def reliability_svg(curves: dict[str, list[tuple[float, float, int]]], size: int = 360) -> str:
    """A reliability diagram: confidence (x) vs accuracy (y); the diagonal is perfect."""
    pad, plot = 40, size - 60
    colors = ["#9a6b00", "#3b6ea8", "#6b8f3b", "#8a4b8f"]

    def xy(conf: float, acc: float) -> tuple[float, float]:
        return pad + conf * plot, pad + (1 - acc) * plot

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size + 20 * len(curves)}" '
        'font-family="system-ui, sans-serif" font-size="11">',
        f'<rect x="{pad}" y="{pad}" width="{plot}" height="{plot}" fill="none" stroke="#bbb"/>',
        f'<line x1="{pad}" y1="{pad + plot}" x2="{pad + plot}" y2="{pad}" stroke="#bbb" stroke-dasharray="4 3"/>',
        f'<text x="{pad + plot / 2}" y="{pad + plot + 28}" text-anchor="middle">confidence</text>',
        f'<text x="12" y="{pad + plot / 2}" transform="rotate(-90 12 {pad + plot / 2})" text-anchor="middle">accuracy</text>',
    ]
    for i, (name, points) in enumerate(curves.items()):
        color = colors[i % len(colors)]
        coords = [xy(c, a) for c, a, _ in points]
        if coords:
            path = " ".join(
                f"{'M' if j == 0 else 'L'}{x:.1f},{y:.1f}" for j, (x, y) in enumerate(coords)
            )
            parts.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2"/>')
            parts += [
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{2 + min(n, 80) ** 0.5 / 2:.1f}" fill="{color}"/>'
                for (x, y), (_, _, n) in zip(coords, points, strict=True)
            ]
        ly = size + 4 + 20 * i
        parts.append(f'<rect x="{pad}" y="{ly}" width="12" height="3" fill="{color}"/>')
        parts.append(f'<text x="{pad + 18}" y="{ly + 5}">{name}</text>')
    parts.append("</svg>")
    return "\n".join(parts)
