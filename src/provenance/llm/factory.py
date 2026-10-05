import os
from collections.abc import Callable, Mapping
from pathlib import Path

import httpx2
import yaml
from pydantic import BaseModel

from provenance.llm.openai_compat import OpenAICompatProvider
from provenance.llm.router import LLMRouter, ModelChoice, Provider
from provenance.llm.types import Usage


class ProviderSpec(BaseModel):
    base_url: str
    api_key_env: str
    timeout_s: float = 60.0


class PriceClass(BaseModel):
    input_per_mtok: float
    output_per_mtok: float
    reference: str
    # Prompt-cache reads; defaults to the full input price for providers without caching.
    cached_input_per_mtok: float | None = None


class RoleSpec(BaseModel):
    price_class: str
    chain: list[ModelChoice]


class LLMConfig(BaseModel):
    providers: dict[str, ProviderSpec]
    price_classes: dict[str, PriceClass]
    roles: dict[str, RoleSpec]


def load_config(path: Path) -> LLMConfig:
    return LLMConfig.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def build_router(
    config: LLMConfig,
    env: Mapping[str, str] | None = None,
    http_client: httpx2.AsyncClient | None = None,
) -> LLMRouter:
    """Builds the router from providers whose API key is present; the rest are dropped."""
    env = os.environ if env is None else env
    providers: dict[str, Provider] = {
        name: OpenAICompatProvider(
            name=name,
            base_url=spec.base_url,
            api_key=env[spec.api_key_env],
            timeout_s=spec.timeout_s,
            http_client=http_client,
        )
        for name, spec in config.providers.items()
        if env.get(spec.api_key_env)
    }
    roles: dict[str, list[ModelChoice]] = {}
    for role, spec in config.roles.items():
        usable = [c for c in spec.chain if c.provider in providers]
        if not usable:
            wanted = ", ".join(sorted({c.provider for c in spec.chain}))
            raise ValueError(f"role '{role}' has no provider with an API key set (needs: {wanted})")
        roles[role] = usable
    return LLMRouter(providers=providers, roles=roles)


def api_equivalent_cost_usd(config: LLMConfig, role: str, usage: Usage) -> float:
    """What this call would cost at the reference list price of its role's tier.

    All real calls run on free tiers; this is the comparable-hosted-model cost used for the
    routed-vs-baseline cost comparison.
    """
    price = config.price_classes[config.roles[role].price_class]
    cached = min(usage.cached_input_tokens, usage.input_tokens)
    cached_price = (
        price.input_per_mtok
        if price.cached_input_per_mtok is None
        else (price.cached_input_per_mtok)
    )
    return (
        (usage.input_tokens - cached) * price.input_per_mtok
        + cached * cached_price
        + usage.output_tokens * price.output_per_mtok
    ) / 1_000_000


def cost_function(config: LLMConfig) -> Callable[[str, Usage], float]:
    """Per-call API-equivalent cost; zero for roles the config doesn't price (test models)."""

    def cost(role: str, usage: Usage) -> float:
        return api_equivalent_cost_usd(config, role, usage) if role in config.roles else 0.0

    return cost
