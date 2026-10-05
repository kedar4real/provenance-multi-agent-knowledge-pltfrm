"""The controller around a scripted agent: tiers, escalation that reuses the evidence,
abstention, the answer cache, budgets and metering."""

import json
from typing import Any, cast

import numpy as np
import pytest

from provenance.agents.graph import PLAN_PROMPT, AgentDeps
from provenance.agents.types import AgentResult, TraceEvent
from provenance.controller.backpressure import Gate
from provenance.controller.budget import MemoryBudgetStore
from provenance.controller.cache import AnswerCache, MemoryCacheStore
from provenance.controller.executor import ABSTAIN_MESSAGE, BudgetExhausted, Controller
from provenance.controller.metrics import Metrics
from provenance.controller.policy import Policy
from provenance.llm.metering import Completer
from provenance.llm.types import ChatRequest, ChatResponse, Usage
from provenance.verifier.scorer import ClaimScorer
from tests.unit.agents.test_graph import PASSAGE, FakeSearcher, FakeSql, no_connection

POLICY = Policy.model_validate({
    "tiers": {"small": {"write_roles": ["serve_small"]},
              "large": {"write_roles": ["serve_large", "serve_small"]}},
    "budgets": {"request_tokens": 30000, "principal_daily_tokens": 10000},
})  # fmt: skip
GROUPS = ["analyst_finance"]
SIMPLE = "What did JPMorgan report as net interest income?"
GOOD = "Net interest income was $95.4 billion [P1]."
INVENTED = "Net interest income was $99.9 billion [P1]."
TEXT_PLAN = {"needs_text": True, "needs_numbers": False, "sql_question": ""}


