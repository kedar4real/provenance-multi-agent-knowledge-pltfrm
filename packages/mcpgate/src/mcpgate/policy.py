"""The gate's policy, from YAML: who may call which tools, and what to do about findings.

    callers:
      claude-desktop:
        tools: [whoami, search_filings, get_passage, ask]   # or ["*"]
        rate_limit: {calls: 30, window_s: 60}
    descriptions: block        # tool-poisoning findings: block | warn
    outputs: redact            # injection found in a tool's output: redact | warn | block | off
    first_use: trust           # an unknown server's tools: trust (and pin) | require_approval
    on_drift: block            # a pinned tool changed or a new one appeared: block | warn
    pins: .mcpgate/pins.json
    audit: .mcpgate/audit.jsonl
    upstream_env: [PROVENANCE_API_KEY]   # environment passed to a stdio upstream
    classifier: false          # add the local injection classifier (mcpgate[classifier])

Deny by default: a caller not in the policy, or a tool not in its list, is refused.
"""

import fnmatch
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class RateLimit(BaseModel):
    calls: int = Field(gt=0)
    window_s: float = Field(gt=0)


class CallerPolicy(BaseModel):
    tools: list[str] = Field(default_factory=list)  # names or glob patterns
    rate_limit: RateLimit | None = None

    def allows(self, tool: str) -> bool:
        return any(fnmatch.fnmatchcase(tool, pattern) for pattern in self.tools)


class Policy(BaseModel):
    callers: dict[str, CallerPolicy]
    descriptions: Literal["block", "warn"] = "block"
    outputs: Literal["redact", "warn", "block", "off"] = "redact"
    first_use: Literal["trust", "require_approval"] = "trust"
    on_drift: Literal["block", "warn"] = "block"
    pins: Path = Path(".mcpgate/pins.json")
    audit: Path = Path(".mcpgate/audit.jsonl")
    upstream_env: list[str] = Field(default_factory=list)
    classifier: bool = False

    @classmethod
    def load(cls, path: Path) -> "Policy":
        policy = cls.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
        # Relative paths are relative to the policy file, not wherever the client launched us.
        base = path.resolve().parent
        return policy.model_copy(update={
            "pins": policy.pins if policy.pins.is_absolute() else base / policy.pins,
            "audit": policy.audit if policy.audit.is_absolute() else base / policy.audit,
        })  # fmt: skip

    def caller(self, name: str) -> CallerPolicy:
        return self.callers.get(name, CallerPolicy())  # unknown caller: no tools
