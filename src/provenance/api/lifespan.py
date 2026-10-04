"""Process-wide resources, created once at startup and closed at shutdown."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import FastAPI
from psycopg_pool import AsyncConnectionPool
from redis.asyncio import Redis

from provenance.api.principals import PrincipalRegistry
from provenance.config import Settings


@dataclass(frozen=True)
class Resources:
    settings: Settings
    registry: PrincipalRegistry
    pool: AsyncConnectionPool
    redis: Redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    registry = PrincipalRegistry.load(settings.principals_path, settings.api_keys_path)
    # Connects as the non-owner app role, so row-level security always applies.
    pool = AsyncConnectionPool(
        settings.app_dsn, min_size=1, max_size=settings.db_pool_max_size, open=False
    )
    # wait=False: the API starts even if Postgres is down; /health/ready reports it.
    await pool.open(wait=False)
    redis = Redis.from_url(settings.redis_url, socket_timeout=2, socket_connect_timeout=2)
    app.state.resources = Resources(settings, registry, pool, redis)
    try:
        yield
    finally:
        await redis.aclose()
        await pool.close()
