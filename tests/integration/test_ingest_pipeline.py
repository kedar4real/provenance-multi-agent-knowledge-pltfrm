"""End-to-end ingestion against the real database, with a fake SEC source and embedder."""

import hashlib
from datetime import date
from typing import Any

import numpy as np
import psycopg
import pytest

from provenance.config import Settings
from provenance.db.security import principal_sql
from provenance.ingest.corpus import CorpusCompany
from provenance.ingest.edgar import FilingRef
from provenance.ingest.pipeline import ingest_company
from provenance.security.pii import RedactedText

pytestmark = pytest.mark.integration

CIK = "0000000001"
ACCESSION = "0000000001-25-000001"
RISK = "Tariffs could raise component costs and hurt margins. " * 40
CONTACT = "Reach our risk office at risk.office@testcorp.com or (212) 555-0147. "
FILING_HTML = f"""<html><body>
<p>Item 1. Business</p><p>{"Test Corp makes widgets for industrial customers. " * 40}</p>
<p>Item 1A. Risk Factors</p><p>{RISK}</p><p>{CONTACT}</p>
<p>Item 1B. Unresolved Staff Comments</p><p>None.</p>
<p>Item 7. Management's Discussion and Analysis of Financial Condition</p>
<p>{"Revenue grew on strong widget demand in every region. " * 40}</p>
<p>Item 7A. Quantitative and Qualitative Disclosures About Market Risk</p><p>Rates.</p>
</body></html>"""


class FakeSource:
    async def ticker_map(self) -> dict[str, tuple[str, str]]:
        return {"TEST": (CIK, "Test Corp")}

    async def ten_k_filings(self, cik: str, limit: int) -> list[FilingRef]:
        return [
            FilingRef(
                cik=cik,
                accession=ACCESSION,
                filed=date(2025, 11, 1),
                report_date=date(2025, 9, 27),
                primary_document="test-20250927.htm",
            )
        ]

    async def document_html(self, ref: FilingRef) -> str:
        return FILING_HTML

    async def company_facts(self, cik: str) -> dict[str, Any]:
        revenue = {
            "start": "2024-09-29", "end": "2025-09-27", "val": 1234.0, "fy": 2025, "fp": "FY",
            "form": "10-K", "accn": ACCESSION, "filed": "2025-11-01", "frame": "CY2025",
        }  # fmt: skip
        return {"facts": {"us-gaap": {"Revenues": {"units": {"USD": [revenue]}}}}}


class FakeEmbedder:
    def count_tokens(self, text: str) -> int:
        return len(text.split())

    def embed_for_chunking(self, units: list[str]) -> np.ndarray:
        return np.array([[1.0, 0.0] if "Tariff" in u else [0.0, 1.0] for u in units])

    def embed_passages(self, passages: list[RedactedText], headers: list[str]) -> np.ndarray:
        assert all(isinstance(p, RedactedText) for p in passages)
        rows = []
        for p, h in zip(passages, headers, strict=True):
            seed = int(hashlib.sha256((h + p.text).encode()).hexdigest()[:8], 16)
            v = np.random.default_rng(seed).standard_normal(384)
            rows.append(v / np.linalg.norm(v))
        return np.array(rows)


COMPANY = CorpusCompany(ticker="TEST", sector="tech")


@pytest.fixture
def ingested(owner: psycopg.Connection, migrated: Settings) -> psycopg.Connection:
    owner.execute(
        "TRUNCATE companies, documents, sections, chunks, financial_facts RESTART IDENTITY CASCADE"
    )
    with psycopg.connect(migrated.owner_dsn) as conn:
        import asyncio

        asyncio.run(ingest_company(COMPANY, FakeSource(), FakeEmbedder(), conn, filings=1))
    return owner


def count(conn: psycopg.Connection, sql: str) -> int:
    row = conn.execute(sql).fetchone()
    assert row is not None
    return int(row[0])


def test_stores_the_three_sections_with_chunks(ingested: psycopg.Connection) -> None:
    items = ingested.execute("SELECT item FROM sections ORDER BY item").fetchall()

    assert [r[0] for r in items] == ["1", "1A", "7"]
    assert count(ingested, "SELECT count(*) FROM chunks") >= 3


def test_pii_never_reaches_any_stored_text(ingested: psycopg.Connection) -> None:
    for table in ("sections", "chunks"):
        leaked = count(
            ingested,
            f"SELECT count(*) FROM {table} WHERE text LIKE '%testcorp.com%' OR text LIKE '%555-0147%'",
        )
        assert leaked == 0, table
    assert count(ingested, "SELECT count(*) FROM sections WHERE text LIKE '%[EMAIL]%'") == 1
    assert count(ingested, "SELECT sum(pii_redactions) FROM sections") == 2


def test_every_chunk_offset_resolves_to_its_text_in_the_section(
    ingested: psycopg.Connection,
) -> None:
    mismatches = count(
        ingested,
        "SELECT count(*) FROM chunks c JOIN sections s ON s.id = c.section_id"
        " WHERE substr(s.text, c.char_start + 1, c.char_end - c.char_start) <> c.text",
    )

    assert mismatches == 0


def test_chunks_carry_a_context_header_naming_company_and_section(
    ingested: psycopg.Connection,
) -> None:
    row = ingested.execute("SELECT context FROM chunks WHERE section = '1A' LIMIT 1").fetchone()

    assert row == ("Test Corp (TEST) 10-K fiscal 2025, Item 1A Risk Factors",)


def test_financial_facts_are_stored_with_the_sector_groups(ingested: psycopg.Connection) -> None:
    row = ingested.execute(
        "SELECT metric, fiscal_year, value, acl_groups FROM financial_facts"
    ).fetchone()

    assert row == ("revenue", 2025, 1234, ["analyst_tech", "research_all"])


def test_reingesting_replaces_instead_of_duplicating(
    ingested: psycopg.Connection, migrated: Settings
) -> None:
    before = count(ingested, "SELECT count(*) FROM chunks")
    with psycopg.connect(migrated.owner_dsn) as conn:
        import asyncio

        asyncio.run(ingest_company(COMPANY, FakeSource(), FakeEmbedder(), conn, filings=1))

    assert count(ingested, "SELECT count(*) FROM chunks") == before
    assert count(ingested, "SELECT count(*) FROM documents") == 1
    assert count(ingested, "SELECT count(*) FROM financial_facts") == 1


@pytest.mark.parametrize(
    ("groups", "visible"), [(["analyst_tech"], True), (["analyst_energy"], False)]
)
def test_ingested_rows_are_scoped_to_the_sector(
    ingested: psycopg.Connection, app: psycopg.Connection, migrated: Settings,
    groups: list[str], visible: bool,
) -> None:  # fmt: skip
    sql, params = principal_sql(groups, migrated.rls_signing_key.get_secret_value())
    app.execute(sql, params)

    assert (count(app, "SELECT count(*) FROM chunks") > 0) is visible
