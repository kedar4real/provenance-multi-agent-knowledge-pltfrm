"""One error shape for every failure: {"error": {"code", "message", "request_id"}}.

Internal details (stack traces, SQL, driver messages) are logged, never returned.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from psycopg import OperationalError
from psycopg_pool import PoolTimeout
from starlette.exceptions import HTTPException as StarletteHTTPException

from provenance.api.middleware import REQUEST_ID_HEADER, current_request_id

log = logging.getLogger("provenance.api")


class ApiError(Exception):
    """Raised by routes and dependencies for expected failures."""

    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def error_response(
    status: int, code: str, message: str, headers: dict[str, str] | None = None
) -> JSONResponse:
    request_id = current_request_id()
    body = {"error": {"code": code, "message": message, "request_id": request_id}}
    # 500s are built outside the request middleware, so the ID header is set here too.
    return JSONResponse(body, status, headers={REQUEST_ID_HEADER: request_id, **(headers or {})})


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def _api_error(_: Request, exc: ApiError) -> JSONResponse:
        headers = {"WWW-Authenticate": "ApiKey"} if exc.status == 401 else None
        return error_response(exc.status, exc.code, exc.message, headers)

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = {404: "not_found", 405: "method_not_allowed"}.get(exc.status_code, "http_error")
        return error_response(exc.status_code, code, str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        fields = ", ".join(".".join(str(p) for p in e["loc"]) for e in exc.errors())
        return error_response(422, "invalid_request", f"invalid fields: {fields}")

    async def _database_down(_: Request, exc: Exception) -> JSONResponse:
        log.warning("database unavailable: %s", type(exc).__name__)
        return error_response(503, "database_unavailable", "the database is unavailable")

    app.add_exception_handler(PoolTimeout, _database_down)
    app.add_exception_handler(OperationalError, _database_down)

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception) -> JSONResponse:
        log.error("unhandled error", exc_info=exc)
        return error_response(500, "internal_error", "internal server error")
