from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any
import os
import time

from uacos.execution.evidence_ledger import (
    append_evidence_event,
    evidence_ledger_path,
    read_evidence_ledger,
    verify_evidence_ledger,
)

TOKEN_USAGE_EVENT = "token_usage_settled"
TOKEN_DECISION_EVENT = "token_budget_decision"
TOKEN_CANCEL_EVENT = "token_reservation_cancelled"
DEFAULT_COMPACT_THRESHOLD = 0.80
_LOCK_TIMEOUT_SEC = 5.0
_LOCK_STALE_SEC = 30.0


@contextmanager
def _governor_lock(repo_root: Path):
    """Cross-process lock for read-decide-append token budget transactions."""
    lock_path = evidence_ledger_path(repo_root).parent / ".token_governor.lock"
    deadline = time.monotonic() + _LOCK_TIMEOUT_SEC
    fd: int | None = None
    while fd is None:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode("ascii", errors="ignore"))
            os.fsync(fd)
        except FileExistsError:
            try:
                age = time.time() - lock_path.stat().st_mtime
                if age > _LOCK_STALE_SEC:
                    lock_path.unlink(missing_ok=True)
                    continue
            except FileNotFoundError:
                continue
            if time.monotonic() >= deadline:
                raise TimeoutError("token_governor_lock_timeout")
            time.sleep(0.01)
    try:
        yield
    finally:
        if fd is not None:
            os.close(fd)
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def _contract_budget(contract: dict[str, Any]) -> int | None:
    if contract.get("status") != "ok" or contract.get("version") != 2:
        raise ValueError("task_contract_v2_required")
    raw = (contract.get("budgets") or {}).get("max_tokens")
    if raw is None:
        return None
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError("max_tokens_must_be_integer") from exc
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


def _scope_rows(repo_root: Path, *, task_id: str, run_id: str | None) -> list[dict[str, Any]]:
    return [
        row
        for row in read_evidence_ledger(repo_root)
        if row.get("task_id") == task_id
        and (run_id is None or row.get("run_id") == run_id)
    ]


def _row_tokens(row: dict[str, Any], key: str = "total_tokens") -> int:
    usage = row.get("token_usage") if isinstance(row.get("token_usage"), dict) else {}
    try:
        return max(0, int(usage.get(key, 0) or 0))
    except (TypeError, ValueError):
        return 0


def _active_reservations(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    settled = {
        str(row.get("action_id"))
        for row in rows
        if row.get("event_type") == TOKEN_USAGE_EVENT and row.get("action_id")
    }
    cancelled = {
        str(row.get("action_id"))
        for row in rows
        if row.get("event_type") == TOKEN_CANCEL_EVENT and row.get("action_id")
    }
    reservations: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row.get("event_type") != TOKEN_DECISION_EVENT:
            continue
        action_id = str(row.get("action_id") or "").strip()
        data = row.get("data") if isinstance(row.get("data"), dict) else {}
        if not action_id or action_id in settled or action_id in cancelled:
            continue
        if data.get("decision") not in {"ALLOW", "COMPACT"}:
            continue
        reservations.setdefault(action_id, row)
    return reservations


def token_usage_summary(
    repo_root: Path,
    *,
    task_id: str,
    run_id: str | None = None,
) -> dict[str, Any]:
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
            "reserved_tokens": None,
        }
    rows = _scope_rows(repo_root, task_id=task_id, run_id=run_id)
    settled_rows = [row for row in rows if row.get("event_type") == TOKEN_USAGE_EVENT]
    seen_actions: set[str] = set()
    total = 0
    event_ids: list[str] = []
    duplicate_action_ids: list[str] = []
    for row in settled_rows:
        action_id = str(row.get("action_id") or "").strip()
        if action_id and action_id in seen_actions:
            duplicate_action_ids.append(action_id)
            continue
        if action_id:
            seen_actions.add(action_id)
        total += _row_tokens(row)
        if row.get("event_id"):
            event_ids.append(str(row["event_id"]))
    reservations = _active_reservations(rows)
    reserved = sum(_row_tokens(row, "requested_tokens") for row in reservations.values())
    return {
        "status": "ok",
        "reason": "canonical_usage_summed",
        "task_id": task_id,
        "run_id": run_id,
        "total_tokens": total,
        "reserved_tokens": reserved,
        "effective_tokens": total + reserved,
        "settled_actions": len(seen_actions),
        "active_reservations": sorted(reservations),
        "evidence_refs": event_ids,
        "duplicate_action_ids": sorted(set(duplicate_action_ids)),
        "ledger_integrity": integrity,
    }


