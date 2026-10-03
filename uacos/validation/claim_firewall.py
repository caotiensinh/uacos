from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from uacos.execution.evidence_ledger import (
    append_evidence_event,
    read_evidence_ledger,
    verify_evidence_ledger,
)

SUPPORTED = "SUPPORTED"
PARTIAL = "PARTIAL"
UNSUPPORTED = "UNSUPPORTED"
CONTRADICTED = "CONTRADICTED"

NEGATIVE_STATUSES = {"fail", "failed", "error", "blocked", "timeout", "not_done", "unknown"}

DEFAULT_CLAIM_POLICIES: dict[str, dict[str, Any]] = {
    "tests_passed": {
        "required_event_types": ["test_command"],
        "accepted_statuses": ["pass"],
        "min_events": 1,
        "all_relevant_must_be_accepted": True,
    },
    "patch_validated": {
        "required_event_types": ["agent_artifact"],
        "accepted_statuses": ["pass"],
        "min_events": 1,
        "all_relevant_must_be_accepted": True,
        "required_truthy_fields": ["diff_hash"],
    },
    "token_usage_recorded": {
        "required_event_types": ["token_usage"],
        "accepted_statuses": ["recorded"],
        "min_events": 1,
        "all_relevant_must_be_accepted": True,
    },
}


def _clean_strings(values: Any) -> list[str]:
    if not isinstance(values, (list, tuple, set)):
        return []
    return [str(value).strip() for value in values if str(value).strip()]


