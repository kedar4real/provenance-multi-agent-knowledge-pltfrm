from typing import Literal

from pydantic import BaseModel, Field

Item = Literal["1", "1A", "7"]
Mode = Literal["hybrid", "dense", "bm25"]
RewriteStatus = Literal["off", "ok", "failed"]


class SearchFilters(BaseModel):
    """Narrow retrieval to these companies, fiscal years and 10-K Items (empty = any)."""

    tickers: list[str] = Field(default_factory=list)
    fiscal_years: list[int] = Field(default_factory=list)
    items: list[Item] = Field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not (self.tickers or self.fiscal_years or self.items)


class RewrittenQuery(BaseModel):
    query: str
    filters: SearchFilters = Field(default_factory=SearchFilters)


class Hit(BaseModel):
    """One retrieved passage, with everything needed to cite it."""

    chunk_id: int
    document_id: int
    ticker: str
    company: str
    fiscal_year: int
    item: str
    section_title: str
    text: str
    context: str
    char_start: int
    char_end: int
    url: str
    dense_rank: int | None = None
    bm25_rank: int | None = None
    fused_score: float = 0.0
    rerank_score: float | None = None
    # Stored at ingest by the injection scanner; None means not scanned yet.
    injection_flagged: bool | None = None
    injection_reasons: list[str] = Field(default_factory=list)


class SearchResult(BaseModel):
    query: str
    search_query: str
    filters: SearchFilters
    filters_relaxed: bool = False
    rewrite: RewriteStatus = "off"
    mode: Mode
    reranked: bool
    hits: list[Hit]
    timings_ms: dict[str, float]
