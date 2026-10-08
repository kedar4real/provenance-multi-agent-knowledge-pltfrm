"""GET /v1/stats: the controller's counters as JSON for the dashboard, plus the caller's own
token budget. Aggregates only (no identities or question text), counted since the API
process started; /metrics serves the same numbers to Prometheus."""

from fastapi import APIRouter
from pydantic import BaseModel

from provenance.api.deps import PrincipalDep, ResourcesDep
from provenance.controller.metrics import MetricsSnapshot
from provenance.llm.router import LLMRouter

router = APIRouter(prefix="/v1", tags=["stats"])


class Budget(BaseModel):
    spent: int
    limit: int


class Stats(BaseModel):
    metrics: MetricsSnapshot | None
    budget: Budget | None
    breakers_open: list[str]


@router.get("/stats")
async def stats(principal: PrincipalDep, resources: ResourcesDep) -> Stats:
    controller = resources.controller
    snapshot = None
    if resources.metrics is not None:
        queue = (controller.gate.running, controller.gate.waiting) if controller else (0, 0)
        snapshot = resources.metrics.snapshot(queue)
    budget = None
    if controller is not None and controller.budgets is not None:
        try:
            spent = await controller.budgets.spent(principal.name)
            budget = Budget(spent=spent, limit=controller.policy.budgets.principal_daily_tokens)
        except Exception:  # Redis down: the dashboard just omits the budget
            budget = None
    llm = resources.llm
    open_breakers = (
        [f"{p}/{m}" for p, m, is_open in llm.breaker_states() if is_open]
        if isinstance(llm, LLMRouter)
        else []
    )
    return Stats(metrics=snapshot, budget=budget, breakers_open=open_breakers)
