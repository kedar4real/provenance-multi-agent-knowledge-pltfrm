import numpy as np
import pytest

from eval.selective_eval import answer_confidences, at_threshold, evaluate, prepare, risk_coverage


def test_risk_coverage_answers_the_most_confident_first() -> None:
    conf = np.array([0.9, 0.8, 0.3, 0.2])
    ok = np.array([1.0, 1.0, 0.0, 1.0])

    r = risk_coverage(conf, ok)

    assert [round(risk, 3) for _, risk in r["curve"]] == [0.0, 0.0, 0.333, 0.25]
    assert r["aurc"] == pytest.approx((0 + 0 + 1 / 3 + 0.25) / 4)
    assert r["aurc_oracle"] == pytest.approx((0 + 0 + 0 + 0.25) / 4)
    assert r["selective_accuracy_80"] == 0.75  # ceil(0.8 * 4) = 4 answers kept
    assert r["accuracy"] == 0.75


def test_at_threshold_compares_predicted_and_actual_accuracy_of_what_is_kept() -> None:
    t = at_threshold(np.array([0.9, 0.7, 0.2]), np.array([1.0, 0.0, 0.0]), 0.5)

    assert t["coverage"] == pytest.approx(2 / 3)
    assert t["kept_accuracy"] == 0.5 and t["predicted_accuracy"] == pytest.approx(0.8)


class KeywordNli:
    """Entails claims containing "good", contradicts the rest."""

    def scores(self, evidence: list[str], claim: str) -> tuple[float, float]:
        return (0.95, 0.02) if "good" in claim else (0.05, 0.9)


def row(case: str, answer: str, supported: bool, correct: str) -> dict[str, object]:
    return {
        "case": case, "declined": False, "correct": correct, "answer": answer,
        "evidence": [{"id": "P1", "text": "evidence"}], "top_rerank": 0.5,
        "claim_labels": [{"claim": answer, "supported": supported}],
    }  # fmt: skip


def test_confidences_are_out_of_fold_by_question_and_rank_good_answers_higher() -> None:
    rows = [row(f"g{i}", "Revenue grew on good demand [P1].", True, "yes") for i in range(10)]
    rows += [row(f"b{i}", "Revenue fell on weak demand [P1].", False, "no") for i in range(10)]
    prepared = prepare(rows, KeywordNli())

    scores = answer_confidences(prepared, "platt_nli")
    results = evaluate(prepared, threshold=0.5)

    assert set(scores) == {r["case"] for r in rows}
    assert min(scores[f"g{i}"] for i in range(10)) > max(scores[f"b{i}"] for i in range(10))
    assert results["platt_nli"]["aurc"] == pytest.approx(results["platt_nli"]["aurc_oracle"])
    assert results["platt_nli"]["at_abstain_threshold"]["kept_accuracy"] == 1.0
