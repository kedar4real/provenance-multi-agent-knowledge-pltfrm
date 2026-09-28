import json
import re
import time
from typing import Any

import httpx2
import openai
from openai import AsyncOpenAI

from provenance.llm.errors import ProviderRejected, ProviderUnavailable, RateLimited
from provenance.llm.types import ChatRequest, ChatResponse, TokenLogprob, ToolCall, Usage

_DURATION = re.compile(r"^\s*([\d.]+)s\s*$")


class OpenAICompatProvider:
    """Any provider exposing the OpenAI chat-completions API (Gemini, Groq, Mistral, ...).

    The SDK's own retries are disabled: the router owns retry and failover decisions, and
    silent SDK retries on 429 would hide rate limits and burn free-tier quota.
    """

    def __init__(
        self,
        name: str,
        base_url: str,
        api_key: str,
        timeout_s: float = 60.0,
        http_client: httpx2.AsyncClient | None = None,
    ) -> None:
        self.name = name
        self._client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout_s,
            max_retries=0,
            http_client=http_client,
        )

    async def complete(self, request: ChatRequest, model: str) -> ChatResponse:
        started = time.perf_counter()
        try:
            raw = await self._client.chat.completions.create(**_payload(request, model))
        except openai.RateLimitError as e:
            raise RateLimited(self.name, _retry_after_s(e.response)) from e
        except (openai.APIConnectionError, openai.InternalServerError) as e:
            raise ProviderUnavailable(self.name, type(e).__name__) from e
        except openai.APIStatusError as e:
            if e.status_code >= 500:
                raise ProviderUnavailable(self.name, f"HTTP {e.status_code}") from e
            raise ProviderRejected(self.name, e.status_code, _error_message(e.response)) from e
        return _parse(raw, self.name, model, (time.perf_counter() - started) * 1000)


def _payload(request: ChatRequest, model: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "messages": [m.model_dump(exclude_none=True) for m in request.messages],
        "temperature": request.temperature,
    }
    if request.max_tokens is not None:
        payload["max_tokens"] = request.max_tokens
    if request.tools:
        payload["tools"] = request.tools
    if request.json_mode:
        payload["response_format"] = {"type": "json_object"}
    if request.logprobs:
        payload["logprobs"] = True
        if request.top_logprobs:
            payload["top_logprobs"] = request.top_logprobs
    if request.seed is not None:
        payload["seed"] = request.seed
    return payload


def _parse(raw: Any, provider: str, model: str, latency_ms: float) -> ChatResponse:
    choice = raw.choices[0]
    msg = choice.message
    tool_calls = [
        ToolCall(id=c.id, name=c.function.name, arguments=_decode_args(c.function.arguments))
        for c in msg.tool_calls or []
    ]
    logprobs = [
        TokenLogprob(
            token=t.token,
            logprob=t.logprob,
            top={alt.token: alt.logprob for alt in (t.top_logprobs or [])},
        )
        for t in (choice.logprobs.content if choice.logprobs and choice.logprobs.content else [])
    ]
    usage = Usage(
        input_tokens=raw.usage.prompt_tokens if raw.usage else 0,
        output_tokens=raw.usage.completion_tokens if raw.usage else 0,
    )
    return ChatResponse(
        content=msg.content or "",
        provider=provider,
        model=model,
        usage=usage,
        latency_ms=latency_ms,
        tool_calls=tool_calls,
        logprobs=logprobs,
    )


def _decode_args(arguments: str) -> dict[str, Any]:
    try:
        decoded = json.loads(arguments or "{}")
    except json.JSONDecodeError:
        return {"_unparsed": arguments}
    return decoded if isinstance(decoded, dict) else {"_value": decoded}


def _retry_after_s(response: Any) -> float | None:
    header = response.headers.get("retry-after")
    if header:
        try:
            return float(header)
        except ValueError:
            pass
    body = _json_body(response)
    errors = body if isinstance(body, list) else [body]
    for err in errors:
        details = err.get("error", {}).get("details", []) if isinstance(err, dict) else []
        for detail in details:
            if str(detail.get("@type", "")).endswith("RetryInfo"):
                match = _DURATION.match(str(detail.get("retryDelay", "")))
                if match:
                    return float(match.group(1))
    return None


def _error_message(response: Any) -> str:
    body = _json_body(response)
    first = body[0] if isinstance(body, list) and body else body
    if isinstance(first, dict):
        err = first.get("error", first)
        if isinstance(err, dict) and "message" in err:
            return str(err["message"])[:300]
    return str(body)[:300]


def _json_body(response: Any) -> Any:
    try:
        return response.json()
    except (ValueError, AttributeError):
        return {}
