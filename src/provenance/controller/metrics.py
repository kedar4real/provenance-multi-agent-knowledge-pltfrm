"""Prometheus metrics for the controller, served at GET /metrics.

Each app gets its own registry (tests build many apps; the global one would refuse the
duplicate names). Breaker and queue gauges are read at scrape time, so they're never stale.
"""

from collections.abc import Callable

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest

from provenance.llm.metering import RunUsage


class Metrics:
    def __init__(self) -> None:
        self.registry = CollectorRegistry()
        r = self.registry
        self.queries = Counter(
            "provenance_queries", "Questions answered, by outcome and tier",
            ["outcome", "tier"], registry=r,
        )  # fmt: skip
        self.escalations = Counter(
            "provenance_escalations", "Small-tier answers redone on the large tier",
            ["reason"], registry=r,
        )  # fmt: skip
        self.cache_lookups = Counter(
            "provenance_cache_lookups", "Answer-cache lookups by result", ["kind"], registry=r
        )
        self.tokens = Counter(
            "provenance_llm_tokens", "LLM tokens by role and kind", ["role", "kind"], registry=r
        )
        self.cost = Counter(
            "provenance_llm_api_equivalent_cost_usd",
            "API-equivalent cost at reference list prices (real calls are free tier)",
            ["role"], registry=r,
        )  # fmt: skip
        self.latency = Histogram(
            "provenance_query_seconds", "End-to-end question latency", ["outcome"],
            buckets=(0.05, 0.25, 1, 2.5, 5, 10, 20, 40, 80), registry=r,
        )  # fmt: skip
        self.shed = Counter(
            "provenance_requests_shed", "Requests refused by backpressure or budgets",
            ["reason"], registry=r,
        )  # fmt: skip
        self.running = Gauge("provenance_runs_in_flight", "Agent runs executing", registry=r)
        self.waiting = Gauge("provenance_runs_waiting", "Agent runs queued", registry=r)
        self.breaker_open = Gauge(
            "provenance_llm_breaker_open", "1 while a provider+model circuit breaker is open",
            ["provider", "model"], registry=r,
        )  # fmt: skip

    def observe_run(self, outcome: str, tier: str, seconds: float, usage: RunUsage) -> None:
        self.queries.labels(outcome, tier).inc()
        self.latency.labels(outcome).observe(seconds)
        for call in usage.calls:
            self.tokens.labels(call.role, "input").inc(call.input_tokens)
            self.tokens.labels(call.role, "cached_input").inc(call.cached_input_tokens)
            self.tokens.labels(call.role, "output").inc(call.output_tokens)
            self.cost.labels(call.role).inc(call.cost_usd)

    def render(
        self,
        queue: tuple[int, int] | None = None,
        breakers: Callable[[], list[tuple[str, str, bool]]] | None = None,
    ) -> bytes:
        if queue is not None:
            self.running.set(queue[0])
            self.waiting.set(queue[1])
        if breakers is not None:
            for provider, model, is_open in breakers():
                self.breaker_open.labels(provider, model).set(1 if is_open else 0)
        return generate_latest(self.registry)
