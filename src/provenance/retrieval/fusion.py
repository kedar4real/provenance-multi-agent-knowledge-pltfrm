"""Reciprocal Rank Fusion: combine rankings using positions only, so retrievers whose scores
live on different scales (cosine distance, BM25) can be merged without calibration."""

RRF_K = 60


def reciprocal_rank_fusion(rankings: list[list[int]], k: int = RRF_K) -> list[tuple[int, float]]:
    """`rankings` are lists of IDs, best first. Each appearance adds 1 / (k + rank), rank
    starting at 1; returns (id, score) best first, ties broken by ID for determinism."""
    scores: dict[int, float] = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] = scores.get(item, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))
