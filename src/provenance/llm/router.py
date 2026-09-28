import asyncio
import time
from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Protocol

from pydantic import BaseModel

from provenance.llm.breaker import CircuitBreaker
from provenance.llm.errors import (
    AllProvidersFailed,
    ProviderRejected,
    ProviderUnavailable,
    RateLimited,
)
from provenance.llm.types import Attempt, ChatRequest, ChatResponse

_AUTH_FAILURE_COOLDOWN_S = 3600.0


class Provider(Protocol):
    name: str

    async def complete(self, request: ChatRequest, model: str) -> ChatResponse: ...


class ModelChoice(BaseModel):
    provider: str
    model: str


class LLMRouter:
    """Serves a role (e.g. "serve_small") from an ordered chain of provider+model choices.

    Per choice: skip if its breaker is open; retry transient failures with exponential
    backoff; on a rate limit, open the breaker for the provider's own retry delay and move
    on; on a rejection, move on without retrying. Breakers are per provider+model because
    free-tier quotas and overloads are per model; an auth failure (one bad key) instead
    blocks the whole provider for an hour. Every attempt is recorded for the audit trail.
    """

    def __init__(
        self,
        providers: Mapping[str, Provider],
        roles: Mapping[str, Sequence[ModelChoice]],
        now: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        max_retries: int = 2,
        backoff_base_s: float = 0.5,
    ) -> None:
        self._providers = providers
        self._roles = roles
        self._sleep = sleep
        self._max_retries = max_retries
        self._backoff_base_s = backoff_base_s
        self._now = now
        self._model_breakers: dict[tuple[str, str], CircuitBreaker] = {}
        self._auth_breakers = {name: CircuitBreaker(now=now) for name in providers}

    def chain(self, role: str) -> list[tuple[str, str]]:
        return [(c.provider, c.model) for c in self._roles[role]]

    async def complete(self, role: str, request: ChatRequest) -> ChatResponse:
        if role not in self._roles:
            raise KeyError(f"unknown LLM role '{role}'")
        attempts: list[Attempt] = []
        for choice in self._roles[role]:
            response = await self._try_choice(choice, request, attempts)
            if response is not None:
                return response.model_copy(update={"attempts": attempts})
        raise AllProvidersFailed(role, attempts)

    async def _try_choice(
        self, choice: ModelChoice, request: ChatRequest, attempts: list[Attempt]
    ) -> ChatResponse | None:
        auth = self._auth_breakers[choice.provider]
        breaker = self._model_breakers.setdefault(
            (choice.provider, choice.model), CircuitBreaker(now=self._now)
        )
        provider = self._providers[choice.provider]
        for gate in (auth, breaker):
            if not gate.allow():
                wait = gate.seconds_until_available()
                attempts.append(_attempt(choice, "breaker_open", f"available in {wait:.0f}s"))
                return None

        for retry in range(self._max_retries + 1):
            started = time.perf_counter()
            try:
                response = await provider.complete(request, choice.model)
            except RateLimited as e:
                breaker.trip(e.retry_after_s)
                attempts.append(_attempt(choice, "rate_limited", str(e), started))
                return None
            except ProviderRejected as e:
                if e.status in (401, 403):
                    auth.trip(_AUTH_FAILURE_COOLDOWN_S)
                attempts.append(_attempt(choice, "rejected", str(e), started))
                return None
            except ProviderUnavailable as e:
                breaker.record_failure()
                attempts.append(_attempt(choice, "unavailable", str(e), started))
                if retry < self._max_retries and breaker.allow():
                    await self._sleep(self._backoff_base_s * 2**retry)
                    continue
                return None
            breaker.record_success()
            attempts.append(_attempt(choice, "ok", "", started))
            return response
        return None


def _attempt(
    choice: ModelChoice, outcome: str, detail: str, started: float | None = None
) -> Attempt:
    latency = (time.perf_counter() - started) * 1000 if started is not None else 0.0
    return Attempt(
        provider=choice.provider,
        model=choice.model,
        outcome=outcome,  # type: ignore[arg-type]
        detail=detail,
        latency_ms=latency,
    )
