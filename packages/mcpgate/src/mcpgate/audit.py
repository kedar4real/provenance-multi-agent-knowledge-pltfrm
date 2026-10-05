"""Append-only JSONL audit log and a per-caller sliding-window rate limiter."""

import json
import time
from collections import deque
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PREVIEW_CHARS = 200


class AuditLog:
    """One JSON object per line. Arguments are logged as a short preview: enough to
    investigate, not a second copy of whatever the caller sent."""

    def __init__(self, path: Path | None) -> None:
        self.path = path
        self.events: list[dict[str, Any]] = []  # also kept in memory, for tests and `inspect`

    def write(self, event: str, **fields: Any) -> None:
        record = {"ts": datetime.now(UTC).isoformat(timespec="milliseconds"), "event": event}
        record |= fields
        self.events.append(record)
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def preview(arguments: dict[str, Any] | None) -> str:
    text = json.dumps(arguments or {}, ensure_ascii=False, default=str)
    return text if len(text) <= PREVIEW_CHARS else text[:PREVIEW_CHARS] + "..."


class RateLimiter:
    def __init__(self, calls: int, window_s: float, clock: Callable[[], float] = time.monotonic):
        self.calls, self.window_s, self._clock = calls, window_s, clock
        self._recent: deque[float] = deque()

    def allow(self) -> tuple[bool, float]:
        """(allowed, seconds until the next call would be allowed)."""
        now = self._clock()
        while self._recent and now - self._recent[0] >= self.window_s:
            self._recent.popleft()
        if len(self._recent) >= self.calls:
            return False, self.window_s - (now - self._recent[0])
        self._recent.append(now)
        return True, 0.0
