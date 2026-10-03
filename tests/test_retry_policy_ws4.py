import pytest

from uacos.runtime.retry_policy import decide_retry, retry_backoff_ms


def test_retryable_failures_get_bounded_backoff():
    decision = decide_retry("adapter_error", iteration=2, max_iterations=5)
    assert decision.action == "retry"
    assert decision.retryable is True
    assert decision.delay_ms == 500
    assert decision.remaining_iterations == 3


def test_non_retryable_failure_stops_immediately():
    decision = decide_retry("stale_patch_precondition_failed", iteration=1, max_iterations=5)
    assert decision.action == "stop"
    assert decision.retryable is False
    assert decision.reason == "non_retryable:stale_patch_precondition_failed"
    assert decision.delay_ms == 0


def test_unknown_failure_fails_closed():
    decision = decide_retry("mystery_failure", iteration=1, max_iterations=5)
    assert decision.action == "stop"
    assert decision.reason == "unknown_failure_fail_closed:mystery_failure"


def test_no_progress_overrides_retryable_failure():
    decision = decide_retry(
        "adapter_error",
        iteration=2,
        max_iterations=5,
        no_progress_stalled=True,
    )
    assert decision.action == "stop"
    assert decision.reason == "no_progress_repeated_identical_outcome"


def test_iteration_budget_exhaustion_overrides_retryability():
    decision = decide_retry("no_patch", iteration=3, max_iterations=3)
    assert decision.action == "stop"
    assert decision.reason == "max_iterations_exhausted"
    assert decision.remaining_iterations == 0


def test_backoff_caps_deterministically():
    assert retry_backoff_ms(1, base_ms=250, max_ms=1000) == 250
    assert retry_backoff_ms(2, base_ms=250, max_ms=1000) == 500
    assert retry_backoff_ms(3, base_ms=250, max_ms=1000) == 1000
    assert retry_backoff_ms(8, base_ms=250, max_ms=1000) == 1000


def test_invalid_retry_policy_inputs_are_rejected():
    with pytest.raises(ValueError, match="iteration_must_be_positive"):
        decide_retry("no_patch", iteration=0, max_iterations=3)
    with pytest.raises(ValueError, match="max_iterations_must_be_positive"):
        decide_retry("no_patch", iteration=1, max_iterations=0)
    with pytest.raises(ValueError, match="base_backoff_exceeds_max"):
        retry_backoff_ms(1, base_ms=1000, max_ms=500)
