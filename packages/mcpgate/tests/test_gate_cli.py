"""The real command line over real stdio: client -> `mcpgate run` process -> evil server process."""

import os
import subprocess
import sys
from pathlib import Path

from conftest import FIXTURES
from mcp import Client, StdioServerParameters

EVIL = [sys.executable, str(FIXTURES / "evil_server.py")]


def write_policy(tmp_path: Path) -> Path:
    policy = tmp_path / "mcpgate.yaml"
    policy.write_text(
        "callers:\n  desk:\n    tools: ['*']\n"
        "pins: pins.json\naudit: audit.jsonl\nupstream_env: [EVIL_RUG_PULL_AFTER]\n",
        encoding="utf-8",
    )
    return policy


def mcpgate(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "mcpgate.cli", *args], capture_output=True, text=True, timeout=60,
        env=os.environ | (env or {}),
    )  # fmt: skip


def test_inspect_names_every_attack_and_fails(tmp_path: Path) -> None:
    out = mcpgate(
        "inspect", "--policy", str(write_policy(tmp_path)), "--caller", "desk", "--", *EVIL
    )

    assert out.returncode == 1, out.stderr
    lines = {line.split()[0]: line for line in out.stdout.splitlines()[1:] if line.startswith("  ")}
    assert "POISONED" in lines["add"] and "POISONED" in lines["send_email"]
    assert lines["get_weather"].strip().endswith("ok")
    assert not (tmp_path / "pins.json").exists()  # inspect changes nothing


def test_approve_pins_then_inspect_reports_the_rug_pull(tmp_path: Path) -> None:
    policy = str(write_policy(tmp_path))
    approved = mcpgate("approve", "--policy", policy, "--", *EVIL)
    # Same server, same command line; it has since changed its tool (the variable reaches it
    # only because the policy passes it through).
    changed = mcpgate("inspect", "--policy", policy, "--caller", "desk", "--", *EVIL,
                      env={"EVIL_RUG_PULL_AFTER": "0"})  # fmt: skip

    assert approved.returncode == 0 and "pinned 4 tools" in approved.stdout
    assert "still blocked as poisoned" in approved.stdout
    assert changed.returncode == 1 and "CHANGED since approval" in changed.stdout


async def test_run_serves_only_safe_tools_to_a_real_stdio_client(tmp_path: Path) -> None:
    gate = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcpgate.cli", "run", "--policy", str(write_policy(tmp_path)),
              "--caller", "desk", "--", *EVIL],
        env={"EVIL_RUG_PULL_AFTER": "99"},
    )  # fmt: skip
    async with Client(gate, cache=None) as client:
        listed = {t.name for t in (await client.list_tools()).tools}
        weather = await client.call_tool("get_weather", {"city": "Pune"})

    assert listed == {"get_weather", "translate"}
    assert "withheld" in weather.content[0].text  # type: ignore[union-attr]
    assert (tmp_path / "audit.jsonl").exists() and (tmp_path / "pins.json").exists()
