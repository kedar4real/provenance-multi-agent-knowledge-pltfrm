from eval.answer_eval import summarize


def row(category: str, correct: str, claims: int, supported: int, declined: bool = False,
        expect_abstain: bool = False) -> dict[str, object]:  # fmt: skip
    return {
        "case": "x", "category": category, "declined": declined,
        "expect_abstain": expect_abstain, "correct": correct, "claims": claims,
        "supported": supported, "faithfulness": supported / claims if claims else None,
        "leaked": [], "answer": "", "model": "fake",
    }  # fmt: skip


def test_summary_reports_correctness_faithfulness_and_declines() -> None:
    rows = [
        row("text", "yes", 4, 4),
        row("text", "partial", 4, 2),
        row("unanswerable", "no", 0, 0, declined=True, expect_abstain=True),
    ]

    table = summarize(rows)

    assert "| text | 2 | 50% | 50% | 0.75 | 0/2 | 0 |" in table
    # A declined answer has no claims, so faithfulness doesn't apply ("-").
    assert "| unanswerable | 1 | 0% | 0% | - | 1/1 | 1 |" in table
    assert "| all | 3 |" in table
    assert "ACL leaks in retrieved context: 0" in table


def test_per_category_sampling_takes_the_first_n_of_each() -> None:
    from eval.answer_eval import first_per_category
    from eval.schema import GoldenCase

    cases = [
        GoldenCase(id=f"{cat}-{i}", category=cat, question="q", reference_answer="a")
        for cat in ("text", "sql") for i in range(3)
    ]  # fmt: skip

    assert [c.id for c in first_per_category(cases, 2)] == ["text-0", "text-1", "sql-0", "sql-1"]
