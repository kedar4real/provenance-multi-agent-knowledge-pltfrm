from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from pydantic import SecretStr

from provenance.api.main import create_app
from provenance.config import Settings

PRINCIPALS_YAML = """
principals:
  ana_tech:
    display_name: Ana
    groups: [analyst_tech]
  rhea_research:
    display_name: Rhea
    groups: [research_all]
"""


@pytest.fixture
def principals_path(tmp_path: Path) -> Path:
    path = tmp_path / "principals.yaml"
    path.write_text(PRINCIPALS_YAML, encoding="utf-8")
    return path


@pytest.fixture
def offline_settings(principals_path: Path, tmp_path: Path) -> Settings:
    """Points at ports nothing listens on: these tests never need a live database."""
    return Settings(
        app_dsn="postgresql://nobody:x@127.0.0.1:1/none?connect_timeout=1",
        redis_url="redis://127.0.0.1:1/0",
        rls_signing_key=SecretStr("unit-test-key"),
        principals_path=principals_path,
        api_keys_path=tmp_path / "api_keys.json",
        load_models=False,
    )


@pytest.fixture
async def client(offline_settings: Settings) -> AsyncIterator[AsyncClient]:
    app = create_app(offline_settings)
    async with (
        LifespanManager(app) as manager,
        AsyncClient(transport=ASGITransport(manager.app), base_url="http://test") as c,
    ):
        yield c
