"""Per-request accounting of model calls: tokens, latency and API-equivalent cost.

A `MeteredLLM` wraps the shared router for one request and records every call it makes.
Graph nodes set `current_node` when they start, and because each node runs in its own
asyncio task (which copies the context), calls are attributed to the right node even when
search and SQL run in parallel.
"""

from collections.abc import Callable
from contextvars import ContextVar
from typing import Protocol

from pydantic import BaseModel, Field, computed_field

from provenance.llm.types import ChatRequest, ChatResponse, Usage

current_node: ContextVar[str] = ContextVar("provenance_llm_node", default="-")

CostFn = Callable[[str, Usage], float]


class Completer(Protocol):
    async def complete(self, role: str, request: ChatRequest) -> ChatResponse: ...


class LLMCall(BaseModel):
    node: str
    role: str
    provider: str
    model: str
    input_tokens: int
    cached_input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_usd: float


class RunUsage(BaseModel):
    calls: list[LLMCall] = Field(default_factory=list)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def input_tokens(self) -> int:
        return sum(c.input_tokens for c in self.calls)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def output_tokens(self) -> int:
        return sum(c.output_tokens for c in self.calls)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cached_input_tokens(self) -> int:
        return sum(c.cached_input_tokens for c in self.calls)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cost_usd(self) -> float:
        return round(sum(c.cost_usd for c in self.calls), 6)

    @property
    def tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def merged(self, other: "RunUsage") -> "RunUsage":
        return RunUsage(calls=[*self.calls, *other.calls])


class MeteredLLM:
    """Records each successful call. Failed calls cost nothing on free tiers and carry no
    usage, so they're visible in the router's attempts instead."""

    def __init__(self, inner: Completer, cost: CostFn) -> None:
        self._inner = inner
        self._cost = cost
        self.usage = RunUsage()

    async def complete(self, role: str, request: ChatRequest) -> ChatResponse:
        response = await self._inner.complete(role, request)
        self.usage.calls.append(
            LLMCall(
                node=current_node.get(),
                role=role,
                provider=response.provider,
                model=response.model,
                input_tokens=response.usage.input_tokens,
                cached_input_tokens=response.usage.cached_input_tokens,
                output_tokens=response.usage.output_tokens,
                latency_ms=round(response.latency_ms, 1),
                cost_usd=round(self._cost(role, response.usage), 8),
            )
        )
        return response
