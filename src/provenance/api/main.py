"""The FastAPI application. Run it with `uv run python -m provenance.api`."""

import logging

from fastapi import FastAPI

from provenance.api.errors import install_error_handlers
from provenance.api.lifespan import Completer, Retriever, lifespan
from provenance.api.middleware import RequestContextMiddleware
from provenance.api.routers import health, me, metrics, query, search, sources
from provenance.config import Settings
from provenance.controller.policy import Policy
from provenance.verifier.scorer import ClaimScorer


def create_app(
    settings: Settings | None = None,
    retriever: Retriever | None = None,
    llm: Completer | None = None,
    scorer: ClaimScorer | None = None,
    policy: Policy | None = None,
) -> FastAPI:
    """`retriever`, `llm`, `scorer` and `policy` are for tests; the lifespan loads the real
    ones (the policy from config/routing.yaml)."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    app = FastAPI(
        title="provenance",
        version="0.1.0",
        summary="Permission-aware, cited answers over SEC 10-K filings.",
        lifespan=lifespan,
    )
    app.state.settings = settings or Settings()
    app.state.retriever = retriever
    app.state.llm = llm
    app.state.scorer = scorer
    app.state.policy = policy
    app.state.tracer_provider = None
    endpoint = app.state.settings.otel_exporter_otlp_endpoint
    if endpoint:  # traces to Jaeger (docker compose --profile observability)
        from provenance.telemetry.otel import setup_tracing

        app.state.tracer_provider = setup_tracing(app, endpoint)
    app.add_middleware(RequestContextMiddleware)
    install_error_handlers(app)
    app.include_router(health.router)
    app.include_router(me.router)
    app.include_router(search.router)
    app.include_router(sources.router)
    app.include_router(query.router)
    app.include_router(metrics.router)
    return app
