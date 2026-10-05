"""Request-scoped dependencies: who is calling, and a database transaction bound to them."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, Request, Security
from fastapi.security import APIKeyHeader
from psycopg import AsyncConnection

from provenance.api.errors import ApiError
from provenance.api.lifespan import Resources
from provenance.api.principals import Principal
from provenance.db.security import principal_sql

DB_ACQUIRE_TIMEOUT_S = 5.0

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_resources(request: Request) -> Resources:
    resources: Resources = request.app.state.resources
    return resources


ResourcesDep = Annotated[Resources, Depends(get_resources)]


async def get_principal(
    resources: ResourcesDep, api_key: Annotated[str | None, Security(_api_key_header)]
) -> Principal:
    if not api_key:
        raise ApiError(401, "missing_api_key", "send an API key in the X-API-Key header")
    principal = resources.registry.authenticate(api_key)
    if principal is None:
        raise ApiError(401, "invalid_api_key", "the API key is not valid")
    return principal


PrincipalDep = Annotated[Principal, Depends(get_principal)]


@asynccontextmanager
async def principal_transaction(
    resources: Resources, principal: Principal
) -> AsyncIterator[AsyncConnection]:
    """A transaction carrying the caller's signed groups. Row-level security reads them, so
    every query in it sees only rows the caller may see. The settings are transaction-local,
    so the pooled connection is clean when it's returned."""
    key = resources.settings.rls_signing_key.get_secret_value()
    sql, params = principal_sql(principal.groups, key)
    async with (
        resources.pool.connection(timeout=DB_ACQUIRE_TIMEOUT_S) as conn,
        conn.transaction(),
    ):
        await conn.execute(sql, params)
        yield conn


async def get_db(
    resources: ResourcesDep, principal: PrincipalDep
) -> AsyncIterator[AsyncConnection]:
    """One principal-scoped transaction per request."""
    async with principal_transaction(resources, principal) as conn:
        yield conn


DbDep = Annotated[AsyncConnection, Depends(get_db)]
