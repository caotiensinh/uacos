from __future__ import annotations

from pathlib import Path
from typing import Any

from uacos.agent.safe_execution import run_safe_agent_execution
from uacos.execution.evidence_ledger import (
    append_evidence_event,
    read_evidence_ledger,
    verify_evidence_ledger,
)
from uacos.runtime.failure_taxonomy import plan_recovery


def _observed_failure(result: dict[str, Any]) -> bool:
    return str(result.get("status") or "") not in {"", "passed"}


def _mutation_applied(result: dict[str, Any]) -> bool:
    return str((result.get("patch_apply") or {}).get("status") or "") == "applied"


def _rollback_verified(result: dict[str, Any]) -> bool:
    return str((result.get("rollback") or {}).get("status") or "") == "rolled_back"


def record_recovery_decision(
    repo_root: Path,
    result: dict[str, Any],
    *,
    task_id: str | None = None,
    repair_attempts: int = 0,
    max_repair_attempts: int = 1,
    repeated_failure: bool = False,
) -> dict[str, Any]:
    """Plan and persist one recovery decision from host-observed execution evidence.

    This function never executes a repair. It is the evidence-bound DECIDE stage in
    OBSERVE -> DECIDE -> EXECUTE. A caller above this layer may act on REPAIR/HUMAN/STOP.
    """
    integrity = verify_evidence_ledger(repo_root)
    if integrity.get("status") != "pass":
        return {
            "action": "STOP",
            "reason": "evidence_ledger_invalid",
            "persisted": False,
            "ledger": integrity,
        }

    failure_reason = str(result.get("reason") or "unknown_failure")
    mutation_applied = _mutation_applied(result)
    rollback_verified = _rollback_verified(result)
    run_id = str(result.get("run_id") or "") or None
    action_id = f"recovery:{run_id or 'unbound'}:{repair_attempts}"

    existing = next(
        (
            row
            for row in read_evidence_ledger(repo_root)
            if row.get("event_type") == "recovery_decision" and row.get("action_id") == action_id
        ),
        None,
    )
    if existing is not None:
        data = existing.get("data") or {}
        if (
            existing.get("run_id") != run_id
            or existing.get("task_id") != task_id
            or str(data.get("failure_reason") or "") != failure_reason
        ):
            return {
                "action": "STOP",
                "reason": "recovery_action_id_conflict",
                "persisted": False,
                "evidence_event_id": existing.get("event_id"),
            }
        decision = dict(data.get("decision") or {})
        return decision | {
            "persisted": True,
            "idempotent_replay": True,
            "evidence_event_id": existing.get("event_id"),
        }

    decision = plan_recovery(
        failure_reason,
        real_failure_observed=_observed_failure(result),
        mutation_applied=mutation_applied,
        rollback_verified=rollback_verified,
        repeated_failure=repeated_failure,
        repair_attempts=repair_attempts,
        max_repair_attempts=max_repair_attempts,
    )

    event = append_evidence_event(
        repo_root,
        event_type="recovery_decision",
        source="uacos.runtime.evidence_guided_recovery",
        status=str(decision.get("action") or "STOP").lower(),
        task_id=task_id,
        run_id=run_id,
        action_id=action_id,
        data={
            "failure_reason": failure_reason,
            "mutation_applied": mutation_applied,
            "rollback_verified": rollback_verified,
            "repair_attempts": repair_attempts,
            "max_repair_attempts": max_repair_attempts,
            "repeated_failure": repeated_failure,
            "decision": decision,
        },
    )
    return decision | {
        "persisted": True,
        "idempotent_replay": False,
        "evidence_event_id": event["event_id"],
    }


def run_safe_execution_with_recovery(
    repo_root: Path,
    task: str,
    adapter: Any,
    *,
    task_id: str | None = None,
    repair_attempts: int = 0,
    max_repair_attempts: int = 1,
    repeated_failure: bool = False,
    **safe_execution_kwargs: Any,
) -> dict[str, Any]:
    """Run the existing safe execution path, then attach an evidence-bound decision.

    Successful execution is returned unchanged except for recovery_decision=None.
    Failure never triggers an implicit agent retry or mutation here.
    """
    result = run_safe_agent_execution(repo_root, task, adapter, **safe_execution_kwargs)
    result["recovery_decision"] = None
    if str(result.get("status") or "") == "passed":
        return result

    result["recovery_decision"] = record_recovery_decision(
        repo_root,
        result,
        task_id=task_id,
        repair_attempts=repair_attempts,
        max_repair_attempts=max_repair_attempts,
        repeated_failure=repeated_failure,
    )
    return result
