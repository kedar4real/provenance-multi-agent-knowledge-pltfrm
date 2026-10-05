import random

from eval.calibration_eval import METHODS, evaluate, report
from provenance.verifier.signals import FEATURES


def synthetic_claims(n: int = 240) -> list[dict[str, object]]:
    rng = random.Random(3)
    claims = []
    for i in range(n):
        supported = rng.random() < 0.7
        nli = min(1.0, max(0.0, (0.85 if supported else 0.35) + rng.gauss(0, 0.2)))
        signals = {f: rng.random() for f in FEATURES} | {"nli_entail": nli}
        claims.append({
            "case": f"c{i // 3}", "system": "agent", "claim": "x", "supported": supported,
            "signals": signals, "answer_correct": supported,
        })  # fmt: skip
    return claims


def test_evaluate_compares_every_method_and_picks_by_brier() -> None:
    results = evaluate(synthetic_claims())

    assert set(METHODS) <= set(results)
    assert results["chosen"] == min(METHODS, key=lambda m: results[m]["brier"])
    assert set(results["ablation_without"]) == set(FEATURES)
    assert results["answer_level"]["n"] == 80
    for m in METHODS:
        low, high = results[m]["ece_ci95"]
        assert low <= results[m]["ece"] <= high + 1e-9


def test_report_marks_the_chosen_method() -> None:
    results = evaluate(synthetic_claims())

    text = report(results)

    assert f"| {results['chosen']} (chosen) |" in text
    assert "Logprob signal: not available" in text
