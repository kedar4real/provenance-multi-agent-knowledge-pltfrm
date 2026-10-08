"""Bounded concurrency and per-request LLM metering."""

import asyncio

import pytest

from provenance.controller.backpressure import Gate, Overloaded
from provenance.controller.metrics import Metrics
from provenance.controller.policy import BackpressureConfig
from provenance.llm.metering import LLMCall, MeteredLLM, RunUsage, current_node
from provenance.llm.types import ChatRequest, ChatResponse, Message, Usage


async def test_runs_beyond_the_limit_queue_and_beyond_the_queue_are_shed() -> None:
    gate = Gate(BackpressureConfig(max_concurrent=1, max_waiting=1, wait_timeout_s=5))
    release = asyncio.Event()

    async def run() -> None:
        async with gate.slot():
            await release.wait()

    first = asyncio.create_task(run())
    await asyncio.sleep(0)
    second = asyncio.create_task(run())  # queues
    await asyncio.sleep(0)
    assert (gate.running, gate.waiting) == (1, 1) and gate.full

    with pytest.raises(Overloaded) as shed:
        await gate.acquire()
    assert shed.value.reason == "queue_full"

    release.set()
    await asyncio.gather(first, second)
    assert (gate.running, gate.waiting) == (0, 0) and not gate.full


async def test_a_queued_run_gives_up_after_the_wait_timeout() -> None:
    gate = Gate(BackpressureConfig(max_concurrent=1, max_waiting=4, wait_timeout_s=0.05))
    await gate.acquire()

    with pytest.raises(Overloaded) as timed_out:
        await gate.acquire()

    assert timed_out.value.reason == "queue_timeout" and gate.waiting == 0
    gate.release()


class FixedLLM:
    async def complete(self, role: str, request: ChatRequest) -> ChatResponse:
        await asyncio.sleep(0)
        usage = Usage(input_tokens=1000, output_tokens=100, cached_input_tokens=400)
        return ChatResponse(content="ok", provider="p", model="m", usage=usage, latency_ms=5)


REQUEST = ChatRequest(messages=[Message(role="user", content="hi")])


async def test_calls_are_costed_and_attributed_to_the_node_that_made_them() -> None:
    meter = MeteredLLM(FixedLLM(), lambda role, u: 0.01 if role == "large" else 0.001)

    async def node(name: str, role: str) -> None:
        current_node.set(name)  # each task gets its own copy of the context
        await meter.complete(role, REQUEST)

    await asyncio.gather(node("search", "small"), node("sql", "large"))

    by_node = {c.node: c for c in meter.usage.calls}
    assert by_node["search"].role == "small" and by_node["sql"].role == "large"
    assert meter.usage.input_tokens == 2000 and meter.usage.cached_input_tokens == 800
    assert meter.usage.tokens == 2200 and meter.usage.cost_usd == pytest.approx(0.011)
    assert current_node.get() == "-"  # the caller's context is untouched


def test_the_metrics_snapshot_reports_counts_tokens_cost_and_latency() -> None:
    metrics = Metrics()
    call = LLMCall(
        node="write", role="serve_small", provider="p", model="m", input_tokens=100,
        cached_input_tokens=0, output_tokens=20, latency_ms=5, cost_usd=0.002,
    )  # fmt: skip
    metrics.observe_run("answered", "small", 3.0, RunUsage(calls=[call]))
    metrics.observe_run("cache_hit", "small", 0.1, RunUsage())
    metrics.cache_lookups.labels("semantic").inc()

    snap = metrics.snapshot(queue=(1, 2))

    assert snap.queries == {"answered": {"small": 1.0}, "cache_hit": {"small": 1.0}}
    assert snap.tokens["serve_small"]["input"] == 100
    assert snap.cost_usd == {"serve_small": pytest.approx(0.002)}
    assert snap.cache_lookups == {"semantic": 1.0}
    assert dict(snap.latency_buckets)[5.0] == 2  # cumulative: both runs took <= 5 s
    assert dict(snap.latency_buckets)[1.0] == 1
    assert snap.latency_sum_s == pytest.approx(3.1)
    assert (snap.running, snap.waiting) == (1, 2)
