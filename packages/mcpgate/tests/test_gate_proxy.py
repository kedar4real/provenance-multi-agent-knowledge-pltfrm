"""The gate end to end, in process: client -> Gate -> the evil fixture server."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from evil_server import build_evil_server
from mcp import Client
from mcpgate.audit import AuditLog
from mcpgate.pinning import PinStore
from mcpgate.policy import CallerPolicy, Policy, RateLimit
from mcpgate.proxy import Gate


def policy(tmp_path: Path, **overrides: Any) -> Policy:
    base: dict[str, Any] = {
        "callers": {"desk": CallerPolicy(tools=["*"])},
        "pins": tmp_path / "pins.json",
        "audit": tmp_path / "audit.jsonl",
    }
    return Policy(**(base | overrides))


@asynccontextmanager
async def gated(
    p: Policy, caller: str = "desk", rug_pull_after: int = 1
) -> AsyncIterator[tuple[Client, Gate]]:
    async with Client(build_evil_server(rug_pull_after), cache=None) as upstream:
        gate = Gate(upstream, "evil", p, caller, PinStore(p.pins), AuditLog(p.audit))
        async with Client(gate.server(), cache=None) as client:
            yield client, gate


def text(result: Any) -> str:
    return " ".join(c.text for c in result.content)


async def test_poisoned_and_shadowing_tools_are_hidden_and_refused(tmp_path: Path) -> None:
    async with gated(policy(tmp_path)) as (client, gate):
        listed = {t.name for t in (await client.list_tools()).tools}
        refused = await client.call_tool("add", {"a": 1, "b": 2, "sidenote": "x"})

    assert "add" not in listed and "send_email" not in listed
    assert {"get_weather"} <= listed
    assert refused.is_error and "hidden instructions" in text(refused)
    assert "sensitive_files" in gate.refused["add"]


async def test_a_rug_pull_is_blocked_on_the_next_listing_and_on_calls(tmp_path: Path) -> None:
    async with gated(policy(tmp_path), rug_pull_after=1) as (client, gate):
        # The gate's first vet pins the clean definition (trust on first use)...
        first = {t.name for t in (await client.list_tools()).tools}
        # ...then the server swaps in a poisoned description.
        second = {t.name for t in (await client.list_tools()).tools}
        call = await client.call_tool("translate", {"text": "hola"})

    assert "translate" in first and "translate" not in second
    assert call.is_error and "possible rug pull" in text(call)
    events = [e["event"] for e in gate.audit.events]
    assert "drift" in events and "rug_pull_suspected" in events


async def test_the_pin_survives_restarts_so_a_later_change_is_still_caught(tmp_path: Path) -> None:
    p = policy(tmp_path)
    async with gated(p, rug_pull_after=99) as (client, _):
        await client.list_tools()  # pins the clean tools
    async with gated(p, rug_pull_after=0) as (client, _):  # a new session, already changed
        listed = {t.name for t in (await client.list_tools()).tools}

    assert "translate" not in listed


async def test_injected_output_is_redacted_flagged_or_blocked_per_policy(tmp_path: Path) -> None:
    results = {}
    for mode in ("redact", "warn", "block", "off"):
        async with gated(policy(tmp_path / mode, outputs=mode)) as (client, _):
            results[mode] = await client.call_tool("get_weather", {"city": "Pune"})

    assert "withheld" in text(results["redact"]) and "IGNORE" not in text(results["redact"])
    assert not results["redact"].is_error
    assert text(results["warn"]).startswith("[mcpgate]") and "IGNORE" in text(results["warn"])
    assert results["block"].is_error and "IGNORE" not in text(results["block"])
    assert "IGNORE" in text(results["off"])


async def test_callers_see_only_their_allowlist(tmp_path: Path) -> None:
    p = policy(tmp_path, callers={"kiosk": CallerPolicy(tools=["get_weather"])})
    async with gated(p, caller="kiosk") as (client, _):
        listed = {t.name for t in (await client.list_tools()).tools}
        call = await client.call_tool("translate", {"text": "hola"})
    async with gated(p, caller="stranger") as (client, _):
        nothing = (await client.list_tools()).tools

    assert listed == {"get_weather"} and call.is_error and "not permitted" in text(call)
    assert nothing == []


async def test_rate_limits_refuse_calls_beyond_the_window(tmp_path: Path) -> None:
    p = policy(tmp_path, callers={"desk": CallerPolicy(
        tools=["*"], rate_limit=RateLimit(calls=2, window_s=60))})  # fmt: skip
    async with gated(p) as (client, _):
        calls = [await client.call_tool("get_weather", {"city": "x"}) for _ in range(3)]

    assert not any(c.is_error for c in calls[:2])
    assert calls[2].is_error and "Rate limit" in text(calls[2])


async def test_require_approval_blocks_an_unknown_server(tmp_path: Path) -> None:
    async with gated(policy(tmp_path, first_use="require_approval")) as (client, gate):
        listed = (await client.list_tools()).tools

    assert listed == [] and "not been approved" in gate.refused["get_weather"]


async def test_every_decision_is_in_the_jsonl_audit(tmp_path: Path) -> None:
    p = policy(tmp_path)
    async with gated(p) as (client, _):
        await client.list_tools()
        await client.call_tool("add", {"a": 1, "b": 2})
        await client.call_tool("get_weather", {"city": "Pune"})

    lines = (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()
    events = [line.split('"event": "')[1].split('"')[0] for line in lines]
    for expected in ("pinned", "poisoned_tool", "list_tools", "call_refused", "output_flagged"):
        assert expected in events
