from provenance.ingest.corpus import ALL_RESEARCH_GROUP, CORPUS


def test_corpus_has_thirty_unique_companies() -> None:
    tickers = [c.ticker for c in CORPUS]

    assert len(tickers) == 30
    assert len(set(tickers)) == 30


def test_each_company_is_visible_to_its_sector_and_all_research() -> None:
    apple = next(c for c in CORPUS if c.ticker == "AAPL")

    assert apple.acl_groups == ["analyst_tech", ALL_RESEARCH_GROUP]
