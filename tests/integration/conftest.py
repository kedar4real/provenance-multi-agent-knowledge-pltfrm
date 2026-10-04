from collections.abc import Iterator

import psycopg
import pytest

from provenance.config import Settings
from provenance.db.migrate import MIGRATIONS_DIR, apply_migrations

TECH = ["analyst_tech"]
RESTRICTED = ["internal_restricted"]


def _to_test_db(dsn: str) -> str:
    return dsn.rsplit("/", 1)[0] + "/provenance_test"


@pytest.fixture(scope="session")
def settings() -> Settings:
    s = Settings()
    try:
        psycopg.connect(s.owner_dsn, connect_timeout=3).close()
    except psycopg.OperationalError:
        pytest.skip("Postgres is not running (docker compose up -d)")
    return s.model_copy(
        update={
            "owner_dsn": _to_test_db(s.owner_dsn),
            "app_dsn": _to_test_db(s.app_dsn),
            "sql_ro_dsn": _to_test_db(s.sql_ro_dsn),
        }
    )


@pytest.fixture(scope="session")
def migrated(settings: Settings) -> Settings:
    with psycopg.connect(settings.owner_dsn, autocommit=True) as conn:
        conn.execute("DROP SCHEMA public CASCADE")
        conn.execute("CREATE SCHEMA public")
    apply_migrations(
        settings.owner_dsn, MIGRATIONS_DIR, settings.rls_signing_key.get_secret_value()
    )
    return settings


@pytest.fixture
def owner(migrated: Settings) -> Iterator[psycopg.Connection]:
    with psycopg.connect(migrated.owner_dsn, autocommit=True) as conn:
        yield conn


@pytest.fixture
def app(migrated: Settings) -> Iterator[psycopg.Connection]:
    with psycopg.connect(migrated.app_dsn) as conn:
        yield conn


@pytest.fixture
def sql_ro(migrated: Settings) -> Iterator[psycopg.Connection]:
    with psycopg.connect(migrated.sql_ro_dsn) as conn:
        yield conn


def vec(first: float) -> str:
    return "[" + ",".join([str(first)] + ["0"] * 383) + "]"


@pytest.fixture
def seeded(owner: psycopg.Connection) -> None:
    owner.execute("TRUNCATE companies, documents, chunks, financial_facts RESTART IDENTITY CASCADE")
    owner.execute(
        "INSERT INTO companies (cik, ticker, name, sector) VALUES ('0000320193','AAPL','Apple','tech')"
    )
    for title, acl, text, emb in [
        ("Apple 10-K 2024", TECH, "supply chain risk in the tariff section", vec(1.0)),
        ("Board memo", RESTRICTED, "confidential tariff merger plan", vec(0.9)),
    ]:
        doc_id = owner.execute(
            "INSERT INTO documents (source, cik, title, acl_groups) "
            "VALUES ('10-K', '0000320193', %s, %s) RETURNING id",
            (title, acl),
        ).fetchone()[0]  # type: ignore[index]
        section_id = owner.execute(
            "INSERT INTO sections (document_id, item, title, text, acl_groups)"
            " VALUES (%s, '1A', 'Risk Factors', %s, %s) RETURNING id",
            (doc_id, text, acl),
        ).fetchone()[0]  # type: ignore[index]
        owner.execute(
            "INSERT INTO chunks (document_id, section_id, section, chunk_index, text, char_start,"
            " char_end, token_count, embedding, acl_groups) VALUES (%s,%s,'1A',0,%s,0,40,8,%s,%s)",
            (doc_id, section_id, text, emb, acl),
        )
    for acl, value in [(TECH, 391035000000), (RESTRICTED, 1)]:
        owner.execute(
            "INSERT INTO financial_facts (cik, concept, metric, value, unit, fiscal_year,"
            " fiscal_period, period_end, form, accession, filed_date, acl_groups) VALUES"
            " ('0000320193','Revenues','revenue',%s,'USD',2024,%s,'2024-09-28','10-K',"
            "'0000320193-24-000123','2024-11-01',%s)",
            (value, "FY" if acl == TECH else "Q4", acl),
        )
