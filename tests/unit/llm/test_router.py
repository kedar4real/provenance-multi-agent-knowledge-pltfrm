from collections.abc import Sequence

import pytest

from provenance.llm.errors import (
    AllProvidersFailed,
    ProviderRejected,
    ProviderUnavailable,
    RateLimited,
)
from provenance.llm.router import LLMRouter, ModelChoice
from provenance.llm.types import ChatRequest, ChatResponse, Message, Usage

REQ = ChatRequest(messages=[Message(role="user", content="q")])


class FakeProvider:
    """Plays back a script of results; an Exception entry is raised instead of returned."""

    def __init__(self, name: str, script: Sequence[str | Exception]) -> None:
        self.name = name
        self.script = list(script)
        self.calls: list[str] = []

    async def complete(self, request: ChatRequest, model: str) -> ChatResponse:
        self.calls.append(model)
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        return ChatResponse(
            content=item, provider=self.name, model=model, usage=Usage(), latency_ms=1
        )


class Clock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t


def make_router(
    *providers: FakeProvider, clock: Clock | None = None, sleeps: list[float] | None = None
) -> LLMRouter:
    async def fake_sleep(s: float) -> None:
        if sleeps is not None:
            sleeps.append(s)

    chain = [ModelChoice(provider=p.name, model=f"{p.name}-model") for p in providers]
    return LLMRouter(
        providers={p.name: p for p in providers},
        roles={"serve": chain},
        now=clock or Clock(),
        sleep=fake_sleep,
        max_retries=2,
    )


async def test_first_choice_answers_when_healthy() -> None:
    a, b = FakeProvider("a", ["from a"]), FakeProvider("b", ["from b"])

    resp = await make_router(a, b).complete("serve", REQ)

    assert resp.content == "from a"
    assert b.calls == []
    assert [(x.provider, x.outcome) for x in resp.attempts] == [("a", "ok")]


async def test_rate_limit_falls_back_to_next_provider() -> None:
    a = FakeProvider("a", [RateLimited("a", retry_after_s=28)])
    b = FakeProvider("b", ["from b"])

    resp = await make_router(a, b).complete("serve", REQ)

    assert resp.content == "from b"
    assert [(x.provider, x.outcome) for x in resp.attempts] == [("a", "rate_limited"), ("b", "ok")]


async def test_rate_limited_provider_is_skipped_until_its_retry_delay_passes() -> None:
    clock = Clock()
    a = FakeProvider("a", [RateLimited("a", retry_after_s=28), "a again"])
    b = FakeProvider("b", ["b1", "b2"])
    router = make_router(a, b, clock=clock)

    await router.complete("serve", REQ)
    clock.t = 10
    second = await router.complete("serve", REQ)
    clock.t = 28
    third = await router.complete("serve", REQ)

    assert second.content == "b2"
    assert [x.outcome for x in second.attempts] == ["breaker_open", "ok"]
    assert third.content == "a again"


async def test_transient_errors_retry_same_provider_with_backoff() -> None:
    sleeps: list[float] = []
    a = FakeProvider("a", [ProviderUnavailable("a", "503"), ProviderUnavailable("a", "503"), "ok"])

    resp = await make_router(a, sleeps=sleeps).complete("serve", REQ)

    assert resp.content == "ok"
    assert len(a.calls) == 3
    assert len(sleeps) == 2 and sleeps[1] > sleeps[0]


async def test_transient_errors_beyond_retries_fall_back() -> None:
    a = FakeProvider("a", [ProviderUnavailable("a", "503")] * 3)
    b = FakeProvider("b", ["from b"])

    resp = await make_router(a, b).complete("serve", REQ)

    assert resp.content == "from b"
    assert len(a.calls) == 3


async def test_rejection_is_not_retried_but_falls_back() -> None:
    a = FakeProvider("a", [ProviderRejected("a", 400, "logprobs unsupported")])
    b = FakeProvider("b", ["from b"])

    resp = await make_router(a, b).complete("serve", REQ)

    assert resp.content == "from b"
    assert len(a.calls) == 1


async def test_auth_rejection_opens_breaker_so_bad_key_is_not_retried() -> None:
    a = FakeProvider("a", [ProviderRejected("a", 401, "bad key")])
    b = FakeProvider("b", ["b1", "b2"])
    router = make_router(a, b)

    await router.complete("serve", REQ)
    await router.complete("serve", REQ)

    assert len(a.calls) == 1


async def test_all_providers_failing_raises_with_every_attempt() -> None:
    a = FakeProvider("a", [RateLimited("a", retry_after_s=5)])
    b = FakeProvider("b", [ProviderRejected("b", 400, "bad")])

    with pytest.raises(AllProvidersFailed) as err:
        await make_router(a, b).complete("serve", REQ)

    assert [(x.provider, x.outcome) for x in err.value.attempts] == [
        ("a", "rate_limited"),
        ("b", "rejected"),
    ]


async def test_rate_limit_on_one_model_does_not_block_other_models_of_same_provider() -> None:
    a = FakeProvider("a", [RateLimited("a", retry_after_s=60), "small ok"])
    router = LLMRouter(
        providers={"a": a},
        roles={
            "large": [ModelChoice(provider="a", model="big")],
            "small": [ModelChoice(provider="a", model="little")],
        },
        now=Clock(),
    )

    with pytest.raises(AllProvidersFailed):
        await router.complete("large", REQ)
    resp = await router.complete("small", REQ)

    assert resp.content == "small ok"
    assert a.calls == ["big", "little"]


async def test_auth_failure_blocks_every_model_of_that_provider() -> None:
    a = FakeProvider("a", [ProviderRejected("a", 401, "bad key")])
    b = FakeProvider("b", ["b ok"])
    router = LLMRouter(
        providers={"a": a, "b": b},
        roles={
            "one": [ModelChoice(provider="a", model="m1")],
            "two": [ModelChoice(provider="a", model="m2"), ModelChoice(provider="b", model="x")],
        },
        now=Clock(),
    )

    with pytest.raises(AllProvidersFailed):
        await router.complete("one", REQ)
    resp = await router.complete("two", REQ)

    assert a.calls == ["m1"]
    assert resp.attempts[0].outcome == "breaker_open"


async def test_unknown_role_is_an_error() -> None:
    with pytest.raises(KeyError, match="nope"):
        await make_router(FakeProvider("a", [])).complete("nope", REQ)
