"""Per-caller daily token budgets, kept in Redis so every API worker shares them."""

from datetime import UTC, datetime
from typing import Protocol

from redis.asyncio import Redis


class BudgetStore(Protocol):
    async def spent(self, principal: str) -> int: ...

    async def add(self, principal: str, tokens: int) -> int: ...


def _day() -> str:
    return datetime.now(UTC).strftime("%Y%m%d")


class RedisBudgetStore:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def spent(self, principal: str) -> int:
        raw = await self._redis.get(f"budget:{principal}:{_day()}")
        return int(raw or 0)

    async def add(self, principal: str, tokens: int) -> int:
        key = f"budget:{principal}:{_day()}"
        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.incrby(key, tokens)
            pipe.expire(key, 2 * 86400)  # outlives the day it counts, then disappears
            total, _ = await pipe.execute()
        return int(total)


class MemoryBudgetStore:
    def __init__(self) -> None:
        self.totals: dict[str, int] = {}

    async def spent(self, principal: str) -> int:
        return self.totals.get(principal, 0)

    async def add(self, principal: str, tokens: int) -> int:
        self.totals[principal] = self.totals.get(principal, 0) + tokens
        return self.totals[principal]
