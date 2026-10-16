"""Reading the audit log: auditors only, enforced by the API and again by the database."""

import json
from collections.abc import AsyncIterator
from pathlib import Path

import psycopg
import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from provenance.api.main import create_app
from provenance.api.principals import hash_key
from provenance.config import Settings
from provenance.db.security import principal_sql

pytestmark = [pytest.mark.integration, pytest.mark.usefixtures("seeded")]

KEYS = {"pk_auditor": "auditor", "pk_tech": "tech"}


@pytest.fixture
def logged(owner: psycopg.Connection, seeded: None) -> None:
    owner.execute("TRUNCATE audit_log")
    owner.execute(
        "INSERT INTO audit_log (request_id, principal, groups, tool, input_preview, outcome,"
        " detail) VALUES ('r1', 'tech', '{analyst_tech}', 'search', 'apple tariffs', 'ok',"
        " '{\"passages\": 3}'), ('r2', 'tech', '{analyst_tech}', 'sql', 'revenue', 'error', '{}')"
    )
    owner.execute("UPDATE chunks SET injection_flagged = true, injection_score = 0.97")


@pytest.fixture
async def client(migrated: Settings, tmp_path: Path) -> AsyncIterator[AsyncClient]:
    principals = tmp_path / "principals.yaml"
    principals.write_text(
        "principals:\n"
        "  auditor: {display_name: Audit, groups: [analyst_tech, auditor]}\n"
        "  tech: {display_name: Tech, groups: [analyst_tech]}\n",
        encoding="utf-8",
    )
    api_keys = tmp_path / "api_keys.json"
    api_keys.write_text(json.dumps({hash_key(k): n for k, n in KEYS.items()}), encoding="utf-8")
    settings = migrated.model_copy(
        update={"principals_path": principals, "api_keys_path": api_keys, "load_models": False}
    )
    app = create_app(settings)
    async with (
        LifespanManager(app) as manager,
        AsyncClient(transport=ASGITransport(manager.app), base_url="http://test") as c,
    ):
        yield c


@pytest.mark.usefixtures("logged")
async def test_an_auditor_reads_entries_daily_counts_and_quarantined_passages(
    client: AsyncClient,
) -> None:
    response = await client.get("/v1/audit", headers={"X-API-Key": "pk_auditor"})

    assert response.status_code == 200, response.text
    body = response.json()
    assert sorted((e["principal"], e["tool"], e["outcome"]) for e in body["entries"]) == [
        ("tech", "search", "ok"),
        ("tech", "sql", "error"),
    ]
    assert sum(d["calls"] for d in body["daily"]) == 2
    # Quarantined passages go through row-level security: only the auditor's own sector.
    assert {q["ticker"] for q in body["quarantined"]} == {"AAPL"}
    assert body["flagged"] == len(body["quarantined"]) == 1


@pytest.mark.usefixtures("logged")
async def test_anyone_else_is_refused(client: AsyncClient) -> None:
    response = await client.get("/v1/audit", headers={"X-API-Key": "pk_tech"})

    assert response.status_code == 403


@pytest.mark.usefixtures("logged")
def test_the_database_refuses_the_reader_without_the_auditor_group(
    app: psycopg.Connection, migrated: Settings
) -> None:
    sql, params = principal_sql(["analyst_tech"], migrated.rls_signing_key.get_secret_value())
    app.execute(sql, params)

    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        app.execute("SELECT * FROM audit_recent(10)")


@pytest.mark.usefixtures("logged")
def test_the_app_role_still_cannot_select_the_log_directly(
    app: psycopg.Connection, migrated: Settings
) -> None:
    sql, params = principal_sql(["auditor"], migrated.rls_signing_key.get_secret_value())
    app.execute(sql, params)

    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        app.execute("SELECT * FROM audit_log")
