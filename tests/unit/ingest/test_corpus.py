import pytest

from provenance.ingest.corpus import ALL_RESEARCH_GROUP, CORPUS, CorpusCompany


def test_corpus_has_thirty_unique_companies() -> None:
    tickers = [c.ticker for c in CORPUS]

    assert len(tickers) == 30
    assert len(set(tickers)) == 30


def test_each_company_is_visible_to_its_sector_and_all_research() -> None:
    apple = next(c for c in CORPUS if c.ticker == "AAPL")

    assert apple.acl_groups == ["analyst_tech", ALL_RESEARCH_GROUP]


def test_exxon_is_pinned_to_the_entity_that_files_its_10ks() -> None:
    # In 2026 the XOM ticker moved to a new holding company that has no 10-Ks yet.
    exxon = next(c for c in CORPUS if c.ticker == "XOM")

    assert exxon.cik == "0000034088"


def test_a_pinned_cik_needs_a_name() -> None:
    with pytest.raises(ValueError):
        CorpusCompany(ticker="XOM", sector="energy", cik="0000034088")
