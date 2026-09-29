"""The demo corpus: 30 companies across 7 sectors. Each sector is an access group, so a
sector analyst sees only their sector's filings; `research_all` sees everything."""

from pydantic import BaseModel

ALL_RESEARCH_GROUP = "research_all"


class CorpusCompany(BaseModel):
    ticker: str
    sector: str

    @property
    def acl_groups(self) -> list[str]:
        return [f"analyst_{self.sector}", ALL_RESEARCH_GROUP]


_SECTORS: dict[str, list[str]] = {
    "tech": ["AAPL", "MSFT", "NVDA", "GOOGL", "META"],
    "retail": ["AMZN", "WMT", "COST", "TGT", "HD"],
    "finance": ["JPM", "BAC", "GS", "V"],
    "healthcare": ["JNJ", "PFE", "UNH", "LLY", "MRK"],
    "energy": ["XOM", "CVX", "COP"],
    "industrials": ["CAT", "BA", "GE", "UPS"],
    "consumer": ["KO", "PEP", "PG", "NKE"],
}

CORPUS: list[CorpusCompany] = [
    CorpusCompany(ticker=t, sector=sector) for sector, tickers in _SECTORS.items() for t in tickers
]
FILINGS_PER_COMPANY = 2
