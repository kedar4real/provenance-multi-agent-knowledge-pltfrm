"""The controller's decisions as pure functions of config/routing.yaml and measured facts.

No I/O and no model calls: the executor gathers the facts (queue depth, verification,
calibrated confidence, tokens spent) and these functions decide. Each decision returns its
reason, which ends up in the trace, the metrics and the audit trail.
"""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

from provenance.controller.classifier import Classification

Tier = Literal["small", "large"]


class RoutingConfig(BaseModel):
    enabled: bool = True
    default_tier: Tier = "large"


class TierConfig(BaseModel):
    write_roles: list[str] = Field(min_length=1)


class EscalateConfig(BaseModel):
    on_failed_verification: bool = True
    on_decline_with_evidence: bool = True
    below_confidence: float = Field(0.5, ge=0, le=1)


class AbstainConfig(BaseModel):
    below_confidence: float = Field(0.3, ge=0, le=1)


class CacheConfig(BaseModel):
    enabled: bool = True
    version: int = 1
    similarity: float = Field(0.95, gt=0, le=1)
    entity_guard: bool = True
    ttl_s: int = Field(86400, gt=0)


class BudgetConfig(BaseModel):
    request_tokens: int = Field(30000, gt=0)
    principal_daily_tokens: int = Field(500000, gt=0)


class BackpressureConfig(BaseModel):
    max_concurrent: int = Field(4, gt=0)
    max_waiting: int = Field(16, ge=0)
    wait_timeout_s: float = Field(30, gt=0)


class Policy(BaseModel):
    routing: RoutingConfig = RoutingConfig()
    tiers: dict[Tier, TierConfig]
    escalate: EscalateConfig = EscalateConfig()
    abstain: AbstainConfig = AbstainConfig()
    cache: CacheConfig = CacheConfig()
    budgets: BudgetConfig = BudgetConfig()
    backpressure: BackpressureConfig = BackpressureConfig()

    @classmethod
    def load(cls, path: Path) -> "Policy":
        return cls.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


class Admission(BaseModel):
    admitted: bool
    reason: str = ""
    retry_after_s: int | None = None


class RunFacts(BaseModel):
    """What the executor measured about one agent run."""

    tier: Tier
    declined: bool
    evidence_count: int
    verified: bool | None  # None: nothing to verify (a decline)
    confidence: float | None  # calibrated; None without a calibrator
    tokens_used: int


def admit(waiting: int, config: BackpressureConfig) -> Admission:
    """Called when no run slot is free: queue the request, or shed it right away."""
    if waiting >= config.max_waiting:
        return Admission(
            admitted=False, reason="queue_full", retry_after_s=int(config.wait_timeout_s)
        )
    return Admission(admitted=True)


def select_tier(classification: Classification, policy: Policy) -> tuple[Tier, list[str]]:
    if not policy.routing.enabled:
        return policy.routing.default_tier, ["routing_off"]
    if classification.complex:
        return policy.routing.default_tier, classification.reasons
    return "small", ["simple"]


def should_escalate(facts: RunFacts, policy: Policy) -> str | None:
    if facts.tier != "small":
        return None
    rules = policy.escalate
    if rules.on_failed_verification and facts.verified is False:
        return "failed_verification"
    if rules.on_decline_with_evidence and facts.declined and facts.evidence_count > 0:
        return "declined_with_evidence"
    if facts.confidence is not None and facts.confidence < rules.below_confidence:
        return "low_confidence"
    return None


def should_abstain(facts: RunFacts, policy: Policy) -> str | None:
    """Only on calibrated confidence: an uncalibrated score is not a probability, and
    acting on it is exactly the failure calibration exists to prevent."""
    if facts.declined or facts.confidence is None:
        return None
    if facts.confidence < policy.abstain.below_confidence:
        return "low_confidence"
    return None


def check_budget(spent: int, limit: int) -> int:
    """Tokens left; zero or less means the budget is spent."""
    return limit - spent


def escalation_fits(facts: RunFacts, policy: Policy) -> bool:
    """An escalation repeats roughly the run's writing cost on the large tier, so it is
    skipped when that would take the request past its token budget."""
    return facts.tokens_used * 2 <= policy.budgets.request_tokens
