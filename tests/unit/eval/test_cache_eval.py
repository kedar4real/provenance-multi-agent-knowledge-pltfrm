from eval.cache_eval import Pair, swap_company, swap_metric, swap_year, sweep


def test_near_misses_change_exactly_one_entity() -> None:
    q = "What was Apple's revenue in fiscal 2024?"

    assert swap_company(q) == "What was Alphabet's revenue in fiscal 2024?"  # same sector
    assert swap_year(q) == "What was Apple's revenue in fiscal 2023?"
    assert swap_metric(q) == "What was Apple's net income in fiscal 2024?"


def test_swaps_skip_questions_without_that_entity() -> None:
    assert swap_year("What risks does Nvidia describe?") is None
    assert swap_company("What risks do chipmakers describe?") is None


def pair(kind: str, original: str, other: str) -> Pair:
    return Pair(id=kind, case="c", kind=kind, original=original, other=other,  # type: ignore[arg-type]
                should_hit=kind == "paraphrase")  # fmt: skip


def test_the_guard_removes_near_miss_hits_that_embeddings_allow() -> None:
    pairs = [
        pair("paraphrase", "Apple revenue in 2024", "Apple's 2024 net sales"),
        pair("year", "Apple revenue in 2024", "Apple revenue in 2023"),
    ]

    result = sweep(pairs, {"paraphrase": 0.96, "year": 0.99})
    at_95 = next(r for r in result["sweep"] if r["threshold"] == 0.95)

    assert at_95["embedding_only"] == {
        "hit_rate": 1.0, "false_hit_rate": 1.0, "false_hit_company": None,
        "false_hit_year": 1.0, "false_hit_metric": None,
    }  # fmt: skip
    assert at_95["guarded"]["hit_rate"] == 1.0 and at_95["guarded"]["false_hit_rate"] == 0.0
    assert result["by_kind"]["year"]["guard_passes"] == 0.0
