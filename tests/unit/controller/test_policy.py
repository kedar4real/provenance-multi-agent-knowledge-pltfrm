"""The controller's pure decisions: classification, tiers, escalation, abstention, budgets."""

from provenance.config import REPO_ROOT
from provenance.controller.classifier import classify, entities
from provenance.controller.policy import (
    BackpressureConfig,
    Policy,
    RunFacts,
    admit,
    check_budget,
    escalation_fits,
    select_tier,
    should_abstain,
    should_escalate,
)

POLICY = Policy.load(REPO_ROOT / "config" / "routing.yaml")


def facts(**overrides: object) -> RunFacts:
    base: dict[str, object] = {
        "tier": "small", "declined": False, "evidence_count": 3, "verified": True,
        "confidence": None, "tokens_used": 2000,
    }  # fmt: skip
    return RunFacts.model_validate(base | overrides)


def test_entities_find_companies_by_name_alias_or_ticker_years_numbers_and_metrics() -> None:
    found = entities("Compare Google and MSFT revenue in FY2024 vs 2023, above $5.2 billion?")

    assert found.tickers == ["GOOGL", "MSFT"]
    assert found.years == [2023, 2024]
    assert found.numbers == ["5.2"]
    assert found.metrics == ["revenue"]


def test_single_letter_tickers_and_lowercase_words_are_not_companies() -> None:
    assert entities("What is a V-shaped recovery? ge is not a ticker here").tickers == []


def test_simple_lookups_are_simple_and_analysis_is_complex() -> None:
    assert not classify("What risks does Nvidia list about export controls?").complex
    assert classify("Compare Apple and Microsoft R&D spending").reasons == [
        "multiple_companies", "comparison",
    ]  # fmt: skip
    assert "calculation" in classify("How much did Costco's revenue grow?").reasons
    assert "explanation" in classify("Why did Boeing's margins fall?").reasons
    assert "multiple_years" in classify("Pfizer revenue 2023 and 2024").reasons


def test_simple_questions_start_small_complex_ones_on_the_default_tier() -> None:
    assert select_tier(classify("Nvidia export control risks"), POLICY) == ("small", ["simple"])
    tier, reasons = select_tier(classify("Compare Apple and Microsoft revenue"), POLICY)
    assert tier == "large" and "comparison" in reasons


def test_routing_off_always_uses_the_default_tier() -> None:
    off = POLICY.model_copy(
        update={"routing": POLICY.routing.model_copy(update={"enabled": False})}
    )
    assert select_tier(classify("Nvidia export control risks"), off) == ("large", ["routing_off"])


def test_small_answers_escalate_for_each_configured_reason() -> None:
    assert should_escalate(facts(verified=False), POLICY) == "failed_verification"
    assert should_escalate(facts(declined=True, verified=None), POLICY) == "declined_with_evidence"
    assert should_escalate(facts(confidence=0.2), POLICY) == "low_confidence"
    assert should_escalate(facts(confidence=0.9), POLICY) is None


def test_no_escalation_from_large_or_for_a_decline_without_evidence() -> None:
    assert should_escalate(facts(tier="large", verified=False), POLICY) is None
    assert should_escalate(facts(declined=True, evidence_count=0, verified=None), POLICY) is None


def test_abstention_needs_a_calibrated_confidence_below_the_threshold() -> None:
    assert should_abstain(facts(confidence=None), POLICY) is None  # uncalibrated: never
    assert should_abstain(facts(confidence=0.1), POLICY) == "low_confidence"
    assert should_abstain(facts(confidence=0.8), POLICY) is None
    assert should_abstain(facts(confidence=0.1, declined=True), POLICY) is None


def test_escalation_is_skipped_when_it_would_blow_the_request_budget() -> None:
    assert escalation_fits(facts(tokens_used=10_000), POLICY)
    assert not escalation_fits(facts(tokens_used=20_000), POLICY)


def test_admission_sheds_only_when_the_queue_is_full() -> None:
    config = BackpressureConfig(max_concurrent=1, max_waiting=2, wait_timeout_s=5)
    assert admit(1, config).admitted
    shed = admit(2, config)
    assert not shed.admitted and shed.reason == "queue_full" and shed.retry_after_s == 5


def test_budget_left() -> None:
    assert check_budget(400, 1000) == 600
    assert check_budget(1200, 1000) <= 0
