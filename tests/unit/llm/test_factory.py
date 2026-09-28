from pathlib import Path

import pytest

from provenance.llm.factory import LLMConfig, api_equivalent_cost_usd, build_router, load_config
from provenance.llm.types import Usage

CONFIG = """
providers:
  alpha: {base_url: "https://alpha.test/v1", api_key_env: ALPHA_KEY}
  beta: {base_url: "https://beta.test/v1", api_key_env: BETA_KEY}
price_classes:
  small: {input_per_mtok: 1.0, output_per_mtok: 5.0, reference: "test"}
roles:
  serve:
    price_class: small
    chain:
      - {provider: alpha, model: a-1}
      - {provider: beta, model: b-1}
"""


@pytest.fixture
def config(tmp_path: Path) -> LLMConfig:
    path = tmp_path / "llm.yaml"
    path.write_text(CONFIG)
    return load_config(path)


def test_loads_roles_in_chain_order(config: LLMConfig) -> None:
    assert [c.provider for c in config.roles["serve"].chain] == ["alpha", "beta"]


def test_providers_without_a_key_are_left_out_of_every_chain(config: LLMConfig) -> None:
    router = build_router(config, env={"BETA_KEY": "b"})

    assert router.chain("serve") == [("beta", "b-1")]


def test_role_with_no_usable_provider_is_reported(config: LLMConfig) -> None:
    with pytest.raises(ValueError, match="serve"):
        build_router(config, env={})


def test_api_equivalent_cost_uses_role_price_class(config: LLMConfig) -> None:
    usage = Usage(input_tokens=1_000_000, output_tokens=200_000)

    assert api_equivalent_cost_usd(config, "serve", usage) == pytest.approx(1.0 + 1.0)


def test_repo_config_is_valid() -> None:
    config = load_config(Path("config/llm.yaml"))

    assert {"serve_small", "serve_large", "bulk", "judge"} <= set(config.roles)
