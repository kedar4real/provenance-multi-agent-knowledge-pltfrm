from typing import Any, Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[dict[str, Any]] | None = None


class ChatRequest(BaseModel):
    messages: list[Message]
    temperature: float = 0.0
    max_tokens: int | None = None
    tools: list[dict[str, Any]] | None = None
    json_mode: bool = False
    logprobs: bool = False
    top_logprobs: int | None = None
    seed: int | None = None
    # Reasoning models (gpt-oss, Gemini) spend hidden tokens thinking; "low" suits simple
    # structured tasks such as judging. Not every model accepts it (Groq's qwen rejects "low").
    reasoning_effort: Literal["low", "medium", "high"] | None = None


class Usage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    # Input tokens the provider served from its prompt cache (a subset of input_tokens).
    cached_input_tokens: int = 0


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict[str, Any]


class TokenLogprob(BaseModel):
    token: str
    logprob: float
    top: dict[str, float] = Field(default_factory=dict)


class Attempt(BaseModel):
    """One provider attempt within a routed call, kept for the audit trail."""

    provider: str
    model: str
    outcome: Literal["ok", "rate_limited", "unavailable", "rejected", "breaker_open"]
    detail: str = ""
    latency_ms: float = 0.0


class ChatResponse(BaseModel):
    content: str
    provider: str
    model: str
    usage: Usage
    latency_ms: float
    tool_calls: list[ToolCall] = Field(default_factory=list)
    logprobs: list[TokenLogprob] = Field(default_factory=list)
    attempts: list[Attempt] = Field(default_factory=list)
    cache_hit: bool = False
