"""Selective answering: if the system only answers when confident, how accurate is it?

uv run python -m eval.selective_eval [--system agent|baseline]

For each answered (not declined) case in the latest answer-eval report, the answer's
confidence is computed the way the API does it: split into claims, signals per claim
against the answer's evidence, the calibrator's probability per claim, the minimum over
claims. The calibrator is fit out-of-fold **by question**, on the judge-labeled claims of
the other questions, so no answer is scored by a calibrator that saw it.

Reported per confidence source (raw NLI entailment, and each calibration method):
- the risk-coverage curve (answer the most confident X%; error rate among those),
  AURC (area under it; lower is better) and selective accuracy at 80% / 90% coverage;
- at the configured abstention threshold: coverage, the accuracy of what's kept, and the
  accuracy the confidences *predicted* for it. Ranking metrics barely change under a
  monotone calibration; what calibration buys is that this predicted number is true, so a
  threshold means what it says.
"""

import argparse
import glob
import json
import random
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from provenance.controller.policy import Policy
from provenance.verifier.calibration import Method, columns_for, fit
from provenance.verifier.claims import split_claims
from provenance.verifier.signals import Entailment, claim_signals

REPORTS = Path("eval/reports")
FOLDS = 5
SOURCES: tuple[Method, ...] = ("raw_nli", "platt_nli", "isotonic_nli", "ensemble")


def latest_rows(system: str) -> list[dict[str, Any]]:
    for path in sorted(glob.glob(str(REPORTS / f"answers-{system}-*.json")), reverse=True):
        data = json.loads(Path(path).read_text("utf-8"))
        if data and "claim_labels" in data[0]:
            return list(data)
    raise SystemExit(f"no answer-eval report with claim labels for '{system}' yet")


def features(signals: dict[str, float], method: Method) -> list[float]:
    return [float(signals[name]) for name in columns_for(method)]


def prepare(rows: list[dict[str, Any]], nli: Entailment) -> list[dict[str, Any]]:
    """Per row: judge-labeled claims (to fit on) and serving-style claims (to score)."""
    prepared = []
    for row in rows:
        evidence = [e["text"] for e in row.get("evidence", [])]
        if not evidence:
            continue
        top = row.get("top_rerank")
        labeled = [
            (claim_signals(str(c["claim"]), evidence, nli, top).model_dump(), bool(c["supported"]))
            for c in row.get("claim_labels", []) if str(c.get("claim", "")).strip()
        ]  # fmt: skip
        serving = []
        if not row["declined"]:
            serving = [
                claim_signals(c.text, evidence, nli, top).model_dump()
                for c in split_claims(row["answer"])
            ]
        prepared.append({
            "case": row["case"], "declined": row["declined"], "correct": row["correct"],
            "labeled": labeled, "serving": serving,
        })  # fmt: skip
    return prepared


def answer_confidences(prepared: list[dict[str, Any]], method: Method) -> dict[str, float]:
    """Out-of-fold by question: answer -> min calibrated claim probability."""
    cases = sorted(p["case"] for p in prepared)
    random.Random(0).shuffle(cases)
    fold = {case: i % FOLDS for i, case in enumerate(cases)}
    scores: dict[str, float] = {}
    for k in range(FOLDS):
        train = [(s, y) for p in prepared if fold[p["case"]] != k for s, y in p["labeled"]]
        if not train or len({y for _, y in train}) < 2:
            continue
        x = np.array([features(s, method) for s, _ in train])
        y = np.array([1.0 if label else 0.0 for _, label in train])
        params = fit(method, x, y)
        for p in prepared:
            if fold[p["case"]] == k and p["serving"] and not p["declined"]:
                probs = params.predict(np.array([features(s, method) for s in p["serving"]]))
                scores[p["case"]] = float(np.min(probs))
    return scores


def risk_coverage(conf: np.ndarray, ok: np.ndarray) -> dict[str, Any]:
    """Answer the most confident first; risk = error rate among the answered."""
    order = np.argsort(-conf, kind="stable")
    hits = np.cumsum(ok[order])
    n = len(ok)
    kept = np.arange(1, n + 1)
    risk = 1 - hits / kept
    oracle = 1 - np.cumsum(np.sort(ok)[::-1]) / kept

    def selective_accuracy(coverage: float) -> float:
        m = max(1, int(np.ceil(coverage * n)))
        return float(hits[m - 1] / m)

    return {
        "n": n,
        "accuracy": float(ok.mean()),
        "aurc": float(risk.mean()),
        "aurc_oracle": float(oracle.mean()),
        "selective_accuracy_80": selective_accuracy(0.8),
        "selective_accuracy_90": selective_accuracy(0.9),
        "curve": [(float(c), float(r)) for c, r in zip(kept / n, risk, strict=True)],
    }