class RoleLLM:
    """Plans for the planner; otherwise answers by role, popping scripted answers."""

    def __init__(self, answers: dict[str, list[str]], tokens: int = 100) -> None:
        self.answers = answers
        self.tokens = tokens
        self.roles: list[str] = []

    async def complete(self, role: str, request: ChatRequest) -> ChatResponse:
        self.roles.append(role)
        if request.messages[0].content == PLAN_PROMPT:
            content = json.dumps(TEXT_PLAN)
        else:
            content = self.answers[role].pop(0)
        usage = Usage(input_tokens=self.tokens, output_tokens=self.tokens // 10)
        return ChatResponse(content=content, provider="f", model=role, usage=usage, latency_ms=1)


class LowConfidenceScorer:
    calibrated = True

    def score(self, answer: str, evidence: list[str], top: float | None) -> tuple[list[Any], float]:
        return [], 0.1


def embed(question: str) -> np.ndarray:
    return np.asarray([1.0, 0.0], dtype=np.float32)


def controller(llm: RoleLLM, **kwargs: Any) -> Controller:
    return Controller(
        policy=kwargs.pop("policy", POLICY), llm=llm, cost=lambda role, u: 0.001,
        gate=Gate(POLICY.backpressure), **kwargs,
    )  # fmt: skip


async def ask(
    c: Controller, question: str = SIMPLE, scorer: Any = None
) -> tuple[AgentResult, list[TraceEvent], FakeSearcher]:
    searcher = FakeSearcher([PASSAGE])

    def make_deps(llm: Completer) -> AgentDeps:
        return AgentDeps(
            llm, searcher, FakeSql([]), no_connection, no_connection,
            scorer=cast(ClaimScorer | None, scorer),
        )  # fmt: skip

    events: list[TraceEvent] = []
    result = None
    async for item in c.run(question, "ana", GROUPS, make_deps):
        if isinstance(item, AgentResult):
            result = item
        else:
            events.append(item)
    assert result is not None
    return result, events, searcher


async def test_a_simple_question_is_answered_on_the_small_tier_and_metered() -> None:
    llm = RoleLLM({"serve_small": [GOOD]})
    budgets = MemoryBudgetStore()

    result, events, _ = await ask(controller(llm, budgets=budgets))

    assert llm.roles == ["serve_small", "serve_small"]  # plan + write, no large call
    assert [e.step for e in events][:1] == ["route"]
    assert result.tier == "small" and result.control is not None
    assert result.control.tier == "small" and result.control.escalated is None
    assert [c.node for c in result.control.usage.calls] == ["plan", "write"]
    assert result.control.usage.tokens == 220 == budgets.totals["ana"]
    assert result.control.budget_left == 10000 - 220


async def test_a_complex_question_starts_on_the_large_tier() -> None:
    llm = RoleLLM({"serve_large": [GOOD]})

    result, _, _ = await ask(controller(llm), "Why did JPMorgan's net interest income grow?")

    assert llm.roles == ["serve_small", "serve_large"] and result.tier == "large"


async def test_a_failing_small_answer_escalates_without_searching_again() -> None:
    llm = RoleLLM({"serve_small": [INVENTED, INVENTED], "serve_large": [GOOD]})

    result, events, searcher = await ask(controller(llm))

    steps = [e.step for e in events]
    assert steps.index("escalate") < len(steps) - 1 and steps.count("search") == 1
    assert searcher.queries == [SIMPLE]
    assert llm.roles == ["serve_small", "serve_small", "serve_small", "serve_large"]
    assert result.answer == GOOD and result.tier == "large"
    assert result.control is not None and result.control.escalated == "failed_verification"
    assert result.verification is not None and result.verification.ok
    assert [e.step for e in result.trace] == steps  # the full story is kept in the result


async def test_escalation_is_skipped_when_over_the_request_budget() -> None:
    llm = RoleLLM({"serve_small": [INVENTED, INVENTED]}, tokens=9000)

    result, events, _ = await ask(controller(llm))

    skipped = [e for e in events if e.step == "escalate"]
    assert skipped and skipped[0].detail["skipped"] == "budget"
    assert "serve_large" not in llm.roles and result.control is not None
    assert result.control.escalated is None


async def test_low_calibrated_confidence_withholds_the_answer_but_keeps_the_evidence() -> None:
    llm = RoleLLM({"serve_large": [GOOD]})
    policy = POLICY.model_copy(
        update={"routing": POLICY.routing.model_copy(update={"enabled": False})}
    )

    result, events, _ = await ask(controller(llm, policy=policy), scorer=LowConfidenceScorer())

    assert events[-1].step == "abstain" and events[-1].detail["confidence"] == 0.1
    assert result.answer == ABSTAIN_MESSAGE and result.evidence
    assert result.control is not None and result.control.abstained == "low_confidence"


async def test_a_repeated_question_is_served_from_the_cache_without_any_model_call() -> None:
    llm = RoleLLM({"serve_small": [GOOD]})
    cache = AnswerCache(MemoryCacheStore(), embed, POLICY.cache)
    c = controller(llm, cache=cache, metrics=Metrics())
    first, _, _ = await ask(c)
    calls = len(llm.roles)

    second, events, searcher = await ask(c, SIMPLE.upper())

    assert len(llm.roles) == calls and searcher.queries == []
    assert [e.step for e in events] == ["route", "cache"]
    assert second.answer == first.answer and second.control is not None
    assert second.control.cache is not None and second.control.cache.kind == "exact"
    assert second.control.usage.tokens == 0
    assert b'provenance_queries_total{outcome="cache_hit",tier="small"} 1.0' in c.metrics.render()  # type: ignore[union-attr]


async def test_withheld_or_unverified_answers_are_never_cached() -> None:
    store = MemoryCacheStore()
    cache = AnswerCache(store, embed, POLICY.cache)
    policy = POLICY.model_copy(
        update={"routing": POLICY.routing.model_copy(update={"enabled": False})}
    )
    abstaining = controller(RoleLLM({"serve_large": [GOOD]}), policy=policy, cache=cache)
    await ask(abstaining, scorer=LowConfidenceScorer())

    unverified = controller(
        RoleLLM({"serve_large": [INVENTED, INVENTED]}), policy=policy, cache=cache
    )
    await ask(unverified)

    assert store.payloads == {}


async def test_a_spent_budget_is_refused_before_the_run() -> None:
    budgets = MemoryBudgetStore()
    await budgets.add("ana", 10000)

    with pytest.raises(BudgetExhausted):
        await controller(RoleLLM({}), budgets=budgets).preflight("ana")
    assert await controller(RoleLLM({}), budgets=budgets).preflight("ben") == 10000
