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
from provenance.controller.backpressure import Gate
from provenance.controller.budget import RedisBudgetStore
from provenance.controller.cache import AnswerCache, RedisCacheStore
from provenance.controller.executor import Controller
from provenance.controller.metrics import Metrics
from provenance.controller.policy import Policy
from provenance.llm.metering import CostFn
from provenance.llm.router import LLMRouter
from provenance.llm.types import ChatRequest, ChatResponse
from provenance.retrieval.hybrid import HybridRetriever
from provenance.retrieval.types import Mode, SearchResult
from provenance.verifier.scorer import ClaimScorer

log = logging.getLogger("provenance.api")

STARTUP_DB_TIMEOUT_S = 5.0


class Completer(Protocol):
    async def complete(self, role: str, request: ChatRequest) -> ChatResponse: ...


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
    # The read-only SQL role, for the agent's SQL worker. RLS applies to it too.
    sql_pool: AsyncConnectionPool
    llm: Completer | None
    scorer: ClaimScorer | None = None
    # M8: routing, escalation, abstention, answer cache, budgets and backpressure. None
    # when the agent can't run (no models or keys).
    controller: Controller | None = None
    metrics: Metrics | None = None


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
    sql_pool = AsyncConnectionPool(settings.sql_ro_dsn, min_size=0, max_size=4, open=False)
    await sql_pool.open(wait=False)
    llm: Completer | None = app.state.llm
    if llm is None and settings.load_models:
        llm = load_router()
    retriever: Retriever | None = app.state.retriever
    if retriever is None and settings.load_models:
        retriever = await build_retriever(pool, llm)
    scorer: ClaimScorer | None = app.state.scorer
    if scorer is None and settings.load_models:
        scorer = await asyncio.to_thread(build_scorer)
    policy: Policy = app.state.policy or Policy.load(settings.routing_path)
    metrics = Metrics()
    controller = None
    if llm is not None and retriever is not None:
        cache = None
        if isinstance(retriever, HybridRetriever):
            cache = AnswerCache(RedisCacheStore(redis), retriever.embed_question, policy.cache)
        controller = Controller(
            policy=policy,
            llm=llm,
            cost=load_pricing(),
            gate=Gate(policy.backpressure),
            cache=cache,
            budgets=RedisBudgetStore(redis),
            metrics=metrics,
        )
    app.state.resources = Resources(
        settings, registry, pool, redis, retriever, sql_pool, llm, scorer, controller, metrics
    )
    try:
        yield
    finally:
        await redis.aclose()
        await sql_pool.close()
        await pool.close()


async def _configure_connection(conn: AsyncConnection) -> None:
    await register_vector_async(conn)
    await conn.commit()  # registration queries opened a transaction; return the conn idle


def build_scorer() -> ClaimScorer:
    """The NLI model plus the fitted calibrator, if eval.calibration_eval has produced one;
    without it, claims are scored but carry no confidence."""
    from provenance.verifier.calibration import CalibratorParams
    from provenance.verifier.nli import NliModel

    path = REPO_ROOT / "config" / "calibration.json"
    calibrator = CalibratorParams.load(path) if path.exists() else None
    if calibrator is None:
        log.warning("no %s yet: answers will carry no confidence", path.name)
    return ClaimScorer(NliModel(), calibrator)


def load_pricing() -> CostFn:
    """API-equivalent cost per call from config/llm.yaml's reference price classes; zero
    for roles it doesn't know (e.g. scripted test models)."""
    from provenance.llm.factory import api_equivalent_cost_usd, load_config
    from provenance.llm.types import Usage

    config = load_config(REPO_ROOT / "config" / "llm.yaml")

    def cost(role: str, usage: Usage) -> float:
        return api_equivalent_cost_usd(config, role, usage) if role in config.roles else 0.0

    return cost


def load_router() -> LLMRouter | None:
    """The LLM router from config/llm.yaml and the provider keys in .env; None without keys."""
    from provenance.llm.factory import build_router, load_config

    try:
        dotenv = {k: v for k, v in dotenv_values(REPO_ROOT / ".env").items() if v is not None}
        return build_router(
            load_config(REPO_ROOT / "config" / "llm.yaml"), {**dotenv, **os.environ}
        )
    except Exception as e:
        log.warning("LLM features disabled: %s", type(e).__name__)
        return None


async def build_retriever(pool: AsyncConnectionPool, llm: Completer | None) -> HybridRetriever:
    """Loads the CPU models (seconds; a one-time download on first run) and, if an LLM and
    the company list are available, the query rewriter."""
    from provenance.retrieval.embeddings import Embedder
    from provenance.retrieval.rerank import Reranker
    from provenance.retrieval.rewrite import QueryRewriter

    embedder = await asyncio.to_thread(Embedder, threads=os.cpu_count() or 4)
    reranker = await asyncio.to_thread(Reranker)
    rewriter = None
    if llm is not None:
        try:
            async with pool.connection(timeout=STARTUP_DB_TIMEOUT_S) as conn:
                cur = await conn.execute("SELECT ticker, name FROM companies")
                companies = {t: n for t, n in await cur.fetchall()}
            if companies:
                rewriter = QueryRewriter(llm, companies)
        except Exception as e:
            log.warning("query rewriting disabled: %s", type(e).__name__)
    return HybridRetriever(embedder, reranker, rewriter)
