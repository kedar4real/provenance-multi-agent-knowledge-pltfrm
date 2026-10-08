"""Optional token streaming, without changing what a completion returns.

A caller that wants the answer as it is written (the agent's writer) sets `token_sink` for
the duration of its call. The provider then streams from the API, forwards each text
fragment to the sink, and still returns one complete ChatResponse, so routing, failover,
metering and the response cache work exactly as for a non-streamed call. Each provider
attempt starts with `reset()`: if the router fails over mid-answer, what was shown so far
is discarded rather than mixed with the next model's text.
"""

from contextvars import ContextVar
from typing import Protocol


class TokenSink(Protocol):
    def reset(self) -> None: ...
    def delta(self, text: str) -> None: ...


token_sink: ContextVar[TokenSink | None] = ContextVar("token_sink", default=None)
