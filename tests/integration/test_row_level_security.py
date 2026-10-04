"""Attacks on per-user document access, run against the real Postgres in docker compose."""

import psycopg
import pytest

from provenance.config import Settings
from provenance.db.migrate import MIGRATIONS_DIR, apply_migrations
from provenance.db.security import principal_sql
from tests.integration.conftest import RESTRICTED, TECH, vec

pytestmark = [pytest.mark.integration, pytest.mark.usefixtures("seeded")]


def as_principal(conn: psycopg.Connection, groups: list[str], key: str) -> None:
    sql, params = principal_sql(groups, key)
    conn.execute(sql, params)


def titles(conn: psycopg.Connection) -> list[str]:
    return [r[0] for r in conn.execute("SELECT title FROM documents ORDER BY title").fetchall()]


def test_no_principal_sees_nothing(app: psycopg.Connection) -> None:
    assert titles(app) == []
    assert app.execute("SELECT count(*) FROM chunks").fetchone() == (0,)


def test_unsigned_groups_see_nothing(app: psycopg.Connection) -> None:
    app.execute("SELECT set_config('app.groups', 'analyst_tech', true)")

    assert titles(app) == []


def test_signed_principal_sees_only_its_groups(app: psycopg.Connection, migrated: Settings) -> None:
    as_principal(app, TECH, migrated.rls_signing_key.get_secret_value())

    assert titles(app) == ["Apple 10-K 2024"]


def test_member_of_both_groups_sees_both(app: psycopg.Connection, migrated: Settings) -> None:
    as_principal(app, TECH + RESTRICTED, migrated.rls_signing_key.get_secret_value())

    assert titles(app) == ["Apple 10-K 2024", "Board memo"]


def test_forged_group_change_after_signing_sees_nothing(
    app: psycopg.Connection, migrated: Settings
) -> None:
    as_principal(app, TECH, migrated.rls_signing_key.get_secret_value())

    # What injected SQL would try: keep the valid signature, swap in a privileged group.
    app.execute("SELECT set_config('app.groups', 'internal_restricted', true)")

    assert titles(app) == []


def test_section_text_for_citations_respects_permissions(
    app: psycopg.Connection, migrated: Settings
) -> None:
    as_principal(app, TECH, migrated.rls_signing_key.get_secret_value())

    rows = app.execute("SELECT text FROM sections").fetchall()

    assert rows == [("supply chain risk in the tariff section",)]


def test_bm25_search_respects_permissions(app: psycopg.Connection, migrated: Settings) -> None:
    as_principal(app, TECH, migrated.rls_signing_key.get_secret_value())

    hits = app.execute("SELECT text FROM chunks WHERE text @@@ 'tariff'").fetchall()

    assert hits == [("supply chain risk in the tariff section",)]


def test_vector_search_respects_permissions(app: psycopg.Connection, migrated: Settings) -> None:
    as_principal(app, TECH, migrated.rls_signing_key.get_secret_value())

    hits = app.execute(
        "SELECT text FROM chunks ORDER BY embedding <=> %s::vector LIMIT 5", (vec(0.9),)
    ).fetchall()

    assert hits == [("supply chain risk in the tariff section",)]


def test_sql_role_sees_only_permitted_financial_rows(
    sql_ro: psycopg.Connection, migrated: Settings
) -> None:
    as_principal(sql_ro, TECH, migrated.rls_signing_key.get_secret_value())

    rows = sql_ro.execute("SELECT fiscal_period FROM financial_facts").fetchall()

    assert rows == [("FY",)]


def test_sql_role_cannot_read_documents(sql_ro: psycopg.Connection) -> None:
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        sql_ro.execute("SELECT * FROM chunks")


def test_sql_role_cannot_write(sql_ro: psycopg.Connection) -> None:
    with pytest.raises(psycopg.errors.ReadOnlySqlTransaction):
        sql_ro.execute("DELETE FROM financial_facts")


def test_sql_role_has_a_statement_timeout(sql_ro: psycopg.Connection) -> None:
    with pytest.raises(psycopg.errors.QueryCanceled):
        sql_ro.execute("SELECT pg_sleep(5)")


@pytest.mark.parametrize("role", ["app", "sql_ro"])
def test_query_roles_cannot_read_the_signing_secret(
    role: str, request: pytest.FixtureRequest
) -> None:
    conn: psycopg.Connection = request.getfixturevalue(role)

    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        conn.execute("SELECT value FROM app_secrets")


def test_app_role_cannot_switch_off_row_security(app: psycopg.Connection) -> None:
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        app.execute("ALTER TABLE chunks DISABLE ROW LEVEL SECURITY")


def test_migrations_are_applied_once(migrated: Settings) -> None:
    applied = apply_migrations(
        migrated.owner_dsn, MIGRATIONS_DIR, migrated.rls_signing_key.get_secret_value()
    )

    assert applied == []
