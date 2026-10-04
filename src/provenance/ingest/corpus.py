"""The demo corpus: 30 companies across 7 sectors. Each sector is an access group, so a
sector analyst sees only their sector's filings; `research_all` sees everything."""

from pydantic import BaseModel, model_validator

ALL_RESEARCH_GROUP = "research_all"


class CorpusCompany(BaseModel):
    """`cik`/`name` pin the SEC filer when the ticker map points elsewhere (see XOM)."""

    ticker: str
    sector: str
    cik: str | None = None
    name: str | None = None

    @model_validator(mode="after")
    def _pin_is_complete(self) -> "CorpusCompany":
        if (self.cik is None) != (self.name is None):
            raise ValueError("a pinned company needs both cik and name")
        return self

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

# In July 2026 the XOM ticker moved to a new holding company (CIK 0002115436) that has not
# filed a 10-K yet; the 10-Ks and XBRL facts are under the original Exxon Mobil Corp.
_PINNED: dict[str, tuple[str, str]] = {"XOM": ("0000034088", "Exxon Mobil Corp")}

CORPUS: list[CorpusCompany] = [
    CorpusCompany(
        ticker=t,
        sector=sector,
        cik=_PINNED[t][0] if t in _PINNED else None,
        name=_PINNED[t][1] if t in _PINNED else None,
    )
    for sector, tickers in _SECTORS.items()
    for t in tickers
]
FILINGS_PER_COMPANY = 2

# How people refer to each company. SEC's registered names ("JPMORGAN CHASE & CO",
# "BANK OF AMERICA CORP /DE/") are for filings; questions and the UI use these.
COMMON_NAMES: dict[str, str] = {
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "GOOGL": "Alphabet",
    "META": "Meta", "AMZN": "Amazon", "WMT": "Walmart", "COST": "Costco", "TGT": "Target",
    "HD": "Home Depot", "JPM": "JPMorgan Chase", "BAC": "Bank of America",
    "GS": "Goldman Sachs", "V": "Visa", "JNJ": "Johnson & Johnson", "PFE": "Pfizer",
    "UNH": "UnitedHealth", "LLY": "Eli Lilly", "MRK": "Merck", "XOM": "ExxonMobil",
    "CVX": "Chevron", "COP": "ConocoPhillips", "CAT": "Caterpillar", "BA": "Boeing",
    "GE": "GE Aerospace", "UPS": "UPS", "KO": "Coca-Cola", "PEP": "PepsiCo",
    "PG": "Procter & Gamble", "NKE": "Nike",
}  # fmt: skip
