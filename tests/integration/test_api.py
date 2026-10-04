"""The API end to end against the real Postgres + Redis: an API key becomes a principal, and
row-level security decides what that principal sees."""

import json
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from provenance.api.main import create_app
from provenance.api.principals import hash_key
from provenance.config import Settings

pytestmark = [pytest.mark.integration, pytest.mark.usefixtures("seeded")]

KEYS = {"pk_tech": "tech", "pk_internal": "internal", "pk_finance": "finance"}


@pytest.fixture
async def client(migrated: Settings, tmp_path: Path) -> AsyncIterator[AsyncClient]:
    principals = tmp_path / "principals.yaml"
    principals.write_text(
        "principals:\n"
        "  tech: {display_name: Tech, groups: [analyst_tech]}\n"
        "  internal: {display_name: Internal, groups: [analyst_tech, internal_restricted]}\n"
        "  finance: {display_name: Finance, groups: [analyst_finance]}\n",
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


async def me(client: AsyncClient, key: str) -> dict[str, object]:
    response = await client.get("/v1/me", headers={"X-API-Key": key})
    assert response.status_code == 200, response.text
    body: dict[str, object] = response.json()
    return body


async def test_ready_when_postgres_and_redis_are_up(client: AsyncClient) -> None:
    response = await client.get("/health/ready")

    assert response.status_code == 200
    assert response.json()["checks"] == {"postgres": "ok", "redis": "ok"}


async def test_analyst_sees_only_their_groups_rows(client: AsyncClient) -> None:
    body = await me(client, "pk_tech")

    assert body["groups"] == ["analyst_tech"]
    assert body["visible"] == {
        "documents": 1,
        "chunks": 1,
        "financial_facts": 1,
        "tickers": ["AAPL"],
    }


async def test_extra_group_unlocks_restricted_rows(client: AsyncClient) -> None:
    body = await me(client, "pk_internal")

    assert body["visible"] == {
        "documents": 2,
        "chunks": 2,
        "financial_facts": 2,
        "tickers": ["AAPL"],
    }


async def test_unrelated_group_sees_nothing(client: AsyncClient) -> None:
    body = await me(client, "pk_finance")

    assert body["visible"] == {"documents": 0, "chunks": 0, "financial_facts": 0, "tickers": []}


async def test_principals_do_not_leak_across_pooled_connections(client: AsyncClient) -> None:
    # Alternate callers on the same small pool; each must see exactly its own rows.
    for _ in range(5):
        assert (await me(client, "pk_internal"))["visible"]["documents"] == 2  # type: ignore[index]
        assert (await me(client, "pk_finance"))["visible"]["documents"] == 0  # type: ignore[index]
