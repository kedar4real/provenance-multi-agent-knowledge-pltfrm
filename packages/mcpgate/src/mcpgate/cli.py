"""mcpgate command line.

    mcpgate inspect --policy P [--caller C] -- <upstream command...>    # report, change nothing
    mcpgate approve --policy P -- <upstream command...>                 # (re)pin its tools
    mcpgate run     --policy P --caller C -- <upstream command...>      # serve over stdio

An upstream is a command speaking MCP over stdio (after `--`), or `--upstream-url` for a
Streamable HTTP server. A stdio upstream gets only a minimal environment plus the variables
the policy lists under `upstream_env`, so it doesn't inherit the client's secrets.
"""

import argparse
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import anyio
from mcp import Client, StdioServerParameters
from mcp.server.stdio import stdio_server

from mcpgate.audit import AuditLog
from mcpgate.pinning import PinStore, compare
from mcpgate.policy import Policy
from mcpgate.proxy import Gate, tool_dict
from mcpgate.scan import Classifier, blocking, scan_tool


def server_id(args: argparse.Namespace) -> str:
    if args.upstream_url:
        return str(args.upstream_url)
    return "stdio:" + " ".join(args.command)


@asynccontextmanager
async def connect(args: argparse.Namespace, policy: Policy) -> AsyncIterator[Client]:
    if args.upstream_url:
        target: Any = args.upstream_url
    else:
        if not args.command:
            raise SystemExit("give the upstream command after --, or --upstream-url")
        env = {k: os.environ[k] for k in policy.upstream_env if k in os.environ}
        target = StdioServerParameters(command=args.command[0], args=args.command[1:], env=env)
    async with Client(target, cache=None) as client:  # never serve a stale tool list
        yield client


def load_classifier(policy: Policy) -> Classifier | None:
    if not policy.classifier:
        return None
    from mcpgate.scan import TransformersClassifier

    return TransformersClassifier()


async def inspect(args: argparse.Namespace, policy: Policy) -> int:
    pins = PinStore(policy.pins).get(server_id(args))
    caller = policy.caller(args.caller)
    classifier = load_classifier(policy)
    async with connect(args, policy) as client:
        tools = [tool_dict(t) for t in (await client.list_tools()).tools]
    drift = compare(pins, tools) if pins else None
    problems = 0
    print(
        f"server: {server_id(args)}  ({'pinned ' + pins.approved_at if pins else 'not approved'})"
    )
    for tool in tools:
        name = str(tool["name"])
        findings = blocking(scan_tool(tool, classifier))
        status = []
        if not caller.allows(name):
            status.append(f"not allowed for {args.caller}")
        if drift and name in drift.changed:
            status.append("CHANGED since approval")
        if drift and name in drift.added:
            status.append("NEW since approval")
        if findings:
            status.append("POISONED: " + ", ".join(sorted({f.reason for f in findings})))
        problems += bool(findings) or bool(drift and name in drift.changed + drift.added)
        print(f"  {name:24} {'; '.join(status) or 'ok'}")
        for f in findings:
            print(f"      {f.where}: {f.reason}: {f.excerpt}")
    if drift and drift.removed:
        print(f"  removed since approval: {', '.join(drift.removed)}")
    return 1 if problems else 0


async def approve(args: argparse.Namespace, policy: Policy) -> int:
    async with connect(args, policy) as client:
        tools = [tool_dict(t) for t in (await client.list_tools()).tools]
    pins = PinStore(policy.pins).approve(server_id(args), tools)
    AuditLog(policy.audit).write("approved", server=server_id(args), tools=sorted(pins.tools))
    poisoned = [str(t["name"]) for t in tools if blocking(scan_tool(t))]
    print(f"pinned {len(pins.tools)} tools for {server_id(args)}")
    if poisoned:
        print(f"note: still blocked as poisoned whatever the pins say: {', '.join(poisoned)}")
    return 0


async def run(args: argparse.Namespace, policy: Policy) -> int:
    audit = AuditLog(policy.audit)
    async with connect(args, policy) as client:
        gate = Gate(client, server_id(args), policy, args.caller, PinStore(policy.pins), audit,
                    load_classifier(policy))  # fmt: skip
        server = gate.server()
        audit.write("started", caller=args.caller, server=server_id(args))
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())
    return 0


def main(argv: list[str] | None = None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    command: list[str] = []
    if "--" in argv:
        split = argv.index("--")
        argv, command = argv[:split], argv[split + 1 :]
    parser = argparse.ArgumentParser(prog="mcpgate", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)  # fmt: skip
    parser.add_argument("action", choices=["inspect", "approve", "run"])
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--caller", default="default")
    parser.add_argument("--upstream-url")
    args = parser.parse_args(argv)
    args.command = command
    policy = Policy.load(args.policy)
    action = {"inspect": inspect, "approve": approve, "run": run}[args.action]
    sys.exit(anyio.run(action, args, policy))


if __name__ == "__main__":
    main()
