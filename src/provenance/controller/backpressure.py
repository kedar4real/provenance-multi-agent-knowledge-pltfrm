"""Bounded concurrency for agent runs: a few run at once, a few more wait, the rest are shed.

Shedding early (HTTP 503 with Retry-After) beats accepting everything: every queued run
holds a connection and would later burn free-tier quota on an answer the client has long
stopped waiting for.
"""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from provenance.controller.policy import Admission, BackpressureConfig, admit


class Overloaded(Exception):
    def __init__(self, reason: str, retry_after_s: int) -> None:
        super().__init__(reason)
        self.reason = reason
        self.retry_after_s = retry_after_s


class Gate:
    def __init__(self, config: BackpressureConfig) -> None:
        self._config = config
        self._slots = asyncio.Semaphore(config.max_concurrent)
        self.running = 0
        self.waiting = 0

    @property
    def full(self) -> bool:
        """No free slot and no room to queue: shed before starting a stream."""
        return self._slots.locked() and not admit(self.waiting, self._config).admitted

    async def acquire(self) -> None:
        if self._slots.locked():
            decision: Admission = admit(self.waiting, self._config)
            if not decision.admitted:
                raise Overloaded(decision.reason, decision.retry_after_s or 1)
        self.waiting += 1
        try:
            await asyncio.wait_for(self._slots.acquire(), self._config.wait_timeout_s)
        except TimeoutError:
            raise Overloaded("queue_timeout", int(self._config.wait_timeout_s)) from None
        finally:
            self.waiting -= 1
        self.running += 1

    def release(self) -> None:
        self.running -= 1
        self._slots.release()

    @asynccontextmanager
    async def slot(self) -> AsyncIterator[None]:
        await self.acquire()
        try:
            yield
        finally:
            self.release()
