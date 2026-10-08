"""Prometheus metrics for the controller, served at GET /metrics.

Each app gets its own registry (tests build many apps; the global one would refuse the
duplicate names). Breaker and queue gauges are read at scrape time, so they're never stale.
"""

import time
from collections import defaultdict
from collections.abc import Callable

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel

from provenance.llm.metering import RunUsage


class MetricsSnapshot(BaseModel):
    """The counters as plain numbers, for the dashboard (GET /v1/stats)."""

    started_at: float  # epoch seconds: counts are since this process started
    queries: dict[str, dict[str, float]]  # outcome -> tier -> count
    cache_lookups: dict[str, float]  # kind -> count
    escalations: dict[str, float]  # reason -> count
    tokens: dict[str, dict[str, float]]  # role -> kind (input, cached_input, output) -> count
    cost_usd: dict[str, float]  # role -> API-equivalent dollars
    latency_buckets: list[tuple[float, float]]  # (upper bound in s, cumulative count)
    latency_sum_s: float
    shed: dict[str, float]  # reason -> count
    running: int
    waiting: int


class Metrics:
    def __init__(self) -> None:
        self.started_at = time.time()
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

    def snapshot(self, queue: tuple[int, int] = (0, 0)) -> MetricsSnapshot:
        nested: dict[str, dict[str, dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
        flat: dict[str, dict[str, float]] = defaultdict(dict)
        buckets: dict[float, float] = defaultdict(float)
        latency_sum = 0.0
        for family in self.registry.collect():
            for sample in family.samples:
                name, labels, value = sample.name, sample.labels, sample.value
                if name == "provenance_queries_total":
                    nested["queries"][labels["outcome"]][labels["tier"]] = value
                elif name == "provenance_llm_tokens_total":
                    nested["tokens"][labels["role"]][labels["kind"]] = value
                elif name == "provenance_cache_lookups_total":
                    flat["cache"][labels["kind"]] = value
                elif name == "provenance_escalations_total":
                    flat["escalations"][labels["reason"]] = value
                elif name == "provenance_llm_api_equivalent_cost_usd_total":
                    flat["cost"][labels["role"]] = value
                elif name == "provenance_requests_shed_total":
                    flat["shed"][labels["reason"]] = value
                elif name == "provenance_query_seconds_bucket":
                    # Summed over outcomes: one latency distribution for the dashboard.
                    buckets[float(labels["le"])] += value
                elif name == "provenance_query_seconds_sum":
                    latency_sum += value
        return MetricsSnapshot(
            started_at=self.started_at,
            queries={k: dict(v) for k, v in nested["queries"].items()},
            cache_lookups=dict(flat["cache"]),
            escalations=dict(flat["escalations"]),
            tokens={k: dict(v) for k, v in nested["tokens"].items()},
            cost_usd=dict(flat["cost"]),
            latency_buckets=sorted(buckets.items()),
            latency_sum_s=latency_sum,
            shed=dict(flat["shed"]),
            running=queue[0],
            waiting=queue[1],
        )
