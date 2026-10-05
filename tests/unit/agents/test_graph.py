"""The agent graph with scripted models and fake workers: routing, parallel workers,
verification-driven revision, the revision cap, and fallbacks."""

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

from psycopg import AsyncConnection

from provenance.agents.graph import PLAN_ROLE, WRITE_ROLE, AgentDeps, build_graph, run_agent
from provenance.agents.types import AgentResult, TraceEvent
from provenance.llm.types import ChatRequest, ChatResponse, Usage
from provenance.retrieval.types import Hit, SearchFilters, SearchResult
from provenance.sql.worker import SqlResult

GROUPS = ["analyst_finance"]


def hit(chunk_id: int, text: str) -> Hit:
    return Hit(
        chunk_id=chunk_id, document_id=1, ticker="JPM", company="JPMorgan Chase",
        fiscal_year=2025, item="7", section_title="MD&A", text=text, context="ctx",
        char_start=0, char_end=len(text), url="https://sec",
    )  # fmt: skip


PASSAGE = hit(11, "Net interest income was $95.4 billion, up 3%.")


class ScriptedLLM:
    def __init__(self, plan: Any, *answers: str) -> None:
        self.plan = plan
        self.answers = list(answers)
        self.calls: list[tuple[str, ChatRequest]] = []

    async def complete(self, role: str, request: ChatRequest) -> ChatResponse:
        self.calls.append((role, request))
        content = json.dumps(self.plan) if role == PLAN_ROLE else self.answers.pop(0)
        return ChatResponse(content=content, provider="f", model="f", usage=Usage(), latency_ms=1)

    def roles(self) -> list[str]:
        return [role for role, _ in self.calls]


class FakeSearcher:
    def __init__(self, hits: list[Hit]) -> None:
        self.hits = hits
        self.queries: list[str] = []

    async def search(
        self, conn: AsyncConnection, query: str, k: int = 8, mode: Any = "hybrid",
        rerank: bool = True, rewrite: bool = True,
    ) -> SearchResult:  # fmt: skip
        self.queries.append(query)
        return SearchResult(
            query=query, search_query=query, filters=SearchFilters(), mode="hybrid",
            reranked=True, hits=self.hits, timings_ms={},
        )  # fmt: skip


class FakeSql:
    def __init__(self, rows: list[list[Any]]) -> None:
        self.rows = rows
        self.questions: list[str] = []

    async def answer(self, question: str, conn: AsyncConnection, groups: list[str]) -> SqlResult:
        self.questions.append(question)
        return SqlResult(
            question=question, sql="SELECT 1", columns=["ticker", "fiscal_year", "value"],
            rows=self.rows, attempts=1,
        )  # fmt: skip


@asynccontextmanager
async def no_connection() -> AsyncIterator[AsyncConnection]:
    yield cast(AsyncConnection, None)


async def run(llm: ScriptedLLM, searcher: FakeSearcher, sql: FakeSql, question: str) -> tuple[
    AgentResult, list[TraceEvent]
]:  # fmt: skip
    deps = AgentDeps(llm, searcher, sql, no_connection, no_connection)
    events: list[TraceEvent] = []
    result = None
    async for item in run_agent(build_graph(deps), question, GROUPS):
        if isinstance(item, AgentResult):
            result = item
        else:
            events.append(item)
    assert result is not None
    return result, events


TEXT_PLAN = {"needs_text": True, "needs_numbers": False, "sql_question": ""}
NUMBERS_PLAN = {"needs_text": False, "needs_numbers": True, "sql_question": "JPM NII 2025"}
BOTH_PLAN = {"needs_text": True, "needs_numbers": True, "sql_question": "JPM NII 2025"}


async def test_text_questions_search_and_answer_with_citations() -> None:
    llm = ScriptedLLM(TEXT_PLAN, "Net interest income was $95.4 billion [P1].")
    sql = FakeSql([])

    result, events = await run(llm, FakeSearcher([PASSAGE]), sql, "How did NII change?")

    assert result.verification is not None and result.verification.ok
    assert [e.step for e in events] == ["plan", "search", "write", "verify"]
    assert sql.questions == []
    assert llm.roles() == [PLAN_ROLE, WRITE_ROLE]


async def test_number_questions_go_to_sql_with_the_planned_request() -> None:
    llm = ScriptedLLM(NUMBERS_PLAN, "It was $95.44 billion [F1].")
    sql = FakeSql([["JPM", 2025, 95443000000.0]])
    searcher = FakeSearcher([PASSAGE])

    result, _ = await run(llm, searcher, sql, "What was JPM's NII in 2025?")

    assert sql.questions == ["JPM NII 2025"]
    assert searcher.queries == []
    assert [e.id for e in result.evidence] == ["F1"]
    assert result.verification is not None and result.verification.ok


async def test_both_workers_run_and_both_kinds_of_evidence_are_citable() -> None:
    llm = ScriptedLLM(BOTH_PLAN, "NII was $95.44 billion [F1], driven by rates [P1].")

    result, events = await run(
        llm, FakeSearcher([PASSAGE]), FakeSql([["JPM", 2025, 95443000000.0]]), "NII and why?"
    )

    assert {e.step for e in events} >= {"search", "sql"}
    assert [e.id for e in result.evidence] == ["P1", "F1"]


async def test_an_invented_number_triggers_one_revision_with_the_reason() -> None:
    llm = ScriptedLLM(
        TEXT_PLAN,
        "Net interest income was $97.1 billion [P1].",
        "Net interest income was $95.4 billion [P1].",
    )

    result, events = await run(llm, FakeSearcher([PASSAGE]), FakeSql([]), "NII?")

    assert result.revisions == 1
    assert result.verification is not None and result.verification.ok
    assert "revise" in [e.step for e in events]
    revision_prompt = llm.calls[-1][1].messages[1].content or ""
    assert "97.1 billion" in revision_prompt


async def test_revision_is_capped_so_the_agent_cannot_loop() -> None:
    llm = ScriptedLLM(TEXT_PLAN, "It was $1.0 billion [P1].", "It was $2.0 billion [P1].")

    result, _ = await run(llm, FakeSearcher([PASSAGE]), FakeSql([]), "NII?")

    assert result.revisions == 1
    assert result.verification is not None and not result.verification.ok
    assert llm.roles().count(WRITE_ROLE) == 2


async def test_no_evidence_means_a_decline_without_calling_the_writer() -> None:
    llm = ScriptedLLM(TEXT_PLAN)

    result, _ = await run(llm, FakeSearcher([]), FakeSql([]), "Tesla deliveries?")

    assert result.declined
    assert WRITE_ROLE not in llm.roles()


async def test_an_unusable_plan_falls_back_to_text_search() -> None:
    llm = ScriptedLLM("not a plan", "NII was $95.4 billion [P1].")
    searcher = FakeSearcher([PASSAGE])

    result, _ = await run(llm, searcher, FakeSql([]), "NII?")

    assert result.plan.needs_text and searcher.queries


async def test_the_question_is_redacted_before_any_model_sees_it() -> None:
    llm = ScriptedLLM(TEXT_PLAN, "NII was $95.4 billion [P1].")

    await run(llm, FakeSearcher([PASSAGE]), FakeSql([]), "NII? reply to jo@example.com")

    assert all("jo@example.com" not in (m.content or "") for _, r in llm.calls for m in r.messages)