def _evaluate_locked(
    repo_root: Path,
    contract: dict[str, Any],
    *,
    task_id: str,
    run_id: str | None,
    requested: int,
    action_id: str | None,
    threshold: float,
    record_decision: bool,
    max_tokens: int | None,
) -> dict[str, Any]:
    usage = token_usage_summary(repo_root, task_id=task_id, run_id=run_id)
    if usage.get("status") != "ok":
        return {"status": "fail", "decision": "STOP", "reason": "evidence_ledger_invalid", "usage": usage}
    rows = _scope_rows(repo_root, task_id=task_id, run_id=run_id)
    settled = {
        str(row.get("action_id")): row
        for row in rows
        if row.get("event_type") == TOKEN_USAGE_EVENT and row.get("action_id")
    }
    if action_id and action_id in settled:
        consumed = int(usage["total_tokens"])
        over = max_tokens is not None and consumed > max_tokens
        return {
            "status": "blocked" if over else "ok",
            "decision": "STOP" if over else "ALLOW",
            "reason": "budget_already_exhausted" if over else "action_already_settled_no_new_reservation",
            "task_id": task_id,
            "run_id": run_id,
            "action_id": action_id,
            "max_tokens": max_tokens,
            "consumed_tokens": consumed,
            "reserved_tokens": int(usage["reserved_tokens"]),
            "requested_tokens": 0,
            "projected_tokens": int(usage["effective_tokens"]),
            "remaining_tokens": None if max_tokens is None else max(0, max_tokens - int(usage["effective_tokens"])),
        }
    reservations = _active_reservations(rows)
    if action_id and action_id in reservations:
        row = reservations[action_id]
        data = row.get("data") if isinstance(row.get("data"), dict) else {}
        return {
            "status": "ok",
            "decision": data.get("decision", "ALLOW"),
            "reason": "action_already_reserved",
            "task_id": task_id,
            "run_id": run_id,
            "action_id": action_id,
            "max_tokens": max_tokens,
            "consumed_tokens": int(usage["total_tokens"]),
            "reserved_tokens": int(usage["reserved_tokens"]),
            "requested_tokens": _row_tokens(row, "requested_tokens"),
            "projected_tokens": int(usage["effective_tokens"]),
            "remaining_tokens": None if max_tokens is None else max(0, max_tokens - int(usage["effective_tokens"])),
            "decision_event_id": row.get("event_id"),
        }
    consumed = int(usage["total_tokens"])
    reserved = int(usage["reserved_tokens"])
    projected = consumed + reserved + requested
    if max_tokens is None:
        decision, reason, remaining = "ALLOW", "contract_token_budget_unbounded", None
    elif projected > max_tokens:
        decision, reason = "STOP", "contract_max_tokens_exceeded"
        remaining = max(0, max_tokens - consumed - reserved)
    elif max_tokens == 0:
        decision = "ALLOW" if requested == 0 else "STOP"
        reason = "zero_budget_no_spend" if requested == 0 else "contract_max_tokens_exceeded"
        remaining = 0
    elif projected >= int(max_tokens * threshold):
        decision, reason = "COMPACT", "token_budget_near_limit"
        remaining = max(0, max_tokens - projected)
    else:
        decision, reason = "ALLOW", "within_token_budget"
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
        "reserved_tokens": reserved,
        "requested_tokens": requested,
        "projected_tokens": projected,
        "remaining_tokens": remaining,
        "compact_threshold": threshold,
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
                "reserved_tokens": reserved,
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
    """Check or atomically reserve planned token spend."""
    try:
        max_tokens = _contract_budget(contract)
        requested = _nonnegative_tokens(requested_tokens, "requested_tokens")
    except ValueError as exc:
        return {"status": "error", "decision": "STOP", "reason": str(exc)}
    task_id = str(task_id or "").strip()
    action_id = str(action_id or "").strip() or None
    if not task_id:
        return {"status": "error", "decision": "STOP", "reason": "task_id_required"}
    if record_decision and not action_id:
        return {"status": "error", "decision": "STOP", "reason": "action_id_required_for_reservation"}
    try:
        threshold = float(compact_threshold)
    except (TypeError, ValueError):
        return {"status": "error", "decision": "STOP", "reason": "invalid_compact_threshold"}
    if not 0 < threshold <= 1:
        return {"status": "error", "decision": "STOP", "reason": "invalid_compact_threshold"}
    try:
        with _governor_lock(repo_root):
            return _evaluate_locked(
                repo_root,
                contract,
                task_id=task_id,
                run_id=run_id,
                requested=requested,
                action_id=action_id,
                threshold=threshold,
                record_decision=record_decision,
                max_tokens=max_tokens,
            )
    except TimeoutError as exc:
        return {"status": "fail", "decision": "STOP", "reason": str(exc)}


