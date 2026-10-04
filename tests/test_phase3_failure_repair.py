from __future__ import annotations

from uacos.runtime.failure_taxonomy import classify_failure, plan_recovery


def test_failure_taxonomy_maps_existing_runtime_classes():
    assert classify_failure("no_patch").category == "CONTEXT"
    assert classify_failure("patch_validation_failed").category == "PATCH"
    assert classify_failure("tests_failed").category == "TEST"
    assert classify_failure("adapter_timeout").category == "PROVIDER"
    assert classify_failure("test_command_blocked").category == "POLICY"
    assert classify_failure("rollback_failed").category == "ROLLBACK"
    assert classify_failure("something_new").category == "UNKNOWN"


def test_repair_requires_real_observed_failure():
    result = plan_recovery(
        "tests_failed",
        real_failure_observed=False,
        rollback_verified=True,
    )
    assert result["action"] == "STOP"
    assert result["reason"] == "repair_requires_observed_failure"


def test_mutation_related_failure_requires_verified_rollback():
    result = plan_recovery(
        "patch_validation_failed",
        real_failure_observed=True,
        rollback_verified=False,
    )
    assert result["action"] == "STOP"
    assert result["reason"] == "verified_rollback_required_before_repair"


def test_verified_patch_failure_gets_one_bounded_repair():
    result = plan_recovery(
        "patch_validation_failed",
        real_failure_observed=True,
        rollback_verified=True,
        repair_attempts=0,
        max_repair_attempts=1,
    )
    assert result["action"] == "REPAIR"
    assert result["strategy"] == "REPLAN_PATCH"
    assert result["remaining_repairs"] == 0


def test_same_failure_signature_stops_instead_of_looping():
    result = plan_recovery(
        "adapter_timeout",
        real_failure_observed=True,
        repeated_failure=True,
    )
    assert result["action"] == "STOP"
    assert result["reason"] == "repeated_failure_signature"


def test_repair_budget_is_hard_bounded():
    result = plan_recovery(
        "dependency_missing",
        real_failure_observed=True,
        repair_attempts=1,
        max_repair_attempts=1,
    )
    assert result["action"] == "STOP"
    assert result["reason"] == "repair_budget_exhausted"


def test_auth_and_hardware_require_human_not_retry_loop():
    auth = plan_recovery("missing_credentials", real_failure_observed=True)
    hardware = plan_recovery("hardware_unavailable", real_failure_observed=True)
    assert auth["action"] == "HUMAN"
    assert auth["reason"] == "human_required:auth"
    assert hardware["action"] == "HUMAN"
    assert hardware["reason"] == "human_required:hardware"


def test_policy_rollback_and_unknown_fail_closed():
    for failure in ("adapter_blocked", "rollback_failed", "unmapped_failure"):
        result = plan_recovery(failure, real_failure_observed=True)
        assert result["action"] == "STOP"
        assert result["reason"].startswith("non_repairable:")


def test_context_and_provider_can_recover_without_rollback_requirement():
    context = plan_recovery("no_patch", real_failure_observed=True)
    provider = plan_recovery("adapter_timeout", real_failure_observed=True)
    assert context["action"] == "REPAIR"
    assert context["strategy"] == "RETRIEVE_MORE_CONTEXT"
    assert provider["action"] == "REPAIR"
    assert provider["strategy"] == "RETRY_OR_SWITCH_PROVIDER"