def at_threshold(conf: np.ndarray, ok: np.ndarray, threshold: float) -> dict[str, Any]:
    kept = conf >= threshold
    return {
        "threshold": threshold,
        "coverage": float(kept.mean()),
        "kept_accuracy": float(ok[kept].mean()) if kept.any() else None,
        "predicted_accuracy": float(conf[kept].mean()) if kept.any() else None,
    }


def evaluate(prepared: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    answered = [p for p in prepared if not p["declined"] and p["serving"]]
    results: dict[str, Any] = {"answered": len(answered), "declined": len(prepared) - len(answered)}
    for method in SOURCES:
        scores = answer_confidences(prepared, method)
        scored = [p for p in answered if p["case"] in scores]
        conf = np.array([scores[p["case"]] for p in scored])
        ok = np.array([1.0 if p["correct"] == "yes" else 0.0 for p in scored])
        if len(ok) == 0:
            continue
        results[method] = {
            **risk_coverage(conf, ok), "at_abstain_threshold": at_threshold(conf, ok, threshold),
        }  # fmt: skip
    return results


def curve_svg(curves: dict[str, list[tuple[float, float]]], size: int = 360) -> str:
    pad, inner = 40, size - 60
    colors = ["#2563eb", "#16a34a", "#d97706", "#dc2626", "#7c3aed"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'font-family="sans-serif" font-size="11">',
        f'<rect x="{pad}" y="20" width="{inner}" height="{inner}" fill="none" stroke="#999"/>',
        f'<text x="{pad + inner / 2}" y="{size - 8}" text-anchor="middle">coverage</text>',
        f'<text x="12" y="{20 + inner / 2}" transform="rotate(-90 12 {20 + inner / 2})" '
        f'text-anchor="middle">error rate among answered</text>',
    ]
    for i, (name, points) in enumerate(curves.items()):
        path = " ".join(f"{pad + c * inner:.1f},{20 + inner - r * inner:.1f}" for c, r in points)
        color = colors[i % len(colors)]
        parts.append(f'<polyline points="{path}" fill="none" stroke="{color}" stroke-width="1.5"/>')
        parts.append(f'<text x="{pad + 6}" y="{34 + 14 * i}" fill="{color}">{name}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def report(results: dict[str, Any], system: str) -> str:
    lines = [
        f"# Selective answering: {system} ({datetime.now(UTC):%Y-%m-%d %H:%M} UTC)",
        "",
        f"{results['answered']} answered cases ({results['declined']} declined, excluded). "
        "Correct = the judge graded the answer fully correct against the reference.",
        "Confidence = the weakest claim's probability, calibrator fit out-of-fold by question.",
        "",
        "| confidence | AURC (lower better) | oracle AURC | acc @80% cov | acc @90% cov "
        "| acc @100% |",
        "|---|---|---|---|---|---|",
    ]
    for method in SOURCES:
        r = results.get(method)
        if r:
            lines.append(
                f"| {method} | {r['aurc']:.3f} | {r['aurc_oracle']:.3f} "
                f"| {r['selective_accuracy_80']:.2f} | {r['selective_accuracy_90']:.2f} "
                f"| {r['accuracy']:.2f} |"
            )
    lines += [
        "",
        "At the configured abstention threshold (config/routing.yaml):",
        "",
        "| confidence | threshold | coverage | accuracy of kept | predicted accuracy of kept |",
        "|---|---|---|---|---|",
    ]
    for method in SOURCES:
        r = results.get(method)
        if r:
            t = r["at_abstain_threshold"]
            kept = "-" if t["kept_accuracy"] is None else f"{t['kept_accuracy']:.2f}"
            pred = "-" if t["predicted_accuracy"] is None else f"{t['predicted_accuracy']:.2f}"
            lines.append(f"| {method} | {t['threshold']} | {t['coverage']:.2f} | {kept} | {pred} |")
    return "\n".join(lines) + "\n"


def main(system: str) -> None:
    from provenance.verifier.nli import NliModel

    threshold = Policy.load(Path("config/routing.yaml")).abstain.below_confidence
    prepared = prepare(latest_rows(system), NliModel())
    results = evaluate(prepared, threshold)
    REPORTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M")
    base = REPORTS / f"selective-{system}-{stamp}"
    curves: dict[str, list[tuple[float, float]]] = {
        m: results[m]["curve"] for m in SOURCES if m in results
    }
    Path(f"{base}.svg").write_text(curve_svg(curves), "utf-8")
    Path(f"{base}.json").write_text(json.dumps(results, indent=2), "utf-8")
    text = report(results, system)
    Path(f"{base}.md").write_text(text + f"\n![risk-coverage]({base.name}.svg)\n", "utf-8")
    print(text)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    parser = argparse.ArgumentParser()
    parser.add_argument("--system", choices=["agent", "baseline"], default="agent")
    main(parser.parse_args().system)
