import time
from collections.abc import Callable


class CircuitBreaker:
    """Blocks calls to a provider until a cooldown passes.

    Tripped explicitly (a rate limit with a known retry delay) or implicitly by consecutive
    transient failures. There is no separate half-open state: once the cooldown passes the
    next call is allowed through, and its outcome either resets or re-trips the breaker.
    """

    def __init__(
        self,
        now: Callable[[], float] = time.monotonic,
        failure_threshold: int = 3,
        base_cooldown_s: float = 30.0,
    ) -> None:
        self._now = now
        self._failure_threshold = failure_threshold
        self._base_cooldown_s = base_cooldown_s
        self._open_until = 0.0
        self._failures = 0

    def allow(self) -> bool:
        return self._now() >= self._open_until

    def seconds_until_available(self) -> float:
        return max(0.0, self._open_until - self._now())

    def trip(self, cooldown_s: float | None = None) -> None:
        until = self._now() + (cooldown_s if cooldown_s is not None else self._base_cooldown_s)
        self._open_until = max(self._open_until, until)

    def record_success(self) -> None:
        self._failures = 0

    def record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self._failure_threshold:
            self.trip()
            self._failures = 0
