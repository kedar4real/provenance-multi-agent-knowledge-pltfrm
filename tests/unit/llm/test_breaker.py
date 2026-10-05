from provenance.llm.breaker import CircuitBreaker


class Clock:
    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t


def test_starts_closed() -> None:
    assert CircuitBreaker(now=Clock()).allow()


def test_trip_blocks_until_cooldown_passes() -> None:
    clock = Clock()
    breaker = CircuitBreaker(now=clock)

    breaker.trip(cooldown_s=30)

    clock.t = 29.9
    assert not breaker.allow()
    clock.t = 30.0
    assert breaker.allow()


def test_consecutive_failures_trip_at_threshold() -> None:
    clock = Clock()
    breaker = CircuitBreaker(now=clock, failure_threshold=3, base_cooldown_s=10)

    breaker.record_failure()
    breaker.record_failure()
    assert breaker.allow()
    breaker.record_failure()
    assert not breaker.allow()
    clock.t = 10
    assert breaker.allow()


def test_success_resets_failure_count() -> None:
    breaker = CircuitBreaker(now=Clock(), failure_threshold=2)

    breaker.record_failure()
    breaker.record_success()
    breaker.record_failure()

    assert breaker.allow()


def test_longer_trip_is_not_shortened_by_a_shorter_one() -> None:
    clock = Clock()
    breaker = CircuitBreaker(now=clock)

    breaker.trip(cooldown_s=60)
    breaker.trip(cooldown_s=5)

    clock.t = 30
    assert not breaker.allow()


def test_reports_seconds_until_available() -> None:
    clock = Clock()
    breaker = CircuitBreaker(now=clock)
    breaker.trip(cooldown_s=20)
    clock.t = 5

    assert breaker.seconds_until_available() == 15


def test_a_very_long_retry_hint_is_capped_so_the_provider_is_reprobed() -> None:
    # Gemini answered "retry after 9230s" and then served requests minutes later; trusting
    # the hint sidelined a working provider for hours in long-running eval processes.
    clock = Clock()
    breaker = CircuitBreaker(now=clock, max_cooldown_s=600)

    breaker.trip(cooldown_s=9230)

    clock.t = 599.9
    assert not breaker.allow()
    clock.t = 600.0
    assert breaker.allow()
