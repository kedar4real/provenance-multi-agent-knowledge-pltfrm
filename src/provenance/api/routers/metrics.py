"""GET /metrics: Prometheus text format. No caller identities or question text are exposed,
only counts, tokens, cost, latency, queue depth and breaker states."""

from fastapi import APIRouter
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST

from provenance.api.deps import ResourcesDep
from provenance.llm.router import LLMRouter

router = APIRouter(tags=["metrics"])


@router.get("/metrics", include_in_schema=False)
async def metrics(resources: ResourcesDep) -> Response:
    if resources.metrics is None:
        return Response(b"", media_type=CONTENT_TYPE_LATEST)
    controller = resources.controller
    queue = (controller.gate.running, controller.gate.waiting) if controller else None
    llm = resources.llm
    breakers = llm.breaker_states if isinstance(llm, LLMRouter) else None
    body = resources.metrics.render(queue, breakers)
    return Response(body, media_type=CONTENT_TYPE_LATEST)
