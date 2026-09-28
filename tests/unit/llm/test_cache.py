from pathlib import Path

import pytest

from provenance.llm.cache import CachedLLM, CacheMiss, ResponseCache, request_key
from provenance.llm.types import ChatRequest, ChatResponse, Message, Usage

REQ = ChatRequest(messages=[Message(role="user", content="q")], temperature=0)


class CountingLLM:
    def __init__(self) -> None:
        self.calls = 0

    async def complete(self, role: str, request: ChatRequest) -> ChatResponse:
        self.calls += 1
        return ChatResponse(
            content=f"answer {self.calls}",
            provider="p",
            model="m",
            usage=Usage(input_tokens=5, output_tokens=2),
            latency_ms=3,
        )


def test_key_is_stable_for_identical_requests() -> None:
    assert request_key("serve", REQ) == request_key("serve", REQ.model_copy())


def test_key_changes_when_any_request_parameter_changes() -> None:
    base = request_key("serve", REQ)

    assert request_key("serve", REQ.model_copy(update={"temperature": 0.7})) != base
    assert request_key("judge", REQ) != base


async def test_read_write_mode_calls_through_once_then_serves_from_disk(tmp_path: Path) -> None:
    inner = CountingLLM()
    llm = CachedLLM(inner, ResponseCache(tmp_path), mode="read_write")

    first = await llm.complete("serve", REQ)
    second = await llm.complete("serve", REQ)

    assert inner.calls == 1
    assert second.content == first.content
    assert second.cache_hit and not first.cache_hit


async def test_cache_survives_a_new_instance(tmp_path: Path) -> None:
    await CachedLLM(CountingLLM(), ResponseCache(tmp_path), mode="read_write").complete(
        "serve", REQ
    )
    inner = CountingLLM()

    resp = await CachedLLM(inner, ResponseCache(tmp_path), mode="read_write").complete("serve", REQ)

    assert inner.calls == 0
    assert resp.content == "answer 1"


async def test_replay_mode_never_calls_the_model(tmp_path: Path) -> None:
    llm = CachedLLM(CountingLLM(), ResponseCache(tmp_path), mode="replay")

    with pytest.raises(CacheMiss):
        await llm.complete("serve", REQ)


async def test_off_mode_always_calls_through(tmp_path: Path) -> None:
    inner = CountingLLM()
    llm = CachedLLM(inner, ResponseCache(tmp_path), mode="off")

    await llm.complete("serve", REQ)
    await llm.complete("serve", REQ)

    assert inner.calls == 2
