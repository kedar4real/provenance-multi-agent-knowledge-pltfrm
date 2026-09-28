from provenance.llm.types import Attempt


class LLMError(Exception):
    """Base for provider failures, normalized across vendors."""

    def __init__(self, provider: str, message: str) -> None:
        super().__init__(f"[{provider}] {message}")
        self.provider = provider


class RateLimited(LLMError):
    def __init__(self, provider: str, retry_after_s: float | None = None) -> None:
        hint = f"retry after {retry_after_s:g}s" if retry_after_s is not None else "no retry hint"
        super().__init__(provider, f"rate limited ({hint})")
        self.retry_after_s = retry_after_s


class ProviderUnavailable(LLMError):
    """Transient: server error, timeout or connection failure. Safe to retry."""

    def __init__(self, provider: str, reason: str) -> None:
        super().__init__(provider, f"unavailable: {reason}")


class ProviderRejected(LLMError):
    """The provider refused this request (4xx other than 429). Retrying won't help."""

    def __init__(self, provider: str, status: int, message: str) -> None:
        super().__init__(provider, f"rejected with {status}: {message}")
        self.status = status


class AllProvidersFailed(Exception):
    def __init__(self, role: str, attempts: list[Attempt]) -> None:
        tried = ", ".join(f"{a.provider}:{a.outcome}" for a in attempts)
        super().__init__(f"every provider for role '{role}' failed ({tried})")
        self.role = role
        self.attempts = attempts
