from typing import Any

from eval.gate import check, make_baseline, table


def result(r1: float = 0.80, leaks: int = 0, n: int = 130) -> dict[str, Any]:
    metrics = {m: {"mean": v} for m, v in
               {"r1": r1, "r5": 0.93, "r10": 0.95, "mrr": 0.86, "ndcg": 0.88}.items()}  # fmt: skip
    return {
        "config": "c",
        "n": n,
        "metrics": metrics,
        "acl": {"cases": 10, "leaks": [None] * leaks},
    }


def failed(checks: list[Any]) -> list[str]:
    return [c.name for c in checks if not c.ok]


def test_a_run_matching_the_baseline_passes_and_small_noise_is_tolerated() -> None:
    baseline = make_baseline(result())

    assert failed(check(result(), baseline)) == []
    assert failed(check(result(r1=0.78), baseline)) == []  # within the 0.03 tolerance
    assert baseline.floors["r1"] == 0.77 and baseline.measured["r1"] == 0.8


def test_a_real_regression_fails_the_gate() -> None:
    baseline = make_baseline(result())

    assert failed(check(result(r1=0.60), baseline)) == ["r1"]


def test_any_access_control_leak_fails_even_if_quality_is_better() -> None:
    baseline = make_baseline(result())

    assert failed(check(result(r1=0.95, leaks=1), baseline)) == ["acl_leaks"]


def test_dropping_cases_cannot_buy_a_pass() -> None:
    baseline = make_baseline(result())

    assert failed(check(result(r1=0.95, n=100), baseline)) == ["cases"]
    assert failed(check(result(n=200), baseline)) == []  # more cases are fine


def test_the_report_names_each_failing_check() -> None:
    text = table(check(result(r1=0.60), make_baseline(result())))

    assert "| r1 | 0.6 | 0.77 | **FAIL** recorded 0.800 |" in text
