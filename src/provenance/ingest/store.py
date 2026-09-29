"""Writes ingested companies, filings and financial facts. Runs as the table owner (batch
ingestion); request paths never use this connection. Text fields accept only RedactedText."""

import re
from dataclasses import dataclass
from datetime import date

import numpy as np
import psycopg
from pgvector.psycopg import register_vector

from provenance.ingest.xbrl import FinancialFact
from provenance.security.pii import RedactedText

_PLACEHOLDER = re.compile(r"\[(?:EMAIL|PHONE|SSN|CARD)\]")


@dataclass(frozen=True)
class ChunkRecord:
    chunk_index: int
    text: RedactedText
    char_start: int
    char_end: int
    token_count: int
    embedding: np.ndarray
    context: str


@dataclass(frozen=True)
class SectionRecord:
    item: str
    title: str
    text: RedactedText
    chunks: list[ChunkRecord]


@dataclass(frozen=True)
class DocumentRecord:
    cik: str
    accession: str
    title: str
    fiscal_year: int
    period_end: date
    filed_date: date
    url: str
    acl_groups: list[str]
    sections: list[SectionRecord]


def upsert_company(conn: psycopg.Connection, cik: str, ticker: str, name: str, sector: str) -> None:
    conn.execute(
        "INSERT INTO companies (cik, ticker, name, sector) VALUES (%s, %s, %s, %s)"
        " ON CONFLICT (cik) DO UPDATE SET ticker = EXCLUDED.ticker, name = EXCLUDED.name,"
        " sector = EXCLUDED.sector",
        (cik, ticker, name, sector),
    )


def replace_financial_facts(
    conn: psycopg.Connection, cik: str, facts: list[FinancialFact], acl_groups: list[str]
) -> None:
    with conn.transaction():
        conn.execute("DELETE FROM financial_facts WHERE cik = %s", (cik,))
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO financial_facts (cik, concept, metric, value, unit, fiscal_year,"
                " fiscal_period, period_start, period_end, calendar_frame, form, accession,"
                " filed_date, acl_groups) VALUES"
                " (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                [
                    (
                        f.cik, f.concept, f.metric, f.value, f.unit, f.fiscal_year,
                        f.fiscal_period, f.period_start, f.period_end, f.calendar_frame,
                        f.form, f.accession, f.filed_date, acl_groups,
                    )
                    for f in facts
                ],
            )  # fmt: skip


def replace_document(conn: psycopg.Connection, doc: DocumentRecord) -> int:
    """Idempotent by accession: an existing copy (and its sections/chunks) is replaced."""
    register_vector(conn)
    with conn.transaction():
        conn.execute("DELETE FROM documents WHERE accession = %s", (doc.accession,))
        row = conn.execute(
            "INSERT INTO documents (source, cik, accession, title, fiscal_year, period_end,"
            " filed_date, url, acl_groups) VALUES ('10-K', %s, %s, %s, %s, %s, %s, %s, %s)"
            " RETURNING id",
            (
                doc.cik, doc.accession, doc.title, doc.fiscal_year, doc.period_end,
                doc.filed_date, doc.url, doc.acl_groups,
            ),
        ).fetchone()  # fmt: skip
        assert row is not None
        document_id: int = row[0]
        for section in doc.sections:
            _insert_section(conn, document_id, section, doc.acl_groups)
    return document_id


def _insert_section(
    conn: psycopg.Connection, document_id: int, section: SectionRecord, acl_groups: list[str]
) -> None:
    row = conn.execute(
        "INSERT INTO sections (document_id, item, title, text, pii_redactions, acl_groups)"
        " VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
        (
            document_id,
            section.item,
            section.title,
            section.text.text,
            section.text.total,
            acl_groups,
        ),
    ).fetchone()
    assert row is not None
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO chunks (document_id, section_id, section, chunk_index, text, char_start,"
            " char_end, token_count, embedding, pii_redactions, context, acl_groups) VALUES"
            " (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            [
                (
                    document_id, row[0], section.item, c.chunk_index, c.text.text, c.char_start,
                    c.char_end, c.token_count, c.embedding.astype(np.float32),
                    len(_PLACEHOLDER.findall(c.text.text)), c.context, acl_groups,
                )
                for c in section.chunks
            ],
        )  # fmt: skip
