"""An append-only record of every tool call: who asked, which tool, what for, what happened.

The app role may INSERT into audit_log but not read, change or delete it (migration 0003).
Inputs are stored as a redacted, truncated preview, never full prompts or results. An
audit write that fails is logged and does not fail the user's request: availability of
answers matters more than completeness of the log, and the failure itself is visible.
"""

import json
import logging
from typing import Any, Literal, Protocol

from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel, Field

from provenance.security.pii import redact

log = logging.getLogger("provenance.audit")
PREVIEW_CHARS = 200


class AuditEntry(BaseModel):
    request_id: str
    principal: str
    groups: list[str]
    tool: str
    input_preview: str
    outcome: Literal["ok", "denied", "error"]
    detail: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def build(
        cls, *, request_id: str, principal: str, groups: list[str], tool: str, tool_input: str,
        outcome: Literal["ok", "denied", "error"], detail: dict[str, Any] | None = None,
    ) -> "AuditEntry":  # fmt: skip
        preview = redact(tool_input).text[:PREVIEW_CHARS]
        return cls(
            request_id=request_id, principal=principal, groups=groups, tool=tool,
            input_preview=preview, outcome=outcome, detail=detail or {},
        )  # fmt: skip


class AuditSink(Protocol):
    async def write(self, entry: AuditEntry) -> None: ...


class PostgresAudit:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self._pool = pool

    async def write(self, entry: AuditEntry) -> None:
        try:
            async with self._pool.connection(timeout=5) as conn:
                await conn.execute(
                    "INSERT INTO audit_log (request_id, principal, groups, tool, input_preview,"
                    " outcome, detail) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (
                        entry.request_id, entry.principal, entry.groups, entry.tool,
                        entry.input_preview, entry.outcome, json.dumps(entry.detail, default=str),
                    ),
                )  # fmt: skip
                await conn.commit()
        except Exception:
            log.exception("audit write failed for request %s", entry.request_id)


class MemoryAudit:
    """For tests and evals: keeps entries in a list."""

    def __init__(self) -> None:
        self.entries: list[AuditEntry] = []

    async def write(self, entry: AuditEntry) -> None:
        self.entries.append(entry)
