from __future__ import annotations

from pathlib import Path
from typing import Any

from uacos.execution.evidence_ledger import (
    append_evidence_event,
    hash_text,
    read_evidence_ledger,
    verify_evidence_ledger,
)

NEGATIVE_STATUSES = {"fail", "failed", "error", "blocked", "timeout", "unknown", "not_done", "unsupported", "contradicted"}
DEFAULT_ACCEPTED_STATUSES = {"pass", "passed", "recorded", "ready", "supported", "verified"}


def _clean_strings(values: Any) -> list[str]:
    if not isinstance(values, (list, tuple, set)):
        return []
    return [str(value).strip() for value in values if str(value).strip()]


def evaluate_mutation_evidence_gate(
    repo_root: Path,
    *,
    patch_text: str,
    allowed_files: list[str],
    allowed_dirs: list[str],
    contract: dict[str, Any] | None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Decide whether a Phase-3 execution may cross the source-mutation boundary.

    The gate is intentionally opt-in for backward compatibility. When enabled it is
    fail-closed: a valid canonical evidence ledger, declared mutation scope, a concrete
    patch, and every declared evidence requirement must be present before source files
    can be changed. This function does not apply a patch or mutate source files.
    """
    if not contract or contract.get("enabled") is not True:
        return {
            "status": "pass",
            "decision": "allow",
            "reason": "evidence_gate_not_enabled",
            "enabled": False,
            "decision_event_id": None,
        }

    ledger_check = verify_evidence_ledger(repo_root)
    if ledger_check.get("status") != "pass":
        return {
            "status": "blocked",
            "decision": "deny",
            "reason": "evidence_ledger_invalid",
            "enabled": True,
            "ledger": ledger_check,
            "decision_event_id": None,
        }

    required_ids = _clean_strings(contract.get("required_event_ids"))
    required_types = set(_clean_strings(contract.get("required_event_types")))
    accepted_statuses = {
        value.lower()
        for value in (_clean_strings(contract.get("accepted_statuses")) or sorted(DEFAULT_ACCEPTED_STATUSES))
    }
    require_scope = contract.get("require_declared_scope", True) is True
    require_patch = contract.get("require_patch", True) is True
    require_evidence = contract.get("require_evidence", True) is True

    findings: list[str] = []
    if require_scope and not (allowed_files or allowed_dirs):
        findings.append("mutation_scope_missing")
    if require_patch and not str(patch_text or "").strip():
        findings.append("patch_missing")
    if require_evidence and not required_ids:
        findings.append("required_evidence_ids_missing")

    rows = read_evidence_ledger(repo_root)
    by_id = {str(row.get("event_id")): row for row in rows if row.get("event_id")}
    missing_ids = [event_id for event_id in required_ids if event_id not in by_id]
    if missing_ids:
        findings.append("required_evidence_missing")

    referenced = [by_id[event_id] for event_id in required_ids if event_id in by_id]
    negative_ids = [
        str(event.get("event_id"))
        for event in referenced
        if str(event.get("status") or "").lower() in NEGATIVE_STATUSES
    ]
    if negative_ids:
        findings.append("negative_evidence_present")

    unacceptable_ids = [
        str(event.get("event_id"))
        for event in referenced
        if str(event.get("status") or "").lower() not in accepted_statuses
        and str(event.get("status") or "").lower() not in NEGATIVE_STATUSES
    ]
    if unacceptable_ids:
        findings.append("evidence_status_not_accepted")

    observed_types = {str(event.get("event_type")) for event in referenced}
    missing_types = sorted(required_types - observed_types)
    if missing_types:
        findings.append("required_evidence_types_missing")

    expected_task_id = str(contract.get("task_id") or "").strip() or None
    mismatched_task_ids: list[str] = []
    if expected_task_id:
        mismatched_task_ids = [
            str(event.get("event_id"))
            for event in referenced
            if event.get("task_id") not in {None, expected_task_id}
        ]
        if mismatched_task_ids:
            findings.append("evidence_task_mismatch")

    decision = "allow" if not findings else "deny"
    status = "pass" if decision == "allow" else "blocked"
    reason = "evidence_requirements_satisfied" if decision == "allow" else findings[0]
    result = {
        "status": status,
        "decision": decision,
        "reason": reason,
        "enabled": True,
        "required_event_ids": required_ids,
        "missing_event_ids": missing_ids,
        "negative_event_ids": negative_ids,
        "unacceptable_event_ids": unacceptable_ids,
        "required_event_types": sorted(required_types),
        "missing_event_types": missing_types,
        "mismatched_task_event_ids": mismatched_task_ids,
        "findings": findings,
        "ledger_head_hash": ledger_check.get("head_hash"),
        "decision_event_id": None,
    }

    # The canonical ledger is valid, so the allow/deny decision itself may be recorded.
    event = append_evidence_event(
        repo_root,
        event_type="mutation_gate",
        source="evidence_gate",
        status=status,
        task_id=expected_task_id,
        run_id=run_id,
        input_hash=hash_text(patch_text),
        evidence_refs=required_ids,
        parent_event_ids=required_ids,
        data={
            "decision": decision,
            "reason": reason,
            "findings": findings,
            "missing_event_ids": missing_ids,
            "missing_event_types": missing_types,
        },
    )
    result["decision_event_id"] = event["event_id"]
    return result
