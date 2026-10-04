import pytest

from provenance.retrieval.fusion import reciprocal_rank_fusion


def test_items_ranked_well_by_both_retrievers_win() -> None:
    fused = reciprocal_rank_fusion([[1, 2, 3], [2, 1, 4]], k=60)

    assert [cid for cid, _ in fused][:2] == [1, 2]
    assert fused[0][1] == pytest.approx(1 / 61 + 1 / 62)


def test_one_strong_agreement_beats_a_single_first_place() -> None:
    # 7 is second in both lists; 1 and 9 are each first in only one.
    fused = reciprocal_rank_fusion([[1, 7], [9, 7]], k=60)

    assert fused[0][0] == 7


def test_only_positions_matter_not_raw_scores() -> None:
    assert reciprocal_rank_fusion([[5, 6]]) == reciprocal_rank_fusion([[5, 6]])
    assert [cid for cid, _ in reciprocal_rank_fusion([[5, 6]])] == [5, 6]


def test_ties_break_by_id_for_deterministic_output() -> None:
    fused = reciprocal_rank_fusion([[3], [2]])

    assert [cid for cid, _ in fused] == [2, 3]


def test_no_rankings_means_no_results() -> None:
    assert reciprocal_rank_fusion([]) == []
