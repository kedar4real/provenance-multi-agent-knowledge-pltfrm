"""Request IDs and access logging, as plain ASGI middleware (BaseHTTPMiddleware buffers
streaming responses, which would break SSE later)."""

import logging
import re
import time
import uuid
from contextvars import ContextVar

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUEST_ID_HEADER = "X-Request-ID"
_VALID_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
_request_id: ContextVar[str] = ContextVar("request_id", default="-")

log = logging.getLogger("provenance.api.access")


def current_request_id() -> str:
    return _request_id.get()


class RequestContextMiddleware:
    """Reuses a caller's X-Request-ID if it's well-formed (so logs join across services),
    otherwise mints one; echoes it on the response and logs one line per request."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        incoming = dict(scope["headers"]).get(REQUEST_ID_HEADER.lower().encode(), b"")
        decoded = incoming.decode("latin-1")
        request_id = decoded if _VALID_ID.match(decoded) else uuid.uuid4().hex
        token = _request_id.set(request_id)
        scope.setdefault("state", {})["request_id"] = request_id
        started = time.perf_counter()
        status = 500

        async def send_with_id(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                MutableHeaders(scope=message)[REQUEST_ID_HEADER] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        finally:
            elapsed_ms = (time.perf_counter() - started) * 1000
            log.info(
                "%s %s %d %.1fms id=%s",
                scope["method"], scope["path"], status, elapsed_ms, request_id,
            )  # fmt: skip
            _request_id.reset(token)
