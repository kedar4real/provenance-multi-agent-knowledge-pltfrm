import pytest

from eval.cost_ab import compare, report


def row(case: str, cost: float, correct: str = "yes", hit: bool = False) -> dict[str, object]:
    return {
        "case": case, "correct": correct, "faithfulness": 1.0, "declined": False,
        "usage": {"input_tokens": int(cost * 1e6), "output_tokens": 0, "cost_usd": cost},
        "llm_ms": 1000.0, "control": {"cache": {"hit": hit}},
    }  # fmt: skip


def test_arms_are_compared_on_shared_cases_and_paraphrase_costs_are_disclosed() -> None:
    agent = [row("a", 0.010), row("b", 0.010), row("only-agent", 0.5)]
    controlled = [row("a", 0.002), row("b", 0.006, "partial"), row("a-para", 0.0, hit=True)]

    result = compare(agent, controlled)

    assert result["shared_cases"] == 2
    assert result["cost_ratio"] == pytest.approx(0.4)
    assert result["controller"]["correct"] == 0.5
    p = result["paraphrases"]
    assert p["n"] == 1 and p["cache_hits"] == 1 and p["share_of_query_set"] == pytest.approx(1 / 3)
    assert result["cost_ratio_with_paraphrases"] == pytest.approx(0.008 / 0.030)
    assert "Cost ratio (controller / agent): 0.40" in report(result)
