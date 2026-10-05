import pytest

from provenance.verifier.claims import split_claims
from provenance.verifier.jev import JevProvider, ProviderNotConfigured
from provenance.verifier.nli import _windows
from provenance.verifier.signals import FEATURES, claim_signals

ANSWER = """JPMorgan's net interest income was $95.4 billion, up 3% [P3]. It rose on rates [P5].

This increase was driven by:
* Higher revolving balances in Card Services [P3, P5]
* Higher wholesale deposit balances [P3]"""


def test_splits_sentences_and_bullets_and_keeps_citations() -> None:
    claims = split_claims(ANSWER)

    assert [c.text for c in claims] == [
        "JPMorgan's net interest income was $95.4 billion, up 3%",
        "It rose on rates",
        "Higher revolving balances in Card Services",
        "Higher wholesale deposit balances",
    ]
    assert claims[2].cited == ["P3", "P5"]


def test_short_fragments_and_lead_ins_are_not_claims() -> None:
    # "It rose on rates" (4 words, kept) vs a 3-word fragment (dropped); lead-ins dropped.
    texts = [c.text for c in split_claims("Up [P1]. It rose on rates [P2]. Drivers were:")]
    assert texts == ["It rose on rates"]


def test_a_decline_has_no_claims() -> None:
    assert split_claims("INSUFFICIENT_EVIDENCE") == []


class FakeNli:
    def scores(self, evidence: list[str], claim: str) -> tuple[float, float]:
        return (0.9, 0.05)


def test_signals_check_numbers_and_word_overlap() -> None:
    evidence = ["Net interest income was $95.4 billion, up 3%, on higher card balances."]

    good = claim_signals("Net interest income was $95.4 billion", evidence, FakeNli(), 0.99)
    bad = claim_signals("Net interest income was $81.0 billion", evidence, FakeNli(), 0.99)
    wordless = claim_signals("Revenue grew on strong demand", evidence, FakeNli(), None)

    assert (good.numbers_ok, good.has_numbers) == (1.0, 1.0)
    assert bad.numbers_ok == 0.0
    assert (wordless.has_numbers, wordless.numbers_ok, wordless.top_rerank) == (0.0, 1.0, 0.0)
    assert good.overlap > wordless.overlap
    assert len(good.vector()) == len(FEATURES)


def test_long_evidence_is_windowed_with_overlap() -> None:
    text = " ".join(f"w{i}" for i in range(500))

    windows = _windows(text)

    assert len(windows) == 3
    assert all(len(w.split()) <= 220 for w in windows)
    assert windows[1].split()[0] == "w160"


def test_the_jev_slot_fails_loudly() -> None:
    with pytest.raises(ProviderNotConfigured, match="not configured"):
        JevProvider().confidence("claim", ["evidence"])
