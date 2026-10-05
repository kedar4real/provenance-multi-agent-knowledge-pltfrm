"""A permission-scoped semantic answer cache on Redis 8 vector sets.

A hit returns a stored answer without running the agent. Three rules keep it safe:
- **Scoped by permissions.** The key includes a hash of the caller's access groups, so an
  answer computed from one sector's filings is never served to a caller who can't see them.
- **Entity guard.** A semantic hit must also mention the same companies, years, numbers
  and metrics ("Apple revenue 2024" vs "Apple revenue 2023" embed almost identically). The
  guard is a vector-set attribute filter, so a near-miss never even competes.
- **Only good answers are stored:** verified, not declined, not abstained, not degraded.

Questions are redacted before they're embedded or stored, like everywhere else.
"""

import asyncio
import hashlib
import json
import time
from collections.abc import Callable
from typing import Protocol

import numpy as np
from pydantic import BaseModel
from redis.asyncio import Redis
from redis.commands.vectorset.commands import QuantizationOptions

from provenance.controller.classifier import Entities, entities
from provenance.controller.policy import CacheConfig

Embed = Callable[[str], np.ndarray]


class CacheLookup(BaseModel):
    hit: bool
    kind: str = "miss"  # "exact" | "semantic" | "miss" | "off"
    similarity: float | None = None
    matched_question: str | None = None
    ms: float = 0.0


class CacheStore(Protocol):
    async def nearest(
        self, namespace: str, vector: list[float], signature: str | None
    ) -> tuple[str, float] | None:
        """The closest element and its cosine similarity, among those with this signature
        (any signature when None)."""
        ...

    async def put(
        self,
        namespace: str,
        element: str,
        vector: list[float],
        signature: str,
        payload: str,
        ttl_s: int,
    ) -> None: ...  # fmt: skip

    async def payload(self, namespace: str, element: str) -> str | None: ...

    async def forget(self, namespace: str, element: str) -> None: ...


def normalize(question: str) -> str:
    return " ".join(question.lower().split()).rstrip("?.! ")


def signature(found: Entities) -> str:
    return hashlib.sha256(found.model_dump_json().encode()).hexdigest()[:16]


def groups_hash(groups: list[str]) -> str:
    return hashlib.sha256("\x1f".join(sorted(set(groups))).encode()).hexdigest()[:16]


class AnswerCache:
    def __init__(self, store: CacheStore, embed: Embed, config: CacheConfig) -> None:
        self._store = store
        self._embed = embed
        self._config = config

    @property
    def enabled(self) -> bool:
        return self._config.enabled

    def namespace(self, groups: list[str]) -> str:
        return f"qcache:v{self._config.version}:{groups_hash(groups)}"

    async def lookup(self, question: str, groups: list[str]) -> tuple[str | None, CacheLookup]:
        """The stored payload (if any) and how it was found."""
        started = time.perf_counter()
        if not self._config.enabled:
            return None, CacheLookup(hit=False, kind="off")
        namespace = self.namespace(groups)
        exact = _element(question)
        payload = await self._store.payload(namespace, exact)
        if payload is not None:
            return payload, _lookup(started, "exact", 1.0, question)

        vector = await asyncio.to_thread(self._vector, question)
        guard = signature(entities(question)) if self._config.entity_guard else None
        nearest = await self._store.nearest(namespace, vector, guard)
        if nearest is None or nearest[1] < self._config.similarity:
            similarity = round(nearest[1], 4) if nearest else None
            return None, CacheLookup(hit=False, similarity=similarity, ms=_elapsed(started))
        element, similarity = nearest
        payload = await self._store.payload(namespace, element)
        if payload is None:  # the answer expired; drop its vector too
            await self._store.forget(namespace, element)
            return None, CacheLookup(hit=False, ms=_elapsed(started))
        matched = json.loads(payload).get("question")
        return payload, _lookup(started, "semantic", similarity, matched)

    async def store(self, question: str, groups: list[str], payload: str) -> None:
        if not self._config.enabled:
            return
        vector = await asyncio.to_thread(self._vector, question)
        await self._store.put(
            self.namespace(groups), _element(question), vector,
            signature(entities(question)), payload, self._config.ttl_s,
        )  # fmt: skip

    def _vector(self, question: str) -> list[float]:
        v = np.asarray(self._embed(question), dtype=np.float32)
        norm = float(np.linalg.norm(v))
        unit: list[float] = (v / norm if norm else v).tolist()
        return unit


