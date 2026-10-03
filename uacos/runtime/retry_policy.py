from __future__ import annotations

from dataclasses import dataclass


RETRYABLE_FAILURES = {
    "no_patch",
    "patch_validation_failed",
    "adapter_timeout",
    "adapter_error",
    "tests_failed",
    "tests_timed_out",
}

NON_RETRYABLE_FAILURES = {
    "cancel_requested",
    "adapter_cancelled",
    "adapter_blocked",
    "test_command_blocked",
    "stale_patch_precondition_failed",
    "patch_precondition_capture_failed",
    "rollback_failed",
    "rollback_verification_failed",
}


@dataclass(frozen=True)
class RetryDecision:
    action: str
    reason: str
    retryable: bool
    delay_ms: int
    remaining_iterations: int

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "reason": self.reason,
            "retryable": self.retryable,
            "delay_ms": self.delay_ms,
            "remaining_iterations": self.remaining_iterations,
        }


def retry_backoff_ms(iteration: int, *, base_ms: int = 250, max_ms: int = 5000) -> int:
    if iteration < 1:
        raise ValueError("iteration_must_be_positive")
    if base_ms < 0 or max_ms < 0:
        raise ValueError("backoff_must_be_non_negative")
    if base_ms > max_ms:
        raise ValueError("base_backoff_exceeds_max")
    return min(max_ms, base_ms * (2 ** max(0, iteration - 1)))


def decide_retry(
    failure_class: str | None,
    *,
    iteration: int,
    max_iterations: int,
    no_progress_stalled: bool = False,
    base_backoff_ms: int = 250,
    max_backoff_ms: int = 5000,
) -> RetryDecision:
    if iteration < 1:
        raise ValueError("iteration_must_be_positive")
    if max_iterations < 1:
        raise ValueError("max_iterations_must_be_positive")

    remaining = max(0, max_iterations - iteration)
    failure = str(failure_class or "unknown_failure")

    if no_progress_stalled:
        return RetryDecision(
            action="stop",
            reason="no_progress_repeated_identical_outcome",
            retryable=False,
            delay_ms=0,
            remaining_iterations=remaining,
        )

    if remaining == 0:
        return RetryDecision(
            action="stop",
            reason="max_iterations_exhausted",
            retryable=False,
            delay_ms=0,
            remaining_iterations=0,
        )

    if failure in NON_RETRYABLE_FAILURES:
        return RetryDecision(
            action="stop",
            reason=f"non_retryable:{failure}",
            retryable=False,
            delay_ms=0,
            remaining_iterations=remaining,
        )

    if failure not in RETRYABLE_FAILURES:
        return RetryDecision(
            action="stop",
            reason=f"unknown_failure_fail_closed:{failure}",
            retryable=False,
            delay_ms=0,
            remaining_iterations=remaining,
        )

    return RetryDecision(
        action="retry",
        reason=f"retryable:{failure}",
        retryable=True,
        delay_ms=retry_backoff_ms(iteration, base_ms=base_backoff_ms, max_ms=max_backoff_ms),
        remaining_iterations=remaining,
    )
