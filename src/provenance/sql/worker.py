"""The SQL worker: question -> model-written SQL -> guard -> read-only execution under RLS."""

import json
from datetime import date
from decimal import Decimal
from typing import Any, Protocol

from psycopg import AsyncConnection
from psycopg import Error as DatabaseError
from pydantic import BaseModel, Field

from provenance.db.security import principal_sql
from provenance.llm.types import ChatRequest, ChatResponse, Message
from provenance.sql.guard import UnsafeSQL, guard
from provenance.sql.schema import schema_prompt

SQL_ROLE = "serve_small"
STATEMENT_TIMEOUT_MS = 3000

_PROMPT = """You write one PostgreSQL SELECT query that answers a question about company
financials, using only the tables below. Return JSON: {{"sql": str}}.
Rules: select readable columns (ticker, fiscal_year, metric, value); order results;
compute changes or ratios in SQL when asked; never modify data.

{schema}"""


class Completer(Protocol):
    async def complete(self, role: str, request: ChatRequest) -> ChatResponse: ...


class SqlResult(BaseModel):
    question: str
    sql: str = ""
    columns: list[str] = Field(default_factory=list)
    rows: list[list[Any]] = Field(default_factory=list)
    error: str | None = None
    attempts: int = 0


class SqlWorker:
    def __init__(self, llm: Completer, signing_key: str, max_attempts: int = 2) -> None:
        self._llm = llm
        self._signing_key = signing_key
        self._max_attempts = max_attempts
        self._system = _PROMPT.format(schema=schema_prompt())

    async def answer(self, question: str, conn: AsyncConnection, groups: list[str]) -> SqlResult:
        """`conn` must be connected as the read-only SQL role. A failed attempt (unsafe SQL
        or a database error) is shown to the model once, so it can repair its query."""
        result = SqlResult(question=question)
        feedback, draft = "", ""
        for attempt in range(1, self._max_attempts + 1):
            result.attempts = attempt
            try:
                draft = await self._write(question, feedback)
                result.sql = guard(draft)
                result.columns, result.rows = await self._run(conn, groups, result.sql)
                result.error = None
                return result
            except (UnsafeSQL, DatabaseError) as e:
                result.error = _short(e)
                feedback = f"Your previous SQL failed: {result.error}\nSQL:\n{result.sql or draft}"
            except (json.JSONDecodeError, KeyError) as e:
                result.error = f"model returned no usable SQL ({type(e).__name__})"
                feedback = "Return JSON with a single key 'sql'."
        return result

    async def _write(self, question: str, feedback: str) -> str:
        user = question if not feedback else f"{question}\n\n{feedback}"
        response = await self._llm.complete(
            SQL_ROLE,
            ChatRequest(
                messages=[
                    Message(role="system", content=self._system),
                    Message(role="user", content=user),
                ],
                json_mode=True,
                max_tokens=600,
            ),
        )
        sql: str = json.loads(response.content)["sql"]
        return sql

    async def _run(
        self, conn: AsyncConnection, groups: list[str], sql: str
    ) -> tuple[list[str], list[list[Any]]]:
        async with conn.transaction():
            await conn.execute("SET TRANSACTION READ ONLY")
            await conn.execute(f"SET LOCAL statement_timeout = {STATEMENT_TIMEOUT_MS}")
            principal, params = principal_sql(groups, self._signing_key)
            await conn.execute(principal, params)
            cur = await conn.execute(sql)  # guarded above
            columns = [c.name for c in cur.description or []]
            rows = [[_plain(v) for v in row] for row in await cur.fetchall()]
        return columns, rows


def _plain(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, date):
        return value.isoformat()
    return value


def _short(error: Exception) -> str:
    return str(error).strip().splitlines()[0][:300]
