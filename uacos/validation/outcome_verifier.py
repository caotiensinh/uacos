from __future__ import annotations

from pathlib import Path
from typing import Any

from uacos.execution.evidence_ledger import (
    append_evidence_event,
    read_evidence_ledger,
    verify_evidence_ledger,
)
from uacos.orchestrator.contract import evaluate_done_predicate

PASS_STATUSES = {"pass", "passed", "success", "ok", "verified", "supported", "allow", "applied"}
FAIL_STATUSES = {"fail", "failed", "error", "blocked", "denied", "contradicted", "unsupported"}


def _status_pass(row: dict[str, Any]) -> bool:
    return str(row.get("status") or "").strip().lower() in PASS_STATUSES


def _status_fail(row: dict[str, Any]) -> bool:
    return str(row.get("status") or "").strip().lower() in FAIL_STATUSES


def _check_id(row: dict[str, Any]) -> str | None:
    data = row.get("data") if isinstance(row.get("data"), dict) else {}
    for value in (
        data.get("check_id"),
        data.get("evidence_id"),
        data.get("name"),
        row.get("command"),
    ):
        text = str(value or "").strip()
        if text:
            return text
    return None


def _evidence_names(row: dict[str, Any]) -> set[str]:
    names = {str(row.get("event_id") or "").strip(), str(row.get("event_type") or "").strip()}
    cid = _check_id(row)
    if cid:
        names.add(cid)
    data = row.get("data") if isinstance(row.get("data"), dict) else {}
    for value in data.get("evidence_names") or []:
        text = str(value or "").strip()
        if text:
            names.add(text)
    return {name for name in names if name}


def _rows_for_task(rows: list[dict[str, Any]], task_id: str | None) -> list[dict[str, Any]]:
    if not task_id:
        return rows
    return [row for row in rows if row.get("task_id") in {None, task_id}]


def _matching_checks(rows: list[dict[str, Any]], event_types: set[str], required: list[str]) -> tuple[set[str], set[str], list[str]]:
    required_set = set(required)
    passed: set[str] = set()
    contradicted: set[str] = set()
    refs: list[str] = []
    for row in rows:
        if str(row.get("event_type") or "") not in event_types:
            continue
        cid = _check_id(row)
        if not cid or cid not in required_set:
            continue
        event_id = str(row.get("event_id") or "")
        if _status_pass(row):
            passed.add(cid)
            if event_id:
                refs.append(event_id)
        elif _status_fail(row):
            contradicted.add(cid)
            if event_id:
                refs.append(event_id)
    return passed, contradicted, refs


def _layer(required: list[str], passed: set[str], contradicted: set[str]) -> dict[str, Any]:
    required_set = set(required)
    missing = sorted(required_set - passed)
    contradictions = sorted(required_set & contradicted)
    if contradictions:
        state = "FAIL"
        reason = "contradictory_evidence"
    elif missing:
        state = "FAIL"
        reason = "required_evidence_missing"
    else:
        state = "PASS"
        reason = "all_required_checks_verified" if required else "not_required"
    return {
        "state": state,
        "reason": reason,
        "required": list(required),
        "passed": sorted(passed),
        "missing": missing,
        "contradictions": contradictions,
    }