def _policy_for(claim: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    claim_type = str(claim.get("claim_type") or "").strip()
    explicit = claim.get("requirements")
    if explicit is not None:
        if not isinstance(explicit, dict):
            return None, "requirements_must_be_object"
        policy = deepcopy(explicit)
    else:
        policy = deepcopy(DEFAULT_CLAIM_POLICIES.get(claim_type))
    if not policy:
        return None, "unknown_claim_type"

    event_types = _clean_strings(policy.get("required_event_types"))
    statuses = _clean_strings(policy.get("accepted_statuses"))
    try:
        min_events = int(policy.get("min_events", 1))
    except (TypeError, ValueError):
        return None, "invalid_min_events"
    if not event_types or not statuses or min_events < 1:
        return None, "invalid_claim_policy"

    policy["required_event_types"] = event_types
    policy["accepted_statuses"] = statuses
    policy["min_events"] = min_events
    policy["required_truthy_fields"] = _clean_strings(policy.get("required_truthy_fields"))
    policy["expected_commands"] = _clean_strings(policy.get("expected_commands"))
    policy["all_relevant_must_be_accepted"] = bool(policy.get("all_relevant_must_be_accepted", True))
    return policy, None


def evaluate_claim(repo_root: Path, claim: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one structured claim strictly against canonical evidence events.

    Natural-language confidence is intentionally irrelevant. A claim is supportable only
    when its declared evidence IDs exist in a valid evidence ledger and satisfy a bounded
    deterministic policy. UNKNOWN/tampered/missing evidence never becomes SUPPORTED.
    """
    claim_id = str(claim.get("claim_id") or "").strip()
    claim_type = str(claim.get("claim_type") or "").strip()
    text = str(claim.get("text") or "").strip()
    evidence_ids = _clean_strings(claim.get("evidence_event_ids"))

    if not claim_id or not claim_type or not text:
        return {
            "claim_id": claim_id or None,
            "claim_type": claim_type or None,
            "status": UNSUPPORTED,
            "reason": "claim_id_type_text_required",
            "evidence_event_ids": evidence_ids,
        }

    ledger_check = verify_evidence_ledger(repo_root)
    if ledger_check.get("status") != "pass":
        return {
            "claim_id": claim_id,
            "claim_type": claim_type,
            "status": UNSUPPORTED,
            "reason": "evidence_ledger_invalid",
            "ledger": ledger_check,
            "evidence_event_ids": evidence_ids,
        }

    policy, policy_error = _policy_for(claim)
    if policy_error:
        return {
            "claim_id": claim_id,
            "claim_type": claim_type,
            "status": UNSUPPORTED,
            "reason": policy_error,
            "evidence_event_ids": evidence_ids,
        }
    assert policy is not None

    if not evidence_ids:
        return {
            "claim_id": claim_id,
            "claim_type": claim_type,
            "status": UNSUPPORTED,
            "reason": "evidence_required",
            "evidence_event_ids": [],
            "policy": policy,
        }

    rows = read_evidence_ledger(repo_root)
    by_id = {str(row.get("event_id")): row for row in rows if row.get("event_id")}
    found = [by_id[event_id] for event_id in evidence_ids if event_id in by_id]
    missing_ids = [event_id for event_id in evidence_ids if event_id not in by_id]
    required_types = set(policy["required_event_types"])
    accepted = set(policy["accepted_statuses"])
    relevant = [event for event in found if str(event.get("event_type")) in required_types]
    unrelated_ids = [str(event.get("event_id")) for event in found if str(event.get("event_type")) not in required_types]

    contradicting = [
        str(event.get("event_id"))
        for event in relevant
        if str(event.get("status") or "").lower() in NEGATIVE_STATUSES
    ]
    if contradicting:
        return {
            "claim_id": claim_id,
            "claim_type": claim_type,
            "status": CONTRADICTED,
            "reason": "referenced_evidence_contradicts_claim",
            "evidence_event_ids": evidence_ids,
            "contradicting_event_ids": contradicting,
            "missing_event_ids": missing_ids,
            "unrelated_event_ids": unrelated_ids,
            "policy": policy,
        }

    if not relevant:
        return {
            "claim_id": claim_id,
            "claim_type": claim_type,
            "status": UNSUPPORTED,
            "reason": "no_relevant_evidence",
            "evidence_event_ids": evidence_ids,
            "missing_event_ids": missing_ids,
            "unrelated_event_ids": unrelated_ids,
            "policy": policy,
        }

    accepted_events = [event for event in relevant if str(event.get("status")) in accepted]
    failed_constraints: list[str] = []
    if len(accepted_events) < policy["min_events"]:
        failed_constraints.append("minimum_evidence_not_met")
    if policy["all_relevant_must_be_accepted"] and len(accepted_events) != len(relevant):
        failed_constraints.append("not_all_relevant_evidence_accepted")

    required_fields = policy["required_truthy_fields"]
    events_missing_fields: list[str] = []
    for event in accepted_events:
        if any(not event.get(field) for field in required_fields):
            events_missing_fields.append(str(event.get("event_id")))
    if events_missing_fields:
        failed_constraints.append("required_fields_missing")

    expected_commands = set(policy["expected_commands"])
    observed_commands = {str(event.get("command")) for event in accepted_events if event.get("command")}
    missing_commands = sorted(expected_commands - observed_commands)
    if missing_commands:
        failed_constraints.append("expected_commands_missing")

    if missing_ids or failed_constraints:
        status = PARTIAL if accepted_events else UNSUPPORTED
        reason = "evidence_incomplete"
    else:
        status = SUPPORTED
        reason = "evidence_policy_satisfied"

    return {
        "claim_id": claim_id,
        "claim_type": claim_type,
        "status": status,
        "reason": reason,
        "evidence_event_ids": evidence_ids,
        "accepted_event_ids": [str(event.get("event_id")) for event in accepted_events],
        "missing_event_ids": missing_ids,
        "unrelated_event_ids": unrelated_ids,
        "events_missing_required_fields": events_missing_fields,
        "missing_commands": missing_commands,
        "failed_constraints": failed_constraints,
        "policy": policy,
    }


def evaluate_claims(repo_root: Path, claims: list[dict[str, Any]]) -> dict[str, Any]:
    results = [evaluate_claim(repo_root, claim) for claim in claims]
    counts = {status: 0 for status in (SUPPORTED, PARTIAL, UNSUPPORTED, CONTRADICTED)}
    for result in results:
        counts[result["status"]] = counts.get(result["status"], 0) + 1
    return {
        "status": "pass" if counts[PARTIAL] == 0 and counts[UNSUPPORTED] == 0 and counts[CONTRADICTED] == 0 else "blocked",
        "counts": counts,
        "results": results,
        "unsupported_claim_ids": [
            result.get("claim_id")
            for result in results
            if result["status"] != SUPPORTED
        ],
    }


def evaluate_and_record_claim(repo_root: Path, claim: dict[str, Any]) -> dict[str, Any]:
    result = evaluate_claim(repo_root, claim)
    event = append_evidence_event(
        repo_root,
        event_type="claim_decision",
        source="claim_firewall",
        status=result["status"].lower(),
        task_id=str(claim.get("task_id") or "").strip() or None,
        evidence_refs=_clean_strings(claim.get("evidence_event_ids")),
        data={
            "claim_id": result.get("claim_id"),
            "claim_type": result.get("claim_type"),
            "decision": result.get("status"),
            "reason": result.get("reason"),
        },
    )
    result = dict(result)
    result["decision_event_id"] = event["event_id"]
    return result


def factual_claims_only(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Return only claims that the firewall can render as factual statements."""
    return [result for result in report.get("results", []) if result.get("status") == SUPPORTED]
