"""Ask a question; the agent's steps stream back as Server-Sent Events, then the answer.

  event: step     one per finished step (plan, search, sql, write, verify, revise)
  event: result   the final answer with its evidence and trace
  event: error    the run failed; details are logged, not sent

Authentication happens before the stream starts, so a bad key is a normal 401. Each worker
opens its own principal-scoped connection inside the stream instead of holding a request
transaction open for the whole run.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from psycopg import AsyncConnection
from pydantic import BaseModel, Field

from provenance.agents.graph import AgentDeps, build_graph, run_agent
from provenance.agents.types import TraceEvent
from provenance.api.deps import PrincipalDep, ResourcesDep, principal_transaction
from provenance.api.errors import ApiError
from provenance.api.lifespan import Resources
from provenance.api.middleware import current_request_id
from provenance.api.principals import Principal
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
    if resources.retriever is None or resources.llm is None:
        raise ApiError(503, "agent_unavailable", "the models or LLM keys are not loaded")
    graph = build_graph(_deps(resources, principal))
    request_id = current_request_id()

    async def events() -> AsyncIterator[str]:
        try:
            async for item in run_agent(graph, body.question, principal.groups):
                kind = "step" if isinstance(item, TraceEvent) else "result"
                yield sse(kind, item.model_dump_json())
        except Exception:
            log.exception("agent run failed id=%s", request_id)
            yield sse("error", '{"code": "agent_failed", "message": "the agent run failed"}')

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _deps(resources: Resources, principal: Principal) -> AgentDeps:
    assert resources.llm is not None and resources.retriever is not None

    @asynccontextmanager
    async def sql_connection() -> AsyncIterator[AsyncConnection]:
        async with resources.sql_pool.connection(timeout=5) as conn:
            yield conn

    return AgentDeps(
        llm=resources.llm,
        searcher=resources.retriever,
        sql_worker=SqlWorker(resources.llm, resources.settings.rls_signing_key.get_secret_value()),
        search_connection=lambda: principal_transaction(resources, principal),
        sql_connection=sql_connection,
    )
