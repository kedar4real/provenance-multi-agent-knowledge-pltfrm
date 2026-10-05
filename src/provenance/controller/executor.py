"""The controller: the I/O around the agent run, driven by the pure decisions in policy.py.

  queue slot -> route (classifier) -> answer cache -> agent run on the chosen tier
    -> escalate to the large tier? -> abstain? -> spend budget, cache, metrics -> result

The verifier measures and the controller decides: the agent never chooses its own model,
retries or budget. Every decision is streamed as a step with its reason.
"""

import json
import logging
import time
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass
from typing import Any

from provenance.agents.graph import AgentDeps, build_graph, run_agent
from provenance.agents.types import AgentResult, ControlReport, TraceEvent
from provenance.agents.verify import DECLINE
from provenance.controller.backpressure import Gate
from provenance.controller.budget import BudgetStore
from provenance.controller.cache import AnswerCache, CacheLookup
from provenance.controller.classifier import classify
from provenance.controller.metrics import Metrics
from provenance.controller.policy import (
    Policy,
    RunFacts,
    Tier,
    check_budget,
    escalation_fits,
    select_tier,
    should_abstain,
    should_escalate,
)
from provenance.llm.metering import Completer, CostFn, MeteredLLM, RunUsage
from provenance.security.pii import redact

log = logging.getLogger("provenance.controller")

ABSTAIN_MESSAGE = (
    "I can't answer this reliably. The evidence I found doesn't support a confident "
    "answer; the sources are listed below so you can check them yourself."
)


class BudgetExhausted(Exception):
    def __init__(self, principal: str) -> None:
        super().__init__(f"daily token budget spent for {principal}")


DepsFactory = Callable[[Completer], AgentDeps]


