from provenance.agents.types import Evidence
from provenance.agents.verify import numbers_in, verify

PASSAGE = Evidence(
    id="P1", kind="passage", label="JPM FY2025 MD&A",
    text="Net interest income was $6.1 billion, down $3.7 billion. Net interest income - "
    "reported $ 95,443 (in millions). Executive members were 73.6% of net sales.",
)  # fmt: skip
FACT = Evidence(id="F1", kind="fact", label="AAPL", text="AAPL FY2025 revenue = 416161000000 USD")
EVIDENCE = [PASSAGE, FACT]


def test_reads_scaled_numbers_and_skips_years() -> None:
    values = dict(numbers_in("In 2025 revenue was $416.2 billion, up 6.4%, on 1,234 stores."))

    assert values == {"416.2 billion": 416.2e9, "6.4%": 6.4, "1,234": 1234.0}


def test_supported_numbers_pass_across_scales_and_rounding() -> None:
    answer = (
        "Net interest income was $6.1 billion [P1], or $95.4 billion managed [P1]; "
        "Apple's revenue was $416.16 billion [F1]. Executive members: 73.6% [P1]."
    )

    assert verify(answer, EVIDENCE).ok


def test_an_invented_figure_is_caught() -> None:
    result = verify("Net interest income was $7.9 billion [P1].", EVIDENCE)

    assert not result.ok
    assert result.unsupported_numbers == ["7.9 billion"]


def test_a_number_must_be_in_the_evidence_it_cites() -> None:
    # 416 billion is real, but it's in F1, not the cited P1.
    assert not verify("Apple's revenue was $416.16 billion [P1].", EVIDENCE).ok


def test_citations_must_exist_and_answers_must_cite() -> None:
    assert verify("Revenue rose [P7].", EVIDENCE).unknown_citations == ["P7"]
    assert verify("Revenue rose a lot.", EVIDENCE).uncited


def test_small_counts_are_not_figures() -> None:
    assert verify("JPM reports in 3 segments [P1].", EVIDENCE).ok


def test_a_decline_needs_no_citations() -> None:
    assert verify("INSUFFICIENT_EVIDENCE", EVIDENCE).ok


def test_feedback_names_each_problem() -> None:
    feedback = verify("It was $9.9 billion [P9].", EVIDENCE).feedback()

    assert "P9" in feedback and "9.9 billion" in feedback
