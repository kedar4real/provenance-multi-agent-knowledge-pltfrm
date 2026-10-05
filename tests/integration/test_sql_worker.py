"""The SQL worker against the real database as the read-only role, with a scripted model."""

import json
from collections.abc import AsyncIterator

import pytest
from psycopg import AsyncConnection

from provenance.config import Settings
from provenance.llm.types import ChatRequest, ChatResponse, Usage
from provenance.sql.worker import SqlWorker
from tests.integration.conftest import RESTRICTED, TECH

pytestmark = [pytest.mark.integration, pytest.mark.usefixtures("seeded")]

REVENUE = (
    "SELECT c.ticker, f.fiscal_year, f.fiscal_period, f.value FROM financial_facts f "
    "JOIN companies c ON c.cik = f.cik WHERE f.metric = 'revenue' ORDER BY f.fiscal_period"
)


class ScriptedLLM:
    """Returns the scripted SQL strings in order; records what it was told."""

    def __init__(self, *sql: str) -> None:
        self.sql = list(sql)
        self.requests: list[ChatRequest] = []

    async def complete(self, role: str, request: ChatRequest) -> ChatResponse:
        self.requests.append(request)
        content = json.dumps({"sql": self.sql.pop(0)})
        return ChatResponse(
            content=content, provider="fake", model="fake", usage=Usage(), latency_ms=1
        )


@pytest.fixture
async def sql_conn(migrated: Settings) -> AsyncIterator[AsyncConnection]:
    conn = await AsyncConnection.connect(migrated.sql_ro_dsn)
    yield conn
    await conn.close()


def worker(llm: ScriptedLLM, settings: Settings) -> SqlWorker:
    return SqlWorker(llm, settings.rls_signing_key.get_secret_value())


async def test_returns_only_the_callers_rows(sql_conn: AsyncConnection, migrated: Settings) -> None:
    result = await worker(ScriptedLLM(REVENUE), migrated).answer("Apple revenue?", sql_conn, TECH)

    assert result.error is None
    assert result.columns == ["ticker", "fiscal_year", "fiscal_period", "value"]
    assert result.rows == [["AAPL", 2024, "FY", 391035000000.0]]


async def test_a_wider_principal_sees_more_with_the_same_sql(
    sql_conn: AsyncConnection, migrated: Settings
) -> None:
    result = await worker(ScriptedLLM(REVENUE), migrated).answer(
        "Apple revenue?", sql_conn, TECH + RESTRICTED
    )

    assert len(result.rows) == 2


async def test_unsafe_sql_is_refused_and_the_model_repairs_it(
    sql_conn: AsyncConnection, migrated: Settings
) -> None:
    llm = ScriptedLLM("SELECT set_config('app.groups', 'internal_restricted', true)", REVENUE)

    result = await worker(llm, migrated).answer("Apple revenue?", sql_conn, TECH)

    assert result.attempts == 2
    assert result.error is None and len(result.rows) == 1
    assert "set_config() is not allowed" in (llm.requests[1].messages[1].content or "")


async def test_a_database_error_is_fed_back_once(
    sql_conn: AsyncConnection, migrated: Settings
) -> None:
    llm = ScriptedLLM("SELECT revenue FROM financial_facts", REVENUE)

    result = await worker(llm, migrated).answer("Apple revenue?", sql_conn, TECH)

    assert result.attempts == 2 and result.rows
    assert 'column "revenue" does not exist' in (llm.requests[1].messages[1].content or "")


async def test_gives_up_after_two_failures_without_rows(
    sql_conn: AsyncConnection, migrated: Settings
) -> None:
    llm = ScriptedLLM("DELETE FROM financial_facts", "SELECT * FROM documents")

    result = await worker(llm, migrated).answer("anything", sql_conn, TECH)

    assert result.rows == []
    assert result.error == "table 'documents' is not allowed (use financial_facts, companies)"


async def test_the_sql_role_cannot_read_other_tables_even_unguarded(
    sql_conn: AsyncConnection,
) -> None:
    # Layer two, without layer one: the role itself has no access to documents.
    with pytest.raises(Exception, match="permission denied"):
        await sql_conn.execute("SELECT count(*) FROM documents")
