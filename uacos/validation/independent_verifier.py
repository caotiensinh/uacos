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
from uacos.validation.outcome_verifier import verify_task_outcome

INDEPENDENT_VERDICT_EVENT = "independent_verification"
_LOCK_TIMEOUT_SEC = 5.0
_LOCK_STALE_SEC = 30.0


@contextmanager
def _verification_lock(repo_root: Path):
    lock_path = evidence_ledger_path(repo_root).parent / ".independent_verifier.lock"
    deadline = time.monotonic() + _LOCK_TIMEOUT_SEC
    fd: int | None = None
    while fd is None:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode("ascii", errors="ignore"))
            os.fsync(fd)
        except FileExistsError:
            try:
                if time.time() - lock_path.stat().st_mtime > _LOCK_STALE_SEC:
                    lock_path.unlink(missing_ok=True)
                    continue
            except FileNotFoundError:
                continue
            if time.monotonic() >= deadline:
                raise TimeoutError("independent_verifier_lock_timeout")
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


def _clean_identity(value: Any, reason: str) -> str:
    identity = str(value or "").strip()
    if not identity:
        raise ValueError(reason)
    return identity


def _existing_verification(
    repo_root: Path,
    *,
    task_id: str,
    run_id: str,
    verification_id: str,
) -> dict[str, Any] | None:
    for row in read_evidence_ledger(repo_root):
        if (
            row.get("event_type") == INDEPENDENT_VERDICT_EVENT
            and row.get("task_id") == task_id
            and row.get("run_id") == run_id
            and row.get("action_id") == verification_id
        ):
            return row
    return None


def verify_independently(
    repo_root: Path,
    contract: dict[str, Any],
    *,
    task_id: str,
    run_id: str,
    actor_id: str,
    verifier_id: str,
    verification_id: str,
    record_verdict: bool = True,
) -> dict[str, Any]:
    """Recompute a task verdict from canonical evidence under independent provenance.

    Agent prose/conclusions are not accepted as inputs. The verifier consumes the Task
    Contract V2 and canonical evidence ledger, delegates deterministic outcome calculation
    to ``verify_task_outcome``, and rejects self-verification.
    """
    repo_root = repo_root.resolve()
    if contract.get("status") != "ok" or contract.get("version") != 2:
        return {"status": "error", "overall": "FAIL", "reason": "task_contract_v2_required"}
    try:
        task_id = _clean_identity(task_id, "task_id_required")
        run_id = _clean_identity(run_id, "run_id_required")
        actor_id = _clean_identity(actor_id, "actor_id_required")
        verifier_id = _clean_identity(verifier_id, "verifier_id_required")
        verification_id = _clean_identity(verification_id, "verification_id_required")
    except ValueError as exc:
        return {"status": "error", "overall": "FAIL", "reason": str(exc)}
    if actor_id == verifier_id:
        return {
            "status": "fail",
            "overall": "FAIL",
            "reason": "self_verification_forbidden",
            "task_id": task_id,
            "run_id": run_id,
            "actor_id": actor_id,
            "verifier_id": verifier_id,
        }

    integrity = verify_evidence_ledger(repo_root)
    if integrity.get("status") != "pass":
        return {
            "status": "fail",
            "overall": "FAIL",
            "reason": "evidence_ledger_invalid",
            "ledger_integrity": integrity,
        }

    try:
        with _verification_lock(repo_root):
            existing = _existing_verification(
                repo_root,
                task_id=task_id,
                run_id=run_id,
                verification_id=verification_id,
            )
            if existing is not None:
                data = existing.get("data") if isinstance(existing.get("data"), dict) else {}
                same_identity = (
                    data.get("actor_id") == actor_id
                    and data.get("verifier_id") == verifier_id
                    and data.get("contract_id") == contract.get("contract_id")
                )
                if not same_identity:
                    return {
                        "status": "fail",
                        "overall": "FAIL",
                        "reason": "verification_id_conflict",
                        "verification_event_id": existing.get("event_id"),
                    }
                overall = str(data.get("overall") or "FAIL")
                return {
                    "status": "pass" if overall == "PASS" else "fail",
                    "overall": overall,
                    "reason": "verification_already_recorded",
                    "idempotent": True,
                    "task_id": task_id,
                    "run_id": run_id,
                    "actor_id": actor_id,
                    "verifier_id": verifier_id,
                    "verification_id": verification_id,
                    "contract_id": contract.get("contract_id"),
                    "verification_event_id": existing.get("event_id"),
                    "evidence_refs": list(existing.get("evidence_refs") or []),
                }

            outcome = verify_task_outcome(
                repo_root,
                contract,
                task_id=task_id,
                run_id=run_id,
                record_verdict=False,
            )
            overall = "PASS" if outcome.get("overall") == "PASS" else "FAIL"
            status = "pass" if overall == "PASS" else "fail"
            reason = "independent_outcome_verified" if overall == "PASS" else "independent_outcome_failed"
            result = {
                "status": status,
                "overall": overall,
                "reason": reason,
                "idempotent": False,
                "task_id": task_id,
                "run_id": run_id,
                "actor_id": actor_id,
                "verifier_id": verifier_id,
                "verification_id": verification_id,
                "contract_id": contract.get("contract_id"),
                "outcome": outcome,
                "evidence_refs": list(outcome.get("evidence_refs") or []),
                "ledger_integrity": outcome.get("ledger_integrity", integrity),
            }
            if not record_verdict:
                return result

            event = append_evidence_event(
                repo_root,
                event_type=INDEPENDENT_VERDICT_EVENT,
                source="uacos.validation.independent_verifier",
                status=status,
                task_id=task_id,
                run_id=run_id,
                action_id=verification_id,
                evidence_refs=result["evidence_refs"],
                parent_event_ids=result["evidence_refs"],
                data={
                    "contract_id": contract.get("contract_id"),
                    "actor_id": actor_id,
                    "verifier_id": verifier_id,
                    "verification_id": verification_id,
                    "overall": overall,
                    "outcome_reason": outcome.get("reason"),
                    "layers": {
                        name: value.get("state")
                        for name, value in (outcome.get("layers") or {}).items()
                    },
                    "done_state": (outcome.get("done_predicate") or {}).get("state"),
                },
            )
            result["verification_event_id"] = event["event_id"]
            return result
    except TimeoutError as exc:
        return {"status": "fail", "overall": "FAIL", "reason": str(exc)}
