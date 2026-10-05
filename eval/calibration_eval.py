"""Calibrate claim confidence on judged claims, compare methods honestly, save the winner.

uv run python -m eval.calibration_eval                 # all judged claims in eval/reports
uv run python -m eval.calibration_eval --audit-sheet   # also write the 100-claim human audit

Claims and labels come from the answer evals (the judge marked each claim supported or not
by the evidence the answer saw), pooled across the baseline and the agent. Every method is
scored out-of-fold (5 folds), so no claim is scored by a model that was fit on it. The
method with the lowest out-of-fold Brier score (a proper scoring rule; picking by ECE alone
can reward a model that hedges everything) is refit on all claims and saved for serving.
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

from provenance.verifier.calibration import (
    Method,
    auroc,
    bootstrap_ece,
    brier,
    columns_for,
    ece,
    fit,
    out_of_fold,
    reliability_bins,
    reliability_svg,
)  # fmt: skip
from provenance.verifier.nli import NliModel
from provenance.verifier.signals import FEATURES, claim_signals

REPORTS = Path("eval/reports")
CALIBRATOR = Path("config/calibration.json")
AUDIT_SHEET = Path("eval/golden/claim_audit.md")
METHODS: tuple[Method, ...] = ("raw_nli", "platt_nli", "isotonic_nli", "ensemble")
AUDIT_SIZE = 100


def latest_rows() -> list[dict[str, Any]]:
    """The most recent full answer-eval report per system that stored claim labels."""
    rows: list[dict[str, Any]] = []
    for system in ("baseline", "agent"):
        reports = sorted(glob.glob(str(REPORTS / f"answers-{system}-*.json")))
        for path in reversed(reports):
            data = json.loads(Path(path).read_text("utf-8"))
            if data and "claim_labels" in data[0]:
                rows += [{**r, "system": system} for r in data]
                break
    return rows


def claims_with_signals(rows: list[dict[str, Any]], nli: NliModel) -> list[dict[str, Any]]:
    claims = []
    for row in rows:
        evidence = [e["text"] for e in row.get("evidence", [])]
        for label in row.get("claim_labels", []):
            text = str(label.get("claim", "")).strip()
            if not text or not evidence:
                continue
            signals = claim_signals(text, evidence, nli, row.get("top_rerank"))
            claims.append(
                {
                    "case": row["case"],
                    "system": row["system"],
                    "claim": text,
                    "supported": bool(label.get("supported")),
                    "signals": signals.model_dump(),
                    "answer_correct": row.get("correct") == "yes",
                }
            )
    return claims


def matrix(claims: list[dict[str, Any]], columns: list[str]) -> np.ndarray:
    return np.array([[c["signals"][name] for name in columns] for c in claims], dtype=float)


def evaluate(claims: list[dict[str, Any]]) -> dict[str, Any]:
    y = np.array([1.0 if c["supported"] else 0.0 for c in claims])
    results: dict[str, Any] = {"n_claims": len(claims), "supported_rate": float(y.mean())}
    predictions: dict[str, np.ndarray] = {}
    for method in METHODS:
        p = out_of_fold(method, matrix(claims, columns_for(method)), y)
        predictions[method] = p
        low, high = bootstrap_ece(p, y)
        results[method] = {
            "ece": ece(p, y), "ece_ci95": [low, high], "brier": brier(p, y), "auroc": auroc(p, y),
        }  # fmt: skip
    # Ablation: what each signal adds to the ensemble (drop it, refit out-of-fold).
    ablation = {}
    for drop in FEATURES:
        kept = [f for f in FEATURES if f != drop]
        p = out_of_fold("ensemble", matrix(claims, kept), y)
        ablation[drop] = {"ece": ece(p, y), "brier": brier(p, y), "auroc": auroc(p, y)}
    results["ablation_without"] = ablation
    results["chosen"] = min(METHODS, key=lambda m: results[m]["brier"])
    # Answer confidence = its weakest claim; does it predict whether the answer was right?
    chosen = predictions[results["chosen"]]
    by_case: dict[tuple[str, str], list[int]] = {}
    for i, c in enumerate(claims):
        by_case.setdefault((c["system"], c["case"]), []).append(i)
    answer_conf = np.array([chosen[idx].min() for idx in by_case.values()])
    answer_ok = np.array(
        [1.0 if claims[idx[0]]["answer_correct"] else 0.0 for idx in by_case.values()]
    )
    results["answer_level"] = {
        "n": len(answer_ok),
        "auroc_min_claim_vs_correct": auroc(answer_conf, answer_ok),
    }
    results["reliability"] = {m: reliability_bins(predictions[m], y) for m in METHODS}
    return results


def report(results: dict[str, Any]) -> str:
    lines = [
        f"# Claim calibration ({datetime.now(UTC):%Y-%m-%d %H:%M} UTC)",
        "",
        f"{results['n_claims']} judged claims; {results['supported_rate']:.0%} supported. "
        "All scores out-of-fold (5 folds); 95% bootstrap CI for ECE.",
        "",
        "| method | ECE | ECE 95% CI | Brier | AUROC |",
        "|---|---|---|---|---|",
    ]
    for m in METHODS:
        r = results[m]
        lines.append(
            f"| {m}{' (chosen)' if m == results['chosen'] else ''} | {r['ece']:.3f} | "
            f"{r['ece_ci95'][0]:.3f}-{r['ece_ci95'][1]:.3f} | {r['brier']:.3f} | {r['auroc']:.3f} |"
        )
    lines += [
        "",
        "Ablation: the ensemble without one signal.",
        "",
        "| without | ECE | Brier | AUROC |",
        "|---|---|---|---|",
    ]
    for name, r in results["ablation_without"].items():
        lines.append(f"| {name} | {r['ece']:.3f} | {r['brier']:.3f} | {r['auroc']:.3f} |")
    a = results["answer_level"]
    lines += [
        "",
        f"Answer confidence (weakest claim) vs answer correctness: AUROC "
        f"{a['auroc_min_claim_vs_correct']:.3f} over {a['n']} answers.",
        "",
        "Logprob signal: not available (no free provider tested returns token logprobs).",
        "",
        "![reliability](calibration-reliability.svg)",
    ]
    return "\n".join(lines) + "\n"


def write_audit_sheet(claims: list[dict[str, Any]], rows: list[dict[str, Any]]) -> None:
    evidence_by_case = {(r["system"], r["case"]): r.get("evidence", []) for r in rows}
    sample = random.Random(11).sample(claims, min(AUDIT_SIZE, len(claims)))
    lines = [
        "# Claim audit (human check of the LLM judge's labels)",
        "",
        "For each claim: is it supported by the evidence? Mark `verdict: [y]` (supported) or",
        "`verdict: [n]` (not supported). Then run `uv run python -m eval.calibration_eval --apply-audit`.",
        "",
    ]
    for i, c in enumerate(sample):
        evidence = evidence_by_case.get((c["system"], c["case"]), [])
        joined = "\n\n".join(f"> [{e['id']}] {' '.join(e['text'].split())[:700]}" for e in evidence)
        lines += [
            f"## claim-{i:03d}  ({c['system']} {c['case']})",
            "",
            f"**Claim:** {c['claim']}",
            "",
            joined,
            "",
            f"judge: {'supported' if c['supported'] else 'not supported'}",
            "",
            "verdict: [ ]",
            "",
        ]
    AUDIT_SHEET.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {AUDIT_SHEET} ({len(sample)} claims)")


def apply_audit() -> None:
    import re

    text = AUDIT_SHEET.read_text("utf-8")
    pairs = re.findall(r"judge: (supported|not supported)\s+verdict: \[(\w?)\]", text)
    marked = [(j, v.lower()) for j, v in pairs if v]
    if len(marked) < len(pairs):
        sys.exit(f"{len(pairs) - len(marked)} claims still unmarked")
    agree = sum((j == "supported") == (v == "y") for j, v in marked)
    print(f"human-judge agreement on claims: {agree}/{len(marked)} = {agree / len(marked):.0%}")


def main(audit_sheet: bool) -> None:
    rows = latest_rows()
    if not rows:
        sys.exit("no answer-eval reports with claim labels yet; run eval.answer_eval first")
    print(f"{len(rows)} judged answers; computing signals...", flush=True)
    claims = claims_with_signals(rows, NliModel())
    results = evaluate(claims)
    REPORTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M")
    curves = {m: [tuple(b) for b in results["reliability"][m]] for m in METHODS}
    (REPORTS / "calibration-reliability.svg").write_text(reliability_svg(curves), "utf-8")  # type: ignore[arg-type]
    (REPORTS / f"calibration-{stamp}.json").write_text(
        json.dumps({**results, "claims": claims}, indent=2), "utf-8"
    )
    text = report(results)
    (REPORTS / f"calibration-{stamp}.md").write_text(text, "utf-8")
    chosen: Method = results["chosen"]
    y = np.array([1.0 if c["supported"] else 0.0 for c in claims])
    fit(chosen, matrix(claims, columns_for(chosen)), y).save(CALIBRATOR)
    print(text)
    print(f"saved {chosen} calibrator to {CALIBRATOR}")
    if audit_sheet:
        write_audit_sheet(claims, rows)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-sheet", action="store_true")
    parser.add_argument("--apply-audit", action="store_true")
    args = parser.parse_args()
    if args.apply_audit:
        apply_audit()
    else:
        main(args.audit_sheet)
