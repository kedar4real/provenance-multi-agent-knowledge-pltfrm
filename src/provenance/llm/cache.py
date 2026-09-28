import hashlib
import json
from pathlib import Path
from typing import Literal, Protocol

from provenance.llm.types import ChatRequest, ChatResponse

CacheMode = Literal["off", "read_write", "replay"]


class CacheMiss(Exception):
    """Replay mode found no recorded response, so the run can't be reproduced exactly."""


class CompletesByRole(Protocol):
    async def complete(self, role: str, request: ChatRequest) -> ChatResponse: ...


def request_key(role: str, request: ChatRequest) -> str:
    canonical = json.dumps(
        {"role": role, "request": request.model_dump(mode="json")},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


class ResponseCache:
    """One JSON file per request hash, sharded by prefix to keep directories small."""

    def __init__(self, root: Path) -> None:
        self._root = root

    def _path(self, key: str) -> Path:
        return self._root / key[:2] / f"{key}.json"

    def get(self, key: str) -> ChatResponse | None:
        path = self._path(key)
        if not path.exists():
            return None
        return ChatResponse.model_validate_json(path.read_text(encoding="utf-8"))

    def put(self, key: str, response: ChatResponse) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(response.model_dump_json(), encoding="utf-8")
        tmp.replace(path)


class CachedLLM:
    """Record/replay wrapper: evals re-run for free and reproduce exactly.

    `read_write` serves hits and records misses; `replay` never calls a model and raises
    `CacheMiss` instead, which is how a run is proven to be fully reproducible.
    """

    def __init__(self, inner: CompletesByRole, cache: ResponseCache, mode: CacheMode) -> None:
        self._inner = inner
        self._cache = cache
        self._mode = mode

    async def complete(self, role: str, request: ChatRequest) -> ChatResponse:
        if self._mode == "off":
            return await self._inner.complete(role, request)
        key = request_key(role, request)
        cached = self._cache.get(key)
        if cached is not None:
            return cached.model_copy(update={"cache_hit": True})
        if self._mode == "replay":
            raise CacheMiss(f"no recorded response for role '{role}' (key {key[:12]})")
        response = await self._inner.complete(role, request)
        self._cache.put(key, response)
        return response