@dataclass
class Controller:
    policy: Policy
    llm: Completer
    cost: CostFn
    gate: Gate
    cache: AnswerCache | None = None
    budgets: BudgetStore | None = None
    metrics: Metrics | None = None

    async def preflight(self, principal: str) -> int | None:
        """Tokens left today; raises BudgetExhausted. Called before the stream starts so a
        spent budget is an ordinary HTTP 429."""
        if self.budgets is None:
            return None
        try:
            spent = await self.budgets.spent(principal)
        except Exception as e:  # Redis down: answer anyway (free tiers cap the real spend)
            log.warning("budget check skipped: %s", type(e).__name__)
            return None
        left = check_budget(spent, self.policy.budgets.principal_daily_tokens)
        if left <= 0:
            if self.metrics:
                self.metrics.shed.labels("budget").inc()
            raise BudgetExhausted(principal)
        return left

    async def run(
        self, question: str, principal: str, groups: list[str], make_deps: DepsFactory
    ) -> AsyncIterator[TraceEvent | AgentResult]:
        started = time.perf_counter()
        # Redacted once, up front: the classifier, cache keys and models never see raw PII.
        question = redact(question).text
        async with self.gate.slot():
            classification = classify(question)
            tier, reasons = select_tier(classification, self.policy)
            route = _event("route", _ms(started), {
                "tier": tier, "reasons": reasons,
                "entities": classification.entities.model_dump(),
            })  # fmt: skip
            yield route
            trace = [route]

            cached = await self._cached(question, groups, tier, reasons, route, started)
            if isinstance(cached, AgentResult):
                yield cached.trace[-1]
                yield cached
                return
            lookup = cached
            if lookup is not None:
                event = _event("cache", lookup.ms, lookup.model_dump())
                yield event
                trace.append(event)

            meter = MeteredLLM(self.llm, self.cost)
            deps = make_deps(meter)
            result = None
            async for item in run_agent(build_graph(deps), question, groups, tier=tier):
                if isinstance(item, AgentResult):
                    result = item
                else:
                    yield item  # streamed live, step by step
            assert result is not None
            trace += result.trace

            escalated = should_escalate(_facts(result, meter), self.policy)
            if escalated and not escalation_fits(_facts(result, meter), self.policy):
                event = _event("escalate", 0.0, {"reason": escalated, "skipped": "budget"})
                yield event
                trace.append(event)
                escalated = None
            if escalated:
                event = _event("escalate", 0.0, {"reason": escalated, "to": "large"})
                yield event
                trace.append(event)
                if self.metrics:
                    self.metrics.escalations.labels(escalated).inc()
                redo = None
                async for item in run_agent(
                    build_graph(deps, entry="write"), question, groups, tier="large",
                    carried=_carry(result),
                ):  # fmt: skip
                    if isinstance(item, AgentResult):
                        redo = item
                    else:
                        yield item
                assert redo is not None
                trace += redo.trace
                result = redo.model_copy(update={"steps": result.steps + redo.steps})

            abstained = should_abstain(_facts(result, meter), self.policy)
            if abstained:
                event = _event("abstain", 0.0, {
                    "reason": abstained, "confidence": result.confidence,
                    "threshold": self.policy.abstain.below_confidence,
                })  # fmt: skip
                yield event
                trace.append(event)
                result = result.model_copy(update={"answer": ABSTAIN_MESSAGE})

            left = None
            if self.budgets is not None:
                try:
                    spent = await self.budgets.add(principal, meter.usage.tokens)
                    left = check_budget(spent, self.policy.budgets.principal_daily_tokens)
                except Exception as e:
                    log.warning("budget not recorded: %s", type(e).__name__)
            result = result.model_copy(update={
                "trace": trace,
                "control": ControlReport(
                    tier=result.tier, tier_reasons=reasons, escalated=escalated,
                    abstained=abstained, cache=lookup, usage=meter.usage, budget_left=left,
                ),
            })  # fmt: skip
            if self.cache is not None and _cacheable(result):
                try:
                    await self.cache.store(question, groups, _payload(question, result))
                except Exception as e:
                    log.warning("answer not cached: %s", type(e).__name__)
            self._observe(result, started)
            yield result

    async def _cached(
        self,
        question: str,
        groups: list[str],
        tier: Tier,
        reasons: list[str],
        route: TraceEvent,
        started: float,
    ) -> AgentResult | CacheLookup | None:
        if self.cache is None or not self.cache.enabled:
            return None
        try:
            payload, lookup = await self.cache.lookup(question, groups)
        except Exception as e:  # a cache outage only costs the speed-up
            log.warning("answer cache unavailable: %s", type(e).__name__)
            payload, lookup = None, CacheLookup(hit=False, kind="error")
        if self.metrics:
            self.metrics.cache_lookups.labels(lookup.kind).inc()
        if payload is None:
            return lookup
        stored = json.loads(payload)
        event = _event("cache", lookup.ms, lookup.model_dump())
        result = AgentResult.model_validate({**stored["result"], "trace": [route, event]})
        result = result.model_copy(update={
            "control": ControlReport(
                tier=result.control.tier if result.control else tier, tier_reasons=reasons,
                cache=lookup,
            ),
        })  # fmt: skip
        self._observe(result, started, outcome="cache_hit")
        return result

    def _observe(self, result: AgentResult, started: float, outcome: str | None = None) -> None:
        if self.metrics is None:
            return
        if outcome is None:
            control = result.control
            outcome = (
                "abstained" if control and control.abstained
                else "declined" if result.declined else "answered"
            )  # fmt: skip
        usage = result.control.usage if result.control else None
        self.metrics.observe_run(
            outcome, result.tier, time.perf_counter() - started,
            usage if usage is not None else RunUsage(),
        )  # fmt: skip


def _facts(result: AgentResult, meter: MeteredLLM) -> RunFacts:
    return RunFacts(
        tier="small" if result.tier == "small" else "large",
        declined=result.answer.strip() == DECLINE,
        evidence_count=len(result.evidence),
        verified=result.verification.ok if result.verification else None,
        confidence=result.confidence,
        tokens_used=meter.usage.tokens,
    )


def _carry(result: AgentResult) -> dict[str, Any]:
    """What the escalated writer reuses, so escalation never searches again."""
    return {
        "plan": result.plan,
        "passages": result.passages,
        "sql": result.sql,
        "withheld": result.withheld,
        "question_flags": result.question_flags,
    }


def _cacheable(result: AgentResult) -> bool:
    control = result.control
    degraded = any(e.detail.get("degraded") for e in result.trace)
    return (
        not result.declined
        and result.answer.strip() != DECLINE
        and control is not None
        and control.abstained is None
        and result.verification is not None
        and result.verification.ok
        and not degraded
        and not result.question_flags  # a question that looks like an attack isn't reused
    )


def _payload(question: str, result: AgentResult) -> str:
    stored = result.model_dump(mode="json", exclude={"trace"})
    return json.dumps({"question": question, "result": stored})


def _ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000, 1)


def _event(step: str, ms: float, detail: dict[str, Any]) -> TraceEvent:
    return TraceEvent(step=step, detail=detail, ms=ms)