def verify_task_outcome(
    repo_root: Path,
    contract: dict[str, Any],
    *,
    task_id: str | None = None,
    record_verdict: bool = True,
) -> dict[str, Any]:
    """Derive task outcome from host-recorded canonical evidence, never agent prose.

    Verification layers are intentionally separate so test success cannot masquerade as
    a working system or a satisfied user outcome. Runtime/outcome checks are matched by
    exact check IDs declared in Task Contract V2.
    """
    repo_root = repo_root.resolve()
    if contract.get("status") != "ok" or contract.get("version") != 2:
        return {"status": "error", "reason": "task_contract_v2_required"}

    ledger_integrity = verify_evidence_ledger(repo_root)
    if ledger_integrity.get("status") != "pass":
        return {
            "status": "fail",
            "reason": "evidence_ledger_invalid",
            "overall": "FAIL",
            "ledger_integrity": ledger_integrity,
            "layers": {},
        }

    rows = _rows_for_task(read_evidence_ledger(repo_root), task_id)
    success = contract.get("success_conditions") or {}
    required_tests = list(success.get("tests") or [])
    required_runtime = list(success.get("runtime") or [])
    required_outcome = list(success.get("outcome") or [])

    passed_tests, failed_tests, test_refs = _matching_checks(
        rows, {"test_result", "test", "verification_test"}, required_tests
    )
    passed_runtime, failed_runtime, runtime_refs = _matching_checks(
        rows, {"runtime_check", "runtime_verification", "system_verification"}, required_runtime
    )
    passed_outcome, failed_outcome, outcome_refs = _matching_checks(
        rows, {"outcome_check", "outcome_verification", "user_outcome"}, required_outcome
    )

    mutation_required = bool((contract.get("scope") or {}).get("allowed_files") or (contract.get("scope") or {}).get("allowed_dirs"))
    code_diff_rows = [
        row
        for row in rows
        if str(row.get("event_type") or "") in {"patch_apply", "mutation"}
        and _status_pass(row)
        and bool(row.get("diff_hash"))
    ]
    code_valid = (not mutation_required) or bool(code_diff_rows)

    layers = {
        "CODE_VALID": {
            "state": "PASS" if code_valid else "FAIL",
            "reason": "verified_mutation_evidence" if mutation_required and code_valid else ("not_required" if not mutation_required else "applied_diff_evidence_missing"),
        },
        "TEST_VALID": _layer(required_tests, passed_tests, failed_tests),
        "SYSTEM_VALID": _layer(required_runtime, passed_runtime, failed_runtime),
        "USER_OUTCOME_VALID": _layer(required_outcome, passed_outcome, failed_outcome),
    }

    observed_evidence: set[str] = set()
    for row in rows:
        if _status_pass(row):
            observed_evidence.update(_evidence_names(row))
    unsupported_claims = [
        str(row.get("event_id") or "")
        for row in rows
        if str(row.get("event_type") or "") == "claim_decision"
        and str(row.get("status") or "").strip().upper() in {"UNSUPPORTED", "CONTRADICTED", "PARTIAL"}
    ]
    forbidden_side_effects = [
        _check_id(row) or str(row.get("event_id") or "")
        for row in rows
        if str(row.get("event_type") or "") in {"forbidden_side_effect", "scope_violation"} and _status_fail(row)
    ]
    result_recorded = any(
        str(row.get("event_type") or "") in {"result_recorded", "result", "final_result"} and _status_pass(row)
        for row in rows
    )

    done = evaluate_done_predicate(
        contract,
        {
            "passed_tests": sorted(passed_tests),
            "runtime_checks": sorted(passed_runtime),
            "outcome_checks": sorted(passed_outcome),
            "evidence": sorted(observed_evidence),
            "forbidden_side_effects": forbidden_side_effects,
            "result_recorded": result_recorded,
            "unsupported_claims": unsupported_claims,
        },
    )
    layers_pass = all(layer.get("state") == "PASS" for layer in layers.values())
    overall = "PASS" if layers_pass and done.get("state") == "done" else "FAIL"
    reason = "user_outcome_verified" if overall == "PASS" else "verification_incomplete_or_failed"

    refs = list(dict.fromkeys(test_refs + runtime_refs + outcome_refs + [str(row.get("event_id")) for row in code_diff_rows if row.get("event_id")]))
    verdict = {
        "status": "pass" if overall == "PASS" else "fail",
        "reason": reason,
        "overall": overall,
        "contract_id": contract.get("contract_id"),
        "task_id": task_id,
        "ledger_integrity": ledger_integrity,
        "layers": layers,
        "done_predicate": done,
        "evidence_refs": refs,
    }

    if record_verdict:
        event = append_evidence_event(
            repo_root,
            event_type="outcome_verdict",
            source="uacos.validation.outcome_verifier",
            status="pass" if overall == "PASS" else "fail",
            task_id=task_id,
            evidence_refs=refs,
            parent_event_ids=refs,
            data={
                "contract_id": contract.get("contract_id"),
                "overall": overall,
                "layers": {name: value["state"] for name, value in layers.items()},
                "done_state": done.get("state"),
            },
        )
        verdict["verdict_event_id"] = event["event_id"]

    return verdict
