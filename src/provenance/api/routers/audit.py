"""GET /v1/audit: recent tool calls, activity per day, and the passages quarantined as
possible prompt injections. For principals in the `auditor` group only.

The check happens twice: here, for a clear 403, and in the database, where the reader
functions (migration 0005) refuse anyone whose HMAC-signed groups lack `auditor`. The app
role itself still cannot SELECT the log. Quarantined passages are read through row-level
security like any other chunk, so an auditor sees only those in their own sectors.
"""

from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel

from provenance.api.deps import DbDep, PrincipalDep
from provenance.api.errors import ApiError

router = APIRouter(prefix="/v1", tags=["audit"])
AUDITOR = "auditor"


class AuditRow(BaseModel):
    at: datetime
    request_id: str
    principal: str
    groups: list[str]
    tool: str
    input_preview: str
    outcome: str
    detail: dict[str, Any] = {}


class DailyCount(BaseModel):
    day: date
    tool: str
    outcome: str
    calls: int


class Quarantined(BaseModel):
    chunk_id: int
    ticker: str
    company: str
    fiscal_year: int | None
    item: str
    reasons: list[str]
    score: float | None
    preview: str


class AuditReport(BaseModel):
    entries: list[AuditRow]
    daily: list[DailyCount]
    scanned: int
    flagged: int
    quarantined: list[Quarantined]


_COUNTS = (
    "SELECT count(*) FILTER (WHERE injection_flagged IS NOT NULL),"
    " count(*) FILTER (WHERE injection_flagged) FROM chunks"
)
_QUARANTINED = (
    "SELECT c.id, co.ticker, co.name, d.fiscal_year, c.section, c.injection_reasons,"
    " c.injection_score, left(c.text, 240)"
    " FROM chunks c JOIN documents d ON d.id = c.document_id"
    " JOIN companies co ON co.cik = d.cik"
    " WHERE c.injection_flagged"
    " ORDER BY c.injection_score DESC NULLS LAST, c.id LIMIT 100"
)


@router.get("/audit")
async def audit(
    principal: PrincipalDep,
    db: DbDep,
    limit: int = Query(200, ge=1, le=1000),
    days: int = Query(14, ge=1, le=90),
) -> AuditReport:
    if AUDITOR not in principal.groups:
        raise ApiError(403, "forbidden", "the audit log is for auditors")
    rows = await (await db.execute("SELECT * FROM audit_recent(%s)", (limit,))).fetchall()
    daily = await (await db.execute("SELECT * FROM audit_daily(%s)", (days,))).fetchall()
    counts = await (await db.execute(_COUNTS)).fetchone()
    flagged = await (await db.execute(_QUARANTINED)).fetchall()
    assert counts is not None
    return AuditReport(
        entries=[AuditRow.model_validate(dict(zip(_ENTRY_FIELDS, r, strict=True))) for r in rows],
        daily=[DailyCount(day=r[0], tool=r[1], outcome=r[2], calls=r[3]) for r in daily],
        scanned=counts[0],
        flagged=counts[1],
        quarantined=[
            Quarantined.model_validate(dict(zip(_QUARANTINE_FIELDS, r, strict=True)))
            for r in flagged
        ],
    )


_ENTRY_FIELDS = list(AuditRow.model_fields)
_QUARANTINE_FIELDS = list(Quarantined.model_fields)
