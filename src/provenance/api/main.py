"""The FastAPI application. Run it with `uv run python -m provenance.api`."""

import logging

from fastapi import FastAPI

from provenance.api.errors import install_error_handlers
from provenance.api.lifespan import Completer, Retriever, lifespan
from provenance.api.middleware import RequestContextMiddleware
from provenance.api.routers import health, me, query, search, sources
from provenance.config import Settings


def create_app(
    settings: Settings | None = None,
    retriever: Retriever | None = None,
    llm: Completer | None = None,
) -> FastAPI:
    """`retriever` and `llm` are for tests; by default the lifespan loads the real ones."""
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
    app.add_middleware(RequestContextMiddleware)
    install_error_handlers(app)
    app.include_router(health.router)
    app.include_router(me.router)
    app.include_router(search.router)
    app.include_router(sources.router)
    app.include_router(query.router)
    return app
