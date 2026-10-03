from uacos.runtime.no_progress import NoProgressTracker, attempt_fingerprint, detect_no_progress


def _attempt(*, failure="no_patch", output="nothing", patch=None, validation=None):
    return {
        "status": "failed",
        "failure_class": failure,
        "patch_present": bool(patch),
        "adapter_result": {
            "status": "completed",
            "output": output,
            "patch": patch,
            "elapsed_ms": 999,
            "tokens_in": 123,
            "tokens_out": 45,
        },
        "patch_validation": validation,
    }


def test_repeated_identical_failure_is_stalled():
    tracker = NoProgressTracker(threshold=2)
    first = tracker.observe(_attempt())
    second = tracker.observe(_attempt())

    assert first["stalled"] is False
    assert second["stalled"] is True
    assert second["reason"] == "repeated_identical_outcome"
    assert second["consecutive_same_outcome"] == 2


def test_volatile_metrics_do_not_change_fingerprint():
    a = _attempt()
    b = _attempt()
    b["adapter_result"]["elapsed_ms"] = 1
    b["adapter_result"]["tokens_in"] = 9999

    assert attempt_fingerprint(a) == attempt_fingerprint(b)


def test_different_patch_breaks_no_progress_streak():
    invalid_a = _attempt(
        failure="patch_validation_failed",
        patch="diff --git a/a.py b/a.py\n",
        validation={"status": "fail", "findings": [{"reason": "outside_allowed_scope"}]},
    )
    invalid_b = _attempt(
        failure="patch_validation_failed",
        patch="diff --git a/b.py b/b.py\n",
        validation={"status": "fail", "findings": [{"reason": "outside_allowed_scope"}]},
    )

    result = detect_no_progress([invalid_a, invalid_a, invalid_b], threshold=2)
    assert result["stalled"] is False
    assert result["consecutive_same_outcome"] == 1


def test_three_identical_outcomes_respect_threshold_three():
    result = detect_no_progress([_attempt(), _attempt(), _attempt()], threshold=3)
    assert result["stalled"] is True
    assert result["consecutive_same_outcome"] == 3


def test_threshold_below_two_is_rejected():
    try:
        NoProgressTracker(threshold=1)
    except ValueError as exc:
        assert str(exc) == "no_progress_threshold_must_be_at_least_2"
    else:
        raise AssertionError("expected ValueError")