def cancel_token_reservation(
    repo_root: Path,
    *,
    task_id: str,
    run_id: str | None,
    action_id: str,
    reason: str = "execution_not_started",
) -> dict[str, Any]:
    task_id = str(task_id or "").strip()
    action_id = str(action_id or "").strip()
    if not task_id or not action_id:
        return {"status": "error", "decision": "STOP", "reason": "task_id_and_action_id_required"}
    try:
        with _governor_lock(repo_root):
            integrity = verify_evidence_ledger(repo_root)
            if integrity.get("status") != "pass":
                return {"status": "fail", "decision": "STOP", "reason": "evidence_ledger_invalid"}
            rows = _scope_rows(repo_root, task_id=task_id, run_id=run_id)
            reservations = _active_reservations(rows)
            if action_id not in reservations:
                return {"status": "ok", "reason": "no_active_reservation", "idempotent": True}
            event = append_evidence_event(
                repo_root,
                event_type=TOKEN_CANCEL_EVENT,
                source="uacos.token.governor",
                status="cancelled",
                task_id=task_id,
                run_id=run_id,
                action_id=action_id,
                data={"reason": str(reason or "execution_not_started")},
                evidence_refs=[reservations[action_id].get("event_id")],
            )
            return {"status": "ok", "reason": "reservation_cancelled", "idempotent": False, "event_id": event["event_id"]}
    except TimeoutError as exc:
        return {"status": "fail", "decision": "STOP", "reason": str(exc)}


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
    """Atomically record actual spend exactly once and supersede its reservation."""
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
    try:
        with _governor_lock(repo_root):
            integrity = verify_evidence_ledger(repo_root)
            if integrity.get("status") != "pass":
                return {"status": "fail", "decision": "STOP", "reason": "evidence_ledger_invalid", "ledger_integrity": integrity}
            rows = _scope_rows(repo_root, task_id=task_id, run_id=run_id)
            existing = next((row for row in rows if row.get("event_type") == TOKEN_USAGE_EVENT and row.get("action_id") == action_id), None)
            if existing is not None:
                summary = token_usage_summary(repo_root, task_id=task_id, run_id=run_id)
                over = max_tokens is not None and int(summary["total_tokens"]) > max_tokens
                return {
                    "status": "blocked" if over else "ok",
                    "decision": "STOP" if over else "ALLOW",
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
            reservations = _active_reservations(rows)
            reservation_ref = reservations.get(action_id, {}).get("event_id")
            event = append_evidence_event(
                repo_root,
                event_type=TOKEN_USAGE_EVENT,
                source="uacos.token.governor",
                status="recorded",
                task_id=task_id,
                run_id=run_id,
                action_id=action_id,
                token_usage=usage_payload,
                evidence_refs=[reservation_ref] if reservation_ref else [],
                data={
                    "contract_id": contract.get("contract_id"),
                    "provider": provider,
                    "model": model,
                    "usage_kind": "actual",
                },
            )
            total = int(before["total_tokens"]) + actual
            exhausted = max_tokens is not None and total > max_tokens
            return {
                "status": "blocked" if exhausted else "ok",
                "decision": "STOP" if exhausted else "ALLOW",
                "reason": "actual_usage_exceeded_contract_budget" if exhausted else "actual_usage_recorded",
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
    except TimeoutError as exc:
        return {"status": "fail", "decision": "STOP", "reason": str(exc)}
