"""Rug-pull detection: pin a fingerprint of every tool a server offers, and refuse tools whose
definition changes (or that appear) until a person re-approves them.

A rug pull is a server that passes review with harmless tools and later changes a tool's
description or schema to carry instructions. Clients usually re-read tool lists silently, so
nothing but a pinned fingerprint notices. Fingerprints cover everything the model reads.
"""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

PINNED_FIELDS = ("name", "title", "description", "inputSchema", "outputSchema", "annotations")


def fingerprint(tool: dict[str, Any]) -> str:
    canonical = {k: tool.get(k) for k in PINNED_FIELDS}
    blob = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode()).hexdigest()


class Drift(BaseModel):
    changed: list[str] = Field(default_factory=list)
    added: list[str] = Field(default_factory=list)
    removed: list[str] = Field(default_factory=list)

    @property
    def any(self) -> bool:
        return bool(self.changed or self.added or self.removed)


class ServerPins(BaseModel):
    tools: dict[str, str]
    approved_at: str


class PinStore:
    """Pins per upstream server, in one JSON file written atomically."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def _load(self) -> dict[str, ServerPins]:
        if not self.path.exists():
            return {}
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return {k: ServerPins.model_validate(v) for k, v in raw.items()}

    def get(self, server: str) -> ServerPins | None:
        return self._load().get(server)

    def approve(self, server: str, tools: list[dict[str, Any]]) -> ServerPins:
        pins = ServerPins(
            tools={str(t["name"]): fingerprint(t) for t in tools},
            approved_at=datetime.now(UTC).isoformat(timespec="seconds"),
        )
        everything = self._load()
        everything[server] = pins
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps({k: v.model_dump() for k, v in everything.items()}, indent=2) + "\n",
            encoding="utf-8",
        )
        tmp.replace(self.path)
        return pins


def compare(pins: ServerPins, tools: list[dict[str, Any]]) -> Drift:
    current = {str(t["name"]): fingerprint(t) for t in tools}
    return Drift(
        changed=sorted(n for n, h in current.items() if n in pins.tools and pins.tools[n] != h),
        added=sorted(n for n in current if n not in pins.tools),
        removed=sorted(n for n in pins.tools if n not in current),
    )
