"""Liveness (is the process up?) and readiness (can it serve?). No auth, no details leaked."""

import asyncio
from typing import Literal

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from provenance.api.deps import ResourcesDep
from provenance.api.lifespan import Resources

router = APIRouter(prefix="/health", tags=["health"])

CHECK_TIMEOUT_S = 2.0
CheckStatus = Literal["ok", "unavailable"]


class Readiness(BaseModel):
    status: CheckStatus
    checks: dict[str, CheckStatus]


@router.get("/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready", response_model=Readiness, responses={503: {"model": Readiness}})
async def ready(resources: ResourcesDep) -> JSONResponse:
    postgres, redis = await asyncio.gather(_postgres(resources), _redis(resources))
    checks: dict[str, CheckStatus] = {"postgres": postgres, "redis": redis}
    ok = all(v == "ok" for v in checks.values())
    body = Readiness(status="ok" if ok else "unavailable", checks=checks)
    return JSONResponse(body.model_dump(), status_code=200 if ok else 503)


async def _postgres(resources: Resources) -> CheckStatus:
    try:
        async with resources.pool.connection(timeout=CHECK_TIMEOUT_S) as conn:
            await conn.execute("SELECT 1")
    except Exception:
        return "unavailable"
    return "ok"


async def _redis(resources: Resources) -> CheckStatus:
    try:
        await asyncio.wait_for(resources.redis.ping(), CHECK_TIMEOUT_S)
    except Exception:
        return "unavailable"
    return "ok"
