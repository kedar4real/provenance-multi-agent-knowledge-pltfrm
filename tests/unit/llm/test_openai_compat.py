from typing import Any

import httpx2
import pytest

from provenance.llm.errors import ProviderRejected, ProviderUnavailable, RateLimited
from provenance.llm.openai_compat import OpenAICompatProvider
from provenance.llm.types import ChatRequest, Message

BASE = "https://llm.test/v1"
URL = f"{BASE}/chat/completions"


def completion(message: dict[str, object], **extra: object) -> dict[str, object]:
    return {
        "id": "c1",
        "object": "chat.completion",
        "created": 0,
        "model": "m1",
        "choices": [{"index": 0, "message": message, "finish_reason": "stop", **extra}],
        "usage": {"prompt_tokens": 12, "completion_tokens": 3, "total_tokens": 15},
    }


class FakeServer:
    """Answers every request with the configured response (or raises the configured error)."""

    def __init__(self) -> None:
        self.response = httpx2.Response(500)
        self.error: Exception | None = None
        self.requests: list[httpx2.Request] = []

    def respond(self, status: int, json: Any = None, headers: dict[str, str] | None = None) -> None:
        self.response = httpx2.Response(status, json=json, headers=headers)

    def fail(self, error: Exception) -> None:
        self.error = error

    def handle(self, request: httpx2.Request) -> httpx2.Response:
        self.requests.append(request)
        if self.error is not None:
            raise self.error
        return self.response


@pytest.fixture
def http() -> FakeServer:
    return FakeServer()


@pytest.fixture
def provider(http: FakeServer) -> OpenAICompatProvider:
    client = httpx2.AsyncClient(transport=httpx2.MockTransport(http.handle))
    return OpenAICompatProvider(
        name="p1", base_url=BASE, api_key="k", timeout_s=5, http_client=client
    )


REQ = ChatRequest(messages=[Message(role="user", content="hi")])


async def test_parses_text_answer_and_token_usage(
    provider: OpenAICompatProvider, http: FakeServer
) -> None:
    http.respond(200, json=completion({"role": "assistant", "content": "hello"}))

    resp = await provider.complete(REQ, model="m1")

    assert resp.content == "hello"
    assert (resp.usage.input_tokens, resp.usage.output_tokens) == (12, 3)
    assert (resp.provider, resp.model) == ("p1", "m1")
    assert resp.latency_ms >= 0


async def test_parses_tool_calls_with_decoded_arguments(
    provider: OpenAICompatProvider, http: FakeServer
) -> None:
    call = {"id": "t1", "type": "function", "function": {"name": "lookup", "arguments": '{"x": 1}'}}
    http.respond(200, json=completion({"role": "assistant", "content": None, "tool_calls": [call]}))

    resp = await provider.complete(REQ, model="m1")

    assert resp.content == ""
    assert [(t.id, t.name, t.arguments) for t in resp.tool_calls] == [("t1", "lookup", {"x": 1})]


async def test_requests_and_parses_token_logprobs(
    provider: OpenAICompatProvider, http: FakeServer
) -> None:
    logprobs = {"content": [{"token": "Yes", "logprob": -0.1, "bytes": None, "top_logprobs": []}]}
    http.respond(200, json=completion({"role": "assistant", "content": "Yes"}, logprobs=logprobs))

    resp = await provider.complete(REQ.model_copy(update={"logprobs": True}), model="m1")

    assert b'"logprobs":true' in http.requests[-1].content.replace(b" ", b"")
    assert [(t.token, t.logprob) for t in resp.logprobs] == [("Yes", -0.1)]


async def test_gemini_style_429_exposes_retry_delay(
    provider: OpenAICompatProvider, http: FakeServer
) -> None:
    body = [
        {
            "error": {
                "code": 429,
                "status": "RESOURCE_EXHAUSTED",
                "details": [
                    {"@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": "28s"}
                ],
            }
        }
    ]
    http.respond(429, json=body)

    with pytest.raises(RateLimited) as err:
        await provider.complete(REQ, model="m1")

    assert err.value.retry_after_s == 28.0
    assert err.value.provider == "p1"


async def test_429_with_retry_after_header(
    provider: OpenAICompatProvider, http: FakeServer
) -> None:
    http.respond(429, headers={"retry-after": "7"}, json={"error": {"message": "slow"}})

    with pytest.raises(RateLimited) as err:
        await provider.complete(REQ, model="m1")

    assert err.value.retry_after_s == 7.0


async def test_429_without_hint_has_no_retry_delay(
    provider: OpenAICompatProvider, http: FakeServer
) -> None:
    http.respond(429, json={"error": {"message": "slow down"}})

    with pytest.raises(RateLimited) as err:
        await provider.complete(REQ, model="m1")

    assert err.value.retry_after_s is None


@pytest.mark.parametrize("status", [500, 502, 503])
async def test_server_errors_are_transient(
    provider: OpenAICompatProvider, http: FakeServer, status: int
) -> None:
    http.respond(status, json={"error": {"message": "down"}})

    with pytest.raises(ProviderUnavailable):
        await provider.complete(REQ, model="m1")


async def test_timeouts_are_transient(provider: OpenAICompatProvider, http: FakeServer) -> None:
    http.fail(httpx2.ReadTimeout("slow"))

    with pytest.raises(ProviderUnavailable):
        await provider.complete(REQ, model="m1")


@pytest.mark.parametrize("status", [400, 401, 404])
async def test_client_errors_are_rejections_with_status(
    provider: OpenAICompatProvider, http: FakeServer, status: int
) -> None:
    http.respond(status, json={"error": {"message": "nope"}})

    with pytest.raises(ProviderRejected) as err:
        await provider.complete(REQ, model="m1")

    assert err.value.status == status
