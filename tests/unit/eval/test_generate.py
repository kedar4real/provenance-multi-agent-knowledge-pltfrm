from eval.generate import copies_passage

PASSAGE = (
    "Executive members accounted for approximately 73.6% of worldwide net sales in "
    "fiscal 2025, and they also qualify for an annual two-percent reward."
)


def test_using_the_filings_own_terms_is_not_copying() -> None:
    assert not copies_passage(
        "What share of Costco's net sales came from Executive members?", PASSAGE
    )


def test_an_eight_word_run_is_copying() -> None:
    question = (
        "Is it true Executive members accounted for approximately 73.6% of worldwide net sales?"
    )

    assert copies_passage(question, PASSAGE)


def test_punctuation_and_case_do_not_hide_a_copy() -> None:
    question = "EXECUTIVE MEMBERS, accounted for approximately 73.6% of worldwide net sales"

    assert copies_passage(question, PASSAGE)


def test_a_seven_word_run_is_allowed() -> None:
    # "account" vs "accounted" breaks the run: 7 shared words, not 8.
    question = "Did Executive members account for approximately 73.6% of worldwide net sales?"

    assert not copies_passage(question, PASSAGE)
