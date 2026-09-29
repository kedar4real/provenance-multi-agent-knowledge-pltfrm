from collections.abc import Iterator

import psycopg
import pytest

from provenance.config import Settings
from provenance.db.migrate import MIGRATIONS_DIR, apply_migrations


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
