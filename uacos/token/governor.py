from __future__ import annotations

from pathlib import Path
from typing import Any

from uacos.execution.evidence_ledger import (
    append_evidence_event,
    read_evidence_ledger,
    verify_evidence_ledger,
)

TOKEN_USAGE_EVENT = "token_usage_settled"
TOKEN_DECISION_EVENT = "token_budget_decision"
DEFAULT_COMPACT_THRESHOLD = 0.80


def _contract_budget(contract: dict[str, Any]) -> int | None:
    if contract.get("status") != "ok" or contract.get("version") != 2:
        raise ValueError("task_contract_v2_required")
    raw = (contract.get("budgets") or {}).get("max_tokens")
    if raw is None:
        return None
    value = int(raw)
    if value < 0:
        raise ValueError("max_tokens_must_be_nonnegative")
    return value


def _nonnegative_tokens(value: Any, name: str) -> int:
    try:
        tokens = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name}_must_be_integer") from exc
    if tokens < 0:
        raise ValueError(f"{name}_must_be_nonnegative")
    return tokens


def _task_run_rows(
    repo_root: Path,
    *,
    task_id: str,
    run_id: str | None,
) -> list[dict[str, Any]]:
    rows = read_evidence_ledger(repo_root)
    return [
        row
        for row in rows
        if row.get("task_id") == task_id
        and (run_id is None or row.get("run_id") == run_id)
    ]


def _settled_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("event_type") == TOKEN_USAGE_EVENT]


def _row_tokens(row: dict[str, Any]) -> int:
    usage = row.get("token_usage") if isinstance(row.get("token_usage"), dict) else {}
    raw = usage.get("total_tokens", 0)
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return 0
    return max(0, value)


