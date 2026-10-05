"""POST /v1/query end to end: real API, search, SQL role and row-level security; a scripted
model so the run is deterministic."""

import json
from pathlib import Path

import psycopg
import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from provenance.api.main import create_app
from provenance.api.principals import hash_key
from provenance.config import Settings
from provenance.llm.types import ChatRequest, ChatResponse, Usage
from provenance.retrieval.hybrid import HybridRetriever
from tests.integration.conftest import FakeEmbedder

pytestmark = [pytest.mark.integration, pytest.mark.usefixtures("corpus")]

FACTS_SQL = (
    "SELECT c.ticker, f.fiscal_year, f.value FROM financial_facts f "
    "JOIN companies c ON c.cik = f.cik WHERE f.metric = 'revenue' ORDER BY c.ticker"
)


class RoleScriptedLLM:
    """Answers by which prompt it was given: the planner, the SQL writer or the answer writer."""

    def __init__(self, plan: dict[str, object], answer: str) -> None:
        self.plan, self.answer = plan, answer

    async def complete(self, role: str, request: ChatRequest) -> ChatResponse:
        system = request.messages[0].content or ""
        if "You route a question" in system:
            content = json.dumps(self.plan)
        elif "PostgreSQL SELECT" in system:
            content = json.dumps({"sql": FACTS_SQL})
        else:
            content = self.answer
        return ChatResponse(content=content, provider="f", model="f", usage=Usage(), latency_ms=1)


@pytest.fixture
def facts(owner: psycopg.Connection) -> None:
    for cik, value, groups in [
        ("0000320193", 416161000000, ["analyst_tech"]),
        ("0000019617", 182447000000, ["analyst_finance"]),
    ]:
        owner.execute(
            "INSERT INTO financial_facts (cik, concept, metric, value, unit, fiscal_year,"
            " fiscal_period, period_end, form, accession, filed_date, acl_groups) VALUES"
            " (%s, 'Revenues', 'revenue', %s, 'USD', 2025, 'FY', '2025-09-27', '10-K', 'x',"
            " '2025-11-01', %s)",
            (cik, value, groups),
        )


async def ask(
    migrated: Settings, tmp_path: Path, llm: RoleScriptedLLM, question: str
) -> tuple[int, list[tuple[str, dict[str, object]]]]:
    principals = tmp_path / "principals.yaml"
    principals.write_text(
        "principals:\n  tech: {display_name: Tech, groups: [analyst_tech]}\n", encoding="utf-8"
    )
    keys = tmp_path / "keys.json"
    keys.write_text(json.dumps({hash_key("pk_tech"): "tech"}), encoding="utf-8")
    settings = migrated.model_copy(
        update={"principals_path": principals, "api_keys_path": keys, "load_models": False}
    )
    retriever = HybridRetriever(FakeEmbedder(), None, None)
    app = create_app(settings, retriever=retriever, llm=llm)
    async with (
        LifespanManager(app) as manager,
        AsyncClient(transport=ASGITransport(manager.app), base_url="http://test") as client,
        client.stream(
            "POST", "/v1/query", json={"question": question}, headers={"X-API-Key": "pk_tech"}
        ) as response,
    ):
        body = (await response.aread()).decode()
        status = response.status_code
    return status, parse_sse(body)


def parse_sse(body: str) -> list[tuple[str, dict[str, object]]]:
    events = []
    for block in body.strip().split("\n\n"):
        fields = dict(line.split(": ", 1) for line in block.splitlines())
        events.append((fields["event"], json.loads(fields["data"])))
    return events


async def test_streams_each_step_then_a_cited_answer(migrated: Settings, tmp_path: Path) -> None:
    llm = RoleScriptedLLM(
        {"needs_text": True, "needs_numbers": False, "sql_question": ""},
        "Tariffs raise component costs [P1].",
    )

    status, events = await ask(migrated, tmp_path, llm, "What do tariffs do to Apple?")

    assert status == 200
    assert [e for e, _ in events] == ["step", "step", "step", "step", "result"]
    assert [d["step"] for e, d in events if e == "step"] == ["plan", "search", "write", "verify"]
    result = events[-1][1]
    assert result["answer"] == "Tariffs raise component costs [P1]."
    assert result["verification"]["ok"] is True  # type: ignore[index]


async def test_the_agent_only_sees_the_callers_rows(
    migrated: Settings, tmp_path: Path, facts: None
) -> None:
    llm = RoleScriptedLLM(
        {"needs_text": True, "needs_numbers": True, "sql_question": "revenue by company"},
        "Apple's revenue was $416.16 billion [F1].",
    )

    _, events = await ask(
        migrated, tmp_path, llm, "Compare Apple and JPMorgan revenue and interest"
    )

    result = events[-1][1]
    rows = result["sql"]["rows"]  # type: ignore[index]
    passages = result["passages"]
    assert rows == [["AAPL", 2025, 416161000000.0]]  # JPM's row exists but isn't visible
    assert {p["ticker"] for p in passages} == {"AAPL"}  # type: ignore[attr-defined]


async def test_query_needs_a_key_and_loaded_models(migrated: Settings, tmp_path: Path) -> None:
    settings = migrated.model_copy(update={"load_models": False})
    async with (
        LifespanManager(create_app(settings)) as manager,
        AsyncClient(transport=ASGITransport(manager.app), base_url="http://test") as client,
    ):
        unauthenticated = await client.post("/v1/query", json={"question": "x"})

    assert unauthenticated.status_code == 401