def _element(question: str) -> str:
    return hashlib.sha256(normalize(question).encode()).hexdigest()[:24]


def _elapsed(started: float) -> float:
    return round((time.perf_counter() - started) * 1000, 1)


def _lookup(started: float, kind: str, similarity: float, matched: str | None) -> CacheLookup:
    return CacheLookup(
        hit=True, kind=kind, similarity=round(similarity, 4), matched_question=matched,
        ms=_elapsed(started),
    )  # fmt: skip


class RedisCacheStore:
    """Vectors in one vector set per namespace (signature as a filterable attribute);
    payloads in plain keys with a TTL. A vector whose payload has expired is removed the
    next time it's matched, and the whole set expires if the namespace goes unused."""

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def nearest(
        self, namespace: str, vector: list[float], signature: str | None
    ) -> tuple[str, float] | None:
        # Raw command: redis-py's async VSIM reply parser fails on scored results.
        args: list[str | float | int] = ["VSIM", f"{namespace}:vec", "VALUES", len(vector)]
        args += [*vector, "WITHSCORES", "COUNT", 1]
        if signature:
            args += ["FILTER", f'.sig == "{signature}"']
        reply = await self._redis.execute_command(*args)  # type: ignore[no-untyped-call]
        if not reply:
            return None
        # A map under RESP3, a flat [element, score, ...] list under RESP2.
        element, score = next(iter(reply.items())) if isinstance(reply, dict) else reply[:2]
        name = element.decode() if isinstance(element, bytes) else str(element)
        return name, 2 * float(score) - 1  # Redis reports (1 + cosine) / 2

    async def put(
        self, namespace: str, element: str, vector: list[float], signature: str, payload: str,
        ttl_s: int,
    ) -> None:  # fmt: skip
        key = f"{namespace}:vec"
        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.set(f"{namespace}:item:{element}", payload, ex=ttl_s)
            pipe.vset().vadd(
                key, vector, element, quantization=QuantizationOptions.NOQUANT,
                attributes={"sig": signature},
            )  # fmt: skip
            pipe.expire(key, ttl_s)
            await pipe.execute()

    async def payload(self, namespace: str, element: str) -> str | None:
        raw = await self._redis.get(f"{namespace}:item:{element}")
        return raw.decode() if isinstance(raw, bytes) else raw

    async def forget(self, namespace: str, element: str) -> None:
        await self._redis.vset().vrem(f"{namespace}:vec", element)


class MemoryCacheStore:
    """Same behaviour in memory, for tests and the cache eval."""

    def __init__(self) -> None:
        self.vectors: dict[str, dict[str, tuple[np.ndarray, str]]] = {}
        self.payloads: dict[tuple[str, str], str] = {}

    async def nearest(
        self, namespace: str, vector: list[float], signature: str | None
    ) -> tuple[str, float] | None:
        query = np.asarray(vector, dtype=np.float32)
        candidates = [
            (element, float(v @ query))
            for element, (v, sig) in self.vectors.get(namespace, {}).items()
            if signature is None or sig == signature
        ]
        return max(candidates, key=lambda c: c[1]) if candidates else None

    async def put(
        self, namespace: str, element: str, vector: list[float], signature: str, payload: str,
        ttl_s: int,
    ) -> None:  # fmt: skip
        self.vectors.setdefault(namespace, {})[element] = (
            np.asarray(vector, dtype=np.float32), signature,
        )  # fmt: skip
        self.payloads[(namespace, element)] = payload

    async def payload(self, namespace: str, element: str) -> str | None:
        return self.payloads.get((namespace, element))

    async def forget(self, namespace: str, element: str) -> None:
        self.vectors.get(namespace, {}).pop(element, None)
