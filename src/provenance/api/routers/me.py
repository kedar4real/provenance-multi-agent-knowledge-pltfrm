"""Who the caller is and what they can see: a quick end-to-end check of auth + RLS."""

from fastapi import APIRouter
from pydantic import BaseModel

from provenance.api.deps import DbDep, PrincipalDep

router = APIRouter(prefix="/v1", tags=["principal"])


class Visibility(BaseModel):
    documents: int
    chunks: int
    financial_facts: int
    tickers: list[str]


class Me(BaseModel):
    name: str
    display_name: str
    groups: list[str]
    visible: Visibility


@router.get("/me")
async def me(principal: PrincipalDep, db: DbDep) -> Me:
    # No group filter in the SQL: row-level security does the filtering.
    cur = await db.execute(
        "SELECT (SELECT count(*) FROM documents), (SELECT count(*) FROM chunks),"
        " (SELECT count(*) FROM financial_facts),"
        " (SELECT coalesce(array_agg(DISTINCT c.ticker ORDER BY c.ticker), '{}')"
        "  FROM documents d JOIN companies c USING (cik))"
    )
    row = await cur.fetchone()
    assert row is not None
    documents, chunks, facts, tickers = row
    return Me(
        name=principal.name,
        display_name=principal.display_name,
        groups=principal.groups,
        visible=Visibility(
            documents=documents, chunks=chunks, financial_facts=facts, tickers=tickers
        ),
    )
