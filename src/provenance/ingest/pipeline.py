"""Ingests one company: financial facts, then each recent 10-K through
sections -> PII redaction -> semantic chunks -> embeddings -> store."""

import asyncio
import time
from typing import Any, Protocol

import numpy as np
import psycopg
from pydantic import BaseModel

from provenance.ingest.chunking import semantic_chunks
from provenance.ingest.corpus import CorpusCompany
from provenance.ingest.edgar import FilingRef
from provenance.ingest.sections import TARGET_ITEMS, extract_items, html_to_text
from provenance.ingest.store import (
    ChunkRecord,
    DocumentRecord,
    SectionRecord,
    replace_document,
    replace_financial_facts,
    upsert_company,
)
from provenance.ingest.xbrl import annual_facts
from provenance.security.pii import RedactedText, redact

ITEM_TITLES = {"1": "Business", "1A": "Risk Factors", "7": "Management's Discussion and Analysis"}


class FilingSource(Protocol):
    async def ticker_map(self) -> dict[str, tuple[str, str]]: ...
    async def ten_k_filings(self, cik: str, limit: int) -> list[FilingRef]: ...
    async def document_html(self, ref: FilingRef) -> str: ...
    async def company_facts(self, cik: str) -> dict[str, Any]: ...


class ChunkEmbedder(Protocol):
    def count_tokens(self, text: str) -> int: ...
    def embed_for_chunking(self, units: list[str]) -> np.ndarray: ...
    def embed_passages(self, passages: list[RedactedText], headers: list[str]) -> np.ndarray: ...


class FilingReport(BaseModel):
    ticker: str
    accession: str
    fiscal_year: int
    chunks_by_item: dict[str, int]
    pii_redactions: int
    seconds: float


async def ingest_company(
    company: CorpusCompany,
    source: FilingSource,
    embedder: ChunkEmbedder,
    conn: psycopg.Connection,
    filings: int,
) -> list[FilingReport]:
    if company.cik and company.name:
        cik, name = company.cik, company.name
    else:
        tickers = await source.ticker_map()
        if company.ticker not in tickers:
            raise ValueError(f"ticker {company.ticker} not found in SEC's ticker list")
        cik, name = tickers[company.ticker]
    facts = annual_facts(cik, await source.company_facts(cik))

    def store_company() -> None:
        upsert_company(conn, cik, company.ticker, name, company.sector)
        replace_financial_facts(conn, cik, facts, company.acl_groups)
        conn.commit()

    await asyncio.to_thread(store_company)
    fiscal_year_by_accession = {f.accession: f.fiscal_year for f in facts}

    reports = []
    for ref in await source.ten_k_filings(cik, filings):
        html = await source.document_html(ref)
        fiscal_year = fiscal_year_by_accession.get(ref.accession, ref.report_date.year)
        report = await asyncio.to_thread(
            _ingest_filing, company, name, ref, html, fiscal_year, embedder, conn
        )
        reports.append(report)
    return reports


def _ingest_filing(
    company: CorpusCompany,
    name: str,
    ref: FilingRef,
    html: str,
    fiscal_year: int,
    embedder: ChunkEmbedder,
    conn: psycopg.Connection,
) -> FilingReport:
    started = time.perf_counter()
    items = extract_items(html_to_text(html))
    sections: list[SectionRecord] = []
    for item in TARGET_ITEMS:
        if item not in items:
            continue
        title = ITEM_TITLES[item]
        context = f"{name} ({company.ticker}) 10-K fiscal {fiscal_year}, Item {item} {title}"
        redacted = redact(items[item].text)
        sections.append(SectionRecord(item, title, redacted, _chunk(redacted, context, embedder)))

    replace_document(
        conn,
        DocumentRecord(
            cik=ref.cik,
            accession=ref.accession,
            title=f"{name} 10-K fiscal {fiscal_year}",
            fiscal_year=fiscal_year,
            period_end=ref.report_date,
            filed_date=ref.filed,
            url=ref.url,
            acl_groups=company.acl_groups,
            sections=sections,
        ),
    )
    conn.commit()
    return FilingReport(
        ticker=company.ticker,
        accession=ref.accession,
        fiscal_year=fiscal_year,
        chunks_by_item={s.item: len(s.chunks) for s in sections},
        pii_redactions=sum(s.text.total for s in sections),
        seconds=round(time.perf_counter() - started, 1),
    )


def _chunk(section: RedactedText, context: str, embedder: ChunkEmbedder) -> list[ChunkRecord]:
    chunks = semantic_chunks(section.text, embedder.embed_for_chunking, embedder.count_tokens)
    if not chunks:
        return []
    pieces = [section.slice(c.char_start, c.char_end) for c in chunks]
    vectors = embedder.embed_passages(pieces, [context] * len(pieces))
    return [
        ChunkRecord(
            chunk_index=i,
            text=piece,
            char_start=c.char_start,
            char_end=c.char_end,
            token_count=c.token_count,
            embedding=vectors[i],
            context=context,
        )
        for i, (c, piece) in enumerate(zip(chunks, pieces, strict=True))
    ]
