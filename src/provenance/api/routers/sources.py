"""A cited passage in its context: the surrounding section text with the span's offsets, so
a client can show exactly what was cited and what came before and after it."""

from fastapi import APIRouter, Query
from pydantic import BaseModel

from provenance.api.deps import DbDep
from provenance.api.errors import ApiError
from provenance.ingest.corpus import COMMON_NAMES

router = APIRouter(prefix="/v1", tags=["sources"])

# Sections run up to ~390K characters (JPMorgan's MD&A); send a window, not the section.
MAX_WINDOW = 6000

_SOURCE = """
SELECT c.id, co.ticker, co.name, d.fiscal_year, c.section, s.title, d.title, d.url,
       d.accession, c.char_start, c.char_end, length(s.text),
       substr(s.text, greatest(c.char_start - %(w)s, 0) + 1,
              (c.char_end - c.char_start) + 2 * %(w)s) AS excerpt,
       greatest(c.char_start - %(w)s, 0) AS window_start
FROM chunks c
JOIN sections s ON s.id = c.section_id
JOIN documents d ON d.id = c.document_id
JOIN companies co ON co.cik = d.cik
WHERE c.id = %(id)s
"""


class Source(BaseModel):
    chunk_id: int
    ticker: str
    company: str
    fiscal_year: int
    item: str
    section_title: str
    document_title: str
    url: str
    accession: str
    text: str
    # Offsets of the cited span within `text`, and where `text` starts in the section.
    highlight_start: int
    highlight_end: int
    window_start: int
    section_length: int


@router.get("/sources/{chunk_id}")
async def source(
    chunk_id: int, db: DbDep, window: int = Query(default=1500, ge=0, le=MAX_WINDOW)
) -> Source:
    cur = await db.execute(_SOURCE, {"id": chunk_id, "w": window})
    row = await cur.fetchone()
    if row is None:
        # Same answer for "doesn't exist" and "not yours": existence isn't disclosed.
        raise ApiError(404, "source_not_found", "no such source")
    (cid, ticker, legal_name, year, item, section_title, doc_title, url, accession,
     start, end, section_length, excerpt, window_start) = row  # fmt: skip
    return Source(
        chunk_id=cid,
        ticker=ticker,
        company=COMMON_NAMES.get(ticker, legal_name),
        fiscal_year=year,
        item=item,
        section_title=section_title,
        document_title=doc_title,
        url=url,
        accession=accession,
        text=excerpt,
        highlight_start=start - window_start,
        highlight_end=end - window_start,
        window_start=window_start,
        section_length=section_length,
    )
