"""Process-wide resources, created once at startup and closed at shutdown."""

import asyncio
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Protocol

from dotenv import dotenv_values
from fastapi import FastAPI
from pgvector.psycopg import register_vector_async
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool
from redis.asyncio import Redis

from provenance.api.principals import PrincipalRegistry
from provenance.config import REPO_ROOT, Settings
from provenance.retrieval.hybrid import HybridRetriever
from provenance.retrieval.types import Mode, SearchResult

log = logging.getLogger("provenance.api")

STARTUP_DB_TIMEOUT_S = 5.0


class Retriever(Protocol):
    @property
    def can_rerank(self) -> bool: ...

    @property
    def can_rewrite(self) -> bool: ...

    async def search(
        self,
        conn: AsyncConnection,
        query: str,
        k: int = ...,
        mode: Mode = ...,
        rerank: bool = ...,
        rewrite: bool = ...,
    ) -> SearchResult: ...


@dataclass(frozen=True)
class Resources:
    settings: Settings
    registry: PrincipalRegistry
    pool: AsyncConnectionPool
    redis: Redis
    retriever: Retriever | None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    registry = PrincipalRegistry.load(settings.principals_path, settings.api_keys_path)
    # Connects as the non-owner app role, so row-level security always applies.
    pool = AsyncConnectionPool(
        settings.app_dsn,
        min_size=1,
        max_size=settings.db_pool_max_size,
        open=False,
        configure=_configure_connection,
    )
    # wait=False: the API starts even if Postgres is down; /health/ready reports it.
    await pool.open(wait=False)
    redis = Redis.from_url(settings.redis_url, socket_timeout=2, socket_connect_timeout=2)
    retriever: Retriever | None = app.state.retriever
    if retriever is None and settings.load_models:
        retriever = await build_retriever(pool)
    app.state.resources = Resources(settings, registry, pool, redis, retriever)
    try:
        yield
    finally:
        await redis.aclose()
        await pool.close()


async def _configure_connection(conn: AsyncConnection) -> None:
    await register_vector_async(conn)
    await conn.commit()  # registration queries opened a transaction; return the conn idle


async def build_retriever(pool: AsyncConnectionPool) -> HybridRetriever:
    """Loads the CPU models (slow: seconds, plus a one-time download) and, if an LLM key and
    the company list are available, the query rewriter."""
    from provenance.llm.factory import build_router, load_config
    from provenance.retrieval.embeddings import Embedder
    from provenance.retrieval.rerank import Reranker
    from provenance.retrieval.rewrite import QueryRewriter

    embedder = await asyncio.to_thread(Embedder, threads=os.cpu_count() or 4)
    reranker = await asyncio.to_thread(Reranker)
    rewriter = None
    try:
        dotenv = {k: v for k, v in dotenv_values(REPO_ROOT / ".env").items() if v is not None}
        env = {**dotenv, **os.environ}
        router = build_router(load_config(REPO_ROOT / "config" / "llm.yaml"), env)
        async with pool.connection(timeout=STARTUP_DB_TIMEOUT_S) as conn:
            cur = await conn.execute("SELECT ticker, name FROM companies")
            companies = {t: n for t, n in await cur.fetchall()}
        if companies:
            rewriter = QueryRewriter(router, companies)
    except Exception as e:
        log.warning("query rewriting disabled: %s", type(e).__name__)
    return HybridRetriever(embedder, reranker, rewriter)
