"""Ask a question; the controller's and agent's steps stream back as Server-Sent Events.

  event: step     one per finished step (route, cache, plan, search, sql, write, verify,
                  revise, score, escalate, abstain)
  event: result   the final answer with its evidence, trace and controller report
  event: error    the run failed or was shed; details are logged, not sent

Authentication, the daily budget (429) and a full queue (503) are checked before the stream
starts, so they're ordinary HTTP errors. Each worker opens its own principal-scoped
connection inside the stream instead of holding a request transaction open for the run.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from psycopg import AsyncConnection
from pydantic import BaseModel, Field

from provenance.agents.graph import AgentDeps
from provenance.agents.types import TraceEvent
from provenance.api.deps import PrincipalDep, ResourcesDep, principal_transaction
from provenance.api.errors import ApiError
from provenance.api.lifespan import Resources
from provenance.api.middleware import current_request_id
from provenance.api.principals import Principal
from provenance.controller.backpressure import Overloaded
from provenance.controller.executor import BudgetExhausted
from provenance.llm.metering import Completer
from provenance.security.audit import PostgresAudit
from provenance.sql.worker import SqlWorker

router = APIRouter(prefix="/v1", tags=["query"])
log = logging.getLogger("provenance.api")


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


def sse(event: str, data: str) -> str:
    return f"event: {event}\ndata: {data}\n\n"


@router.post("/query", response_class=StreamingResponse)
async def query(
    body: QueryRequest, resources: ResourcesDep, principal: PrincipalDep
) -> StreamingResponse:
    controller = resources.controller
    if controller is None:
        raise ApiError(503, "agent_unavailable", "the models or LLM keys are not loaded")
    try:
        await controller.preflight(principal.name)
    except BudgetExhausted:
        raise ApiError(
            429, "budget_exhausted", "today's token budget is spent", _seconds_to_utc_midnight()
        ) from None
    if controller.gate.full:
        if controller.metrics:
            controller.metrics.shed.labels("queue_full").inc()
        raise ApiError(
            503, "overloaded", "too many questions in flight; retry shortly",
            int(controller.policy.backpressure.wait_timeout_s),
        )  # fmt: skip
    request_id = current_request_id()

    def make_deps(llm: Completer) -> AgentDeps:
        return _deps(resources, principal, llm)

    async def events() -> AsyncIterator[str]:
        try:
            async for item in controller.run(
                body.question, principal.name, principal.groups, make_deps
            ):
                kind = "step" if isinstance(item, TraceEvent) else "result"
                yield sse(kind, item.model_dump_json())
        except Overloaded as e:
            if controller.metrics:
                controller.metrics.shed.labels(e.reason).inc()
            yield sse("error", '{"code": "overloaded", "message": "the queue timed out"}')
        except Exception:
            log.exception("agent run failed id=%s", request_id)
            yield sse("error", '{"code": "agent_failed", "message": "the agent run failed"}')

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _seconds_to_utc_midnight() -> int:
    now = datetime.now(UTC)
    midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return max(1, int((midnight - now).total_seconds()))


def _deps(resources: Resources, principal: Principal, llm: Completer) -> AgentDeps:
    """`llm` is the per-request metered wrapper, so every call is counted."""
    assert resources.retriever is not None

    @asynccontextmanager
    async def sql_connection() -> AsyncIterator[AsyncConnection]:
        async with resources.sql_pool.connection(timeout=5) as conn:
            yield conn

    return AgentDeps(
        llm=llm,
        searcher=resources.retriever,
        sql_worker=SqlWorker(llm, resources.settings.rls_signing_key.get_secret_value()),
        search_connection=lambda: principal_transaction(resources, principal),
        sql_connection=sql_connection,
        scorer=resources.scorer,
        audit=PostgresAudit(resources.pool),
        principal=principal.name,
        request_id=current_request_id(),
    )