def token_usage_summary(
    repo_root: Path,
    *,
    task_id: str,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Summarize canonical settled usage for exactly one task/run scope."""
    task_id = str(task_id or "").strip()
    if not task_id:
        raise ValueError("task_id_required")
    integrity = verify_evidence_ledger(repo_root)
    if integrity.get("status") != "pass":
        return {
            "status": "fail",
            "reason": "evidence_ledger_invalid",
            "ledger_integrity": integrity,
            "total_tokens": None,
        }

    rows = _settled_rows(_task_run_rows(repo_root, task_id=task_id, run_id=run_id))
    seen_actions: set[str] = set()
    total = 0
    event_ids: list[str] = []
    duplicate_action_ids: list[str] = []
    for row in rows:
        action_id = str(row.get("action_id") or "").strip()
        if action_id and action_id in seen_actions:
            duplicate_action_ids.append(action_id)
            continue
        if action_id:
            seen_actions.add(action_id)
        total += _row_tokens(row)
        if row.get("event_id"):
            event_ids.append(str(row["event_id"]))

    return {
        "status": "ok",
        "reason": "canonical_usage_summed",
        "task_id": task_id,
        "run_id": run_id,
        "total_tokens": total,
        "settled_actions": len(seen_actions),
        "evidence_refs": event_ids,
        "duplicate_action_ids": sorted(set(duplicate_action_ids)),
        "ledger_integrity": integrity,
    }


def evaluate_token_budget(
    repo_root: Path,
    contract: dict[str, Any],
    *,
    task_id: str,
    run_id: str | None = None,
    requested_tokens: int,
    action_id: str | None = None,
    compact_threshold: float = DEFAULT_COMPACT_THRESHOLD,
    record_decision: bool = True,
) -> dict[str, Any]:
    """Reserve/check a planned token spend without consuming it.

    Returns ALLOW, COMPACT, or STOP. The decision is derived from Task Contract V2
    and canonical settled usage. It never trusts provider/agent prose.
    """
    try:
        max_tokens = _contract_budget(contract)
        requested = _nonnegative_tokens(requested_tokens, "requested_tokens")
    except ValueError as exc:
        return {"status": "error", "decision": "STOP", "reason": str(exc)}

    task_id = str(task_id or "").strip()
    if not task_id:
        return {"status": "error", "decision": "STOP", "reason": "task_id_required"}
    if not 0 < float(compact_threshold) <= 1:
        return {"status": "error", "decision": "STOP", "reason": "invalid_compact_threshold"}

    usage = token_usage_summary(repo_root, task_id=task_id, run_id=run_id)
    if usage.get("status") != "ok":
        return {
            "status": "fail",
            "decision": "STOP",
            "reason": "evidence_ledger_invalid",
            "usage": usage,
        }

    rows = _settled_rows(_task_run_rows(repo_root, task_id=task_id, run_id=run_id))
    if action_id and any(row.get("action_id") == action_id for row in rows):
        result = {
            "status": "ok",
            "decision": "ALLOW",
            "reason": "action_already_settled_no_new_reservation",
            "task_id": task_id,
            "run_id": run_id,
            "action_id": action_id,
            "max_tokens": max_tokens,
            "consumed_tokens": usage["total_tokens"],
            "requested_tokens": 0,
            "projected_tokens": usage["total_tokens"],
            "remaining_tokens": None if max_tokens is None else max(0, max_tokens - usage["total_tokens"]),
        }
        return result

    consumed = int(usage["total_tokens"])
    projected = consumed + requested
    if max_tokens is None:
        decision = "ALLOW"
        reason = "contract_token_budget_unbounded"
        remaining = None
    elif projected > max_tokens:
        decision = "STOP"
        reason = "contract_max_tokens_exceeded"
        remaining = max(0, max_tokens - consumed)
    elif max_tokens == 0:
        decision = "ALLOW" if requested == 0 else "STOP"
        reason = "zero_budget_no_spend" if requested == 0 else "contract_max_tokens_exceeded"
        remaining = 0
    elif projected >= int(max_tokens * float(compact_threshold)):
        decision = "COMPACT"
        reason = "token_budget_near_limit"
        remaining = max(0, max_tokens - projected)
    else:
        decision = "ALLOW"
        reason = "within_token_budget"
        remaining = max_tokens - projected

    result = {
        "status": "ok" if decision != "STOP" else "blocked",
        "decision": decision,
        "reason": reason,
        "task_id": task_id,
        "run_id": run_id,
        "action_id": action_id,
        "contract_id": contract.get("contract_id"),
        "max_tokens": max_tokens,
        "consumed_tokens": consumed,
        "requested_tokens": requested,
        "projected_tokens": projected,
        "remaining_tokens": remaining,
        "compact_threshold": float(compact_threshold),
        "usage_evidence_refs": usage.get("evidence_refs", []),
    }
    if record_decision:
        event = append_evidence_event(
            repo_root,
            event_type=TOKEN_DECISION_EVENT,
            source="uacos.token.governor",
            status=decision.lower(),
            task_id=task_id,
            run_id=run_id,
            action_id=action_id,
            token_usage={
                "requested_tokens": requested,
                "consumed_tokens": consumed,
                "projected_tokens": projected,
                "max_tokens": max_tokens,
            },
            evidence_refs=usage.get("evidence_refs", []),
            data={
                "contract_id": contract.get("contract_id"),
                "decision": decision,
                "reason": reason,
                "remaining_tokens": remaining,
            },
        )
        result["decision_event_id"] = event["event_id"]
    return result


def settle_token_usage(
    repo_root: Path,
    contract: dict[str, Any],
    *,
    task_id: str,
    run_id: str | None,
    action_id: str,
    actual_tokens: int,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Record actual spend exactly once and report post-call budget state.

    Actual usage is truth: if it exceeds a prior estimate or the remaining budget, it is
    still recorded and the returned decision is STOP so another model call cannot proceed.
    """
    try:
        max_tokens = _contract_budget(contract)
        actual = _nonnegative_tokens(actual_tokens, "actual_tokens")
        inp = None if input_tokens is None else _nonnegative_tokens(input_tokens, "input_tokens")
        out = None if output_tokens is None else _nonnegative_tokens(output_tokens, "output_tokens")
    except ValueError as exc:
        return {"status": "error", "decision": "STOP", "reason": str(exc)}

    task_id = str(task_id or "").strip()
    action_id = str(action_id or "").strip()
    if not task_id:
        return {"status": "error", "decision": "STOP", "reason": "task_id_required"}
    if not action_id:
        return {"status": "error", "decision": "STOP", "reason": "action_id_required"}

    integrity = verify_evidence_ledger(repo_root)
    if integrity.get("status") != "pass":
        return {
            "status": "fail",
            "decision": "STOP",
            "reason": "evidence_ledger_invalid",
            "ledger_integrity": integrity,
        }

    scoped = _settled_rows(_task_run_rows(repo_root, task_id=task_id, run_id=run_id))
    existing = next((row for row in scoped if row.get("action_id") == action_id), None)
    if existing is not None:
        return {
            "status": "ok",
            "decision": "ALLOW" if max_tokens is None or token_usage_summary(repo_root, task_id=task_id, run_id=run_id)["total_tokens"] <= max_tokens else "STOP",
            "reason": "usage_already_settled",
            "idempotent": True,
            "event_id": existing.get("event_id"),
            "actual_tokens": _row_tokens(existing),
        }

    before = token_usage_summary(repo_root, task_id=task_id, run_id=run_id)
    if before.get("status") != "ok":
        return {"status": "fail", "decision": "STOP", "reason": "evidence_ledger_invalid", "usage": before}

    usage_payload: dict[str, Any] = {"total_tokens": actual}
    if inp is not None:
        usage_payload["input_tokens"] = inp
    if out is not None:
        usage_payload["output_tokens"] = out

    event = append_evidence_event(
        repo_root,
        event_type=TOKEN_USAGE_EVENT,
        source="uacos.token.governor",
        status="recorded",
        task_id=task_id,
        run_id=run_id,
        action_id=action_id,
        token_usage=usage_payload,
        data={
            "contract_id": contract.get("contract_id"),
            "provider": provider,
            "model": model,
            "usage_kind": "actual",
        },
    )
    total = int(before["total_tokens"]) + actual
    exhausted = max_tokens is not None and total > max_tokens
    decision = "STOP" if exhausted else "ALLOW"
    reason = "actual_usage_exceeded_contract_budget" if exhausted else "actual_usage_recorded"
    return {
        "status": "blocked" if exhausted else "ok",
        "decision": decision,
        "reason": reason,
        "idempotent": False,
        "event_id": event["event_id"],
        "task_id": task_id,
        "run_id": run_id,
        "action_id": action_id,
        "actual_tokens": actual,
        "consumed_tokens": total,
        "max_tokens": max_tokens,
        "remaining_tokens": None if max_tokens is None else max(0, max_tokens - total),
    }
