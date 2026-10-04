"""App behaviour that needs no database: auth failures, error shape, request IDs, health."""

from httpx import AsyncClient

from provenance.api.main import create_app
from provenance.config import Settings


async def test_liveness_needs_nothing(client: AsyncClient) -> None:
    response = await client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_readiness_reports_unreachable_dependencies(client: AsyncClient) -> None:
    response = await client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "unavailable",
        "checks": {"postgres": "unavailable", "redis": "unavailable"},
    }


async def test_missing_api_key_is_401(client: AsyncClient) -> None:
    response = await client.get("/v1/me")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "ApiKey"
    assert response.json()["error"]["code"] == "missing_api_key"


async def test_wrong_api_key_is_401(client: AsyncClient) -> None:
    response = await client.get("/v1/me", headers={"X-API-Key": "pk_wrong"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_api_key"


async def test_errors_share_one_shape_with_the_request_id(client: AsyncClient) -> None:
    response = await client.get("/nope")

    body = response.json()
    assert response.status_code == 404
    assert body["error"]["code"] == "not_found"
    assert body["error"]["request_id"] == response.headers["X-Request-ID"]


async def test_well_formed_request_id_is_reused(client: AsyncClient) -> None:
    response = await client.get("/health/live", headers={"X-Request-ID": "trace-abc.123"})

    assert response.headers["X-Request-ID"] == "trace-abc.123"


async def test_malformed_request_id_is_replaced(client: AsyncClient) -> None:
    response = await client.get("/health/live", headers={"X-Request-ID": "bad id\twith<html>"})

    assert response.headers["X-Request-ID"] != "bad id\twith<html>"
    assert len(response.headers["X-Request-ID"]) == 32


async def test_unhandled_errors_hide_internals(offline_settings: Settings) -> None:
    from asgi_lifespan import LifespanManager
    from httpx import ASGITransport

    app = create_app(offline_settings)

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("secret connection string postgres://user:pw@host")

    async with (
        LifespanManager(app) as manager,
        AsyncClient(
            transport=ASGITransport(manager.app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client,
    ):
        response = await client.get("/boom")

    assert response.status_code == 500
    assert "secret" not in response.text
    assert response.json()["error"] == {
        "code": "internal_error",
        "message": "internal server error",
        "request_id": response.headers["X-Request-ID"],
    }
