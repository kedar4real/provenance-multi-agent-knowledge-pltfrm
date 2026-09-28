"""Live smoke test of the LLM layer: one tiny call per role, logprob support, and failover.

uv run python scripts/llm_smoke.py
"""

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

from provenance.llm.errors import AllProvidersFailed
from provenance.llm.factory import api_equivalent_cost_usd, build_router, load_config
from provenance.llm.router import LLMRouter, ModelChoice
from provenance.llm.types import ChatRequest, Message

load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]

ASK = ChatRequest(
    messages=[Message(role="user", content="Reply with exactly one word: the capital of France.")],
    max_tokens=400,
)
YES_NO = ChatRequest(
    messages=[Message(role="user", content="Is 7 a prime number? Answer only Yes or No.")],
    max_tokens=5,
    logprobs=True,
    top_logprobs=2,
)


async def main() -> None:
    config = load_config(Path("config/llm.yaml"))
    router = build_router(config)

    print("== one call per role ==")
    for role in config.roles:
        try:
            resp = await router.complete(role, ASK)
        except AllProvidersFailed as e:
            print(f"{role:<12} FAILED: {e}")
            continue
        fell_back = [f"{a.provider}:{a.outcome}" for a in resp.attempts if a.outcome != "ok"]
        cost = api_equivalent_cost_usd(config, role, resp.usage)
        print(
            f"{role:<12} {resp.provider}/{resp.model:<24} -> {resp.content.strip()[:30]!r:<12} "
            f"tokens {resp.usage.input_tokens}/{resp.usage.output_tokens} "
            f"{resp.latency_ms:.0f}ms  api-equiv ${cost:.6f}"
            + (f"  (fell back past {', '.join(fell_back)})" if fell_back else "")
        )

    print("\n== logprob support (constrained Yes/No) ==")
    for role in ("serve_small", "bulk"):
        for provider, model in router.chain(role):
            single = LLMRouter(
                providers=router._providers,
                roles={"x": [ModelChoice(provider=provider, model=model)]},
            )
            try:
                resp = await single.complete("x", YES_NO)
                first = resp.logprobs[0] if resp.logprobs else None
                shown = f"{first.token!r} {first.logprob:.4f} top={first.top}" if first else "none"
                print(f"{provider}/{model:<24} answer={resp.content.strip()!r} logprobs: {shown}")
            except Exception as e:
                print(f"{provider}/{model:<24} ERROR {str(e)[:120]}")

    print("\n== failover: first choice is a model that doesn't exist ==")
    broken = LLMRouter(
        providers=router._providers,
        roles={
            "demo": [
                ModelChoice(provider="gemini", model="gemini-does-not-exist"),
                ModelChoice(provider="groq", model="openai/gpt-oss-20b"),
            ]
        },
    )
    resp = await broken.complete("demo", ASK)
    for a in resp.attempts:
        print(f"  attempt {a.provider}/{a.model}: {a.outcome} {a.detail[:90]}")
    print(f"  answered by {resp.provider}: {resp.content.strip()!r}")


if __name__ == "__main__":
    asyncio.run(main())
