import math

import pytest

from eval.retrieval_metrics import bootstrap_ci, ndcg_at, recall_at, reciprocal_rank

GOLD = {"g1", "g2"}  # one passage and its near-duplicate from the next year


def test_recall_counts_any_gold_within_k() -> None:
    retrieved = ["x", "y", "g2", "z"]

    assert recall_at(retrieved, GOLD, 2) == 0.0
    assert recall_at(retrieved, GOLD, 3) == 1.0


def test_reciprocal_rank_uses_the_first_gold_hit() -> None:
    assert reciprocal_rank(["x", "g1", "g2"], GOLD) == 0.5
    assert reciprocal_rank(["x", "y"], GOLD) == 0.0


def test_reciprocal_rank_ignores_hits_beyond_k() -> None:
    retrieved = [f"x{i}" for i in range(10)] + ["g1"]

    assert reciprocal_rank(retrieved, GOLD, k=10) == 0.0


def test_ndcg_rewards_rank_and_ignores_duplicate_evidence() -> None:
    assert ndcg_at(["g1"], GOLD) == 1.0
    assert ndcg_at(["x", "g1"], GOLD) == pytest.approx(1 / math.log2(3))
    # A second copy of the same evidence adds nothing.
    assert ndcg_at(["g1", "g2"], GOLD) == 1.0


def test_bootstrap_interval_brackets_the_mean() -> None:
    values = [1.0] * 70 + [0.0] * 30

    low, high = bootstrap_ci(values)

    assert low < 0.7 < high
    assert low > 0.55 and high < 0.85


def test_bootstrap_of_nothing_is_zero() -> None:
    assert bootstrap_ci([]) == (0.0, 0.0)
