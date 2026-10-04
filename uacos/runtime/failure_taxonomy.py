from __future__ import annotations

from dataclasses import dataclass
from typing import Any


CATEGORY_MAP = {
    "no_patch": "CONTEXT",
    "patch_validation_failed": "PATCH",
    "stale_patch_precondition_failed": "PATCH",
    "patch_precondition_capture_failed": "ENVIRONMENT",
    "tests_failed": "TEST",
    "tests_timed_out": "TEST",
    "adapter_timeout": "PROVIDER",
    "adapter_error": "PROVIDER",
    "adapter_cancelled": "CANCELLED",
    "adapter_blocked": "POLICY",
    "test_command_blocked": "POLICY",
    "cancel_requested": "CANCELLED",
    "rollback_failed": "ROLLBACK",
    "rollback_verification_failed": "ROLLBACK",
    "no_progress_repeated_identical_outcome": "NO_PROGRESS",
    "max_iterations_exhausted": "NO_PROGRESS",
    "auth_failed": "AUTH",
    "missing_credentials": "AUTH",
    "dependency_missing": "DEPENDENCY",
    "network_unavailable": "NETWORK",
    "hardware_unavailable": "HARDWARE",
}

MUTATION_RELATED = {"PATCH", "TEST"}
AUTO_REPAIRABLE = {"CONTEXT", "PATCH", "TEST", "DEPENDENCY", "PROVIDER"}
HUMAN_REQUIRED = {"AUTH", "HARDWARE"}
HARD_STOP = {"POLICY", "CANCELLED", "ROLLBACK", "NO_PROGRESS", "UNKNOWN"}


@dataclass(frozen=True)
class FailureClassification:
    raw: str
    category: str
    repairable: bool
    mutation_related: bool
    requires_human: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw": self.raw,
            "category": self.category,
            "repairable": self.repairable,
            "mutation_related": self.mutation_related,
            "requires_human": self.requires_human,
        }


def classify_failure(failure_class: str | None) -> FailureClassification:
    raw = str(failure_class or "unknown_failure").strip() or "unknown_failure"
    category = CATEGORY_MAP.get(raw, "UNKNOWN")
    return FailureClassification(
        raw=raw,
        category=category,
        repairable=category in AUTO_REPAIRABLE,
        mutation_related=category in MUTATION_RELATED,
        requires_human=category in HUMAN_REQUIRED,
    )


def plan_recovery(
    failure_class: str | None,
    *,
    real_failure_observed: bool,
    mutation_applied: bool = False,
    rollback_verified: bool = False,
    repeated_failure: bool = False,
    repair_attempts: int = 0,
    max_repair_attempts: int = 1,
) -> dict[str, Any]:
    """Return one bounded recovery action without performing mutation.

    The planner is intentionally deterministic and fail-closed. It does not trust an
    agent's prose claim that a failure or rollback happened; callers must supply facts
    derived from host-observed evidence. Rollback is required only when a failed path
    actually mutated workspace state.
    """
    classification = classify_failure(failure_class)

    if not real_failure_observed:
        return {
            "action": "STOP",
            "reason": "repair_requires_observed_failure",
            "classification": classification.to_dict(),
        }
    if repeated_failure:
        return {
            "action": "STOP",
            "reason": "repeated_failure_signature",
            "classification": classification.to_dict(),
        }
    if repair_attempts >= max_repair_attempts:
        return {
            "action": "STOP",
            "reason": "repair_budget_exhausted",
            "classification": classification.to_dict(),
        }
    if classification.requires_human:
        return {
            "action": "HUMAN",
            "reason": f"human_required:{classification.category.lower()}",
            "classification": classification.to_dict(),
        }
    if classification.category in HARD_STOP or not classification.repairable:
        return {
            "action": "STOP",
            "reason": f"non_repairable:{classification.category.lower()}",
            "classification": classification.to_dict(),
        }
    if classification.mutation_related and mutation_applied and not rollback_verified:
        return {
            "action": "STOP",
            "reason": "verified_rollback_required_before_repair",
            "classification": classification.to_dict(),
        }

    strategy = {
        "CONTEXT": "RETRIEVE_MORE_CONTEXT",
        "PATCH": "REPLAN_PATCH",
        "TEST": "REPLAN_FROM_TEST_EVIDENCE",
        "DEPENDENCY": "DIAGNOSE_DEPENDENCY",
        "PROVIDER": "RETRY_OR_SWITCH_PROVIDER",
    }[classification.category]
    return {
        "action": "REPAIR",
        "reason": "bounded_evidence_guided_repair_allowed",
        "strategy": strategy,
        "classification": classification.to_dict(),
        "remaining_repairs": max(0, max_repair_attempts - repair_attempts - 1),
    }
