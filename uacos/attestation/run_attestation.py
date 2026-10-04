from __future__ import annotations

from typing import Any
from pathlib import Path
import hashlib
import hmac
import json

from uacos.execution.evidence_ledger import read_evidence_ledger, verify_evidence_ledger


ALLOWED_FINAL_STATUSES = {"pass", "fail", "blocked", "unknown"}
ALLOWED_ROLLBACK_STATES = {"not_required", "verified", "failed", "unknown"}


def _canonical(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(payload: bytes | str) -> str:
    raw = payload.encode("utf-8") if isinstance(payload, str) else payload
    return hashlib.sha256(raw).hexdigest()


def hash_contract(contract: dict[str, Any]) -> str:
    if contract.get("status") != "ok" or contract.get("version") != 2:
        raise ValueError("task_contract_v2_required")
    return _sha256(_canonical(contract))


def _normalized_status(value: str) -> str:
    status = str(value or "").strip().lower()
    if status not in ALLOWED_FINAL_STATUSES:
        raise ValueError("invalid_final_status")
    return status


def _normalized_rollback(value: str) -> str:
    state = str(value or "").strip().lower()
    if state not in ALLOWED_ROLLBACK_STATES:
        raise ValueError("invalid_rollback_state")
    return state


def _nonempty(value: str | None, reason: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise ValueError(reason)
    return normalized


def _find_verdict_event(
    repo_root: Path,
    *,
    verdict_event_id: str,
    run_id: str,
    task_id: str | None,
    final_status: str,
) -> dict[str, Any] | None:
    for row in read_evidence_ledger(repo_root):
        if row.get("event_id") != verdict_event_id:
            continue
        if str(row.get("event_type") or "") != "outcome_verdict":
            return None
        if row.get("run_id") != run_id:
            return None
        if task_id is not None and row.get("task_id") != task_id:
            return None
        if str(row.get("status") or "").strip().lower() != final_status:
            return None
        return row
    return None


def create_run_attestation(
    repo_root: Path,
    *,
    contract: dict[str, Any],
    run_id: str,
    workspace_sha: str,
    final_status: str,
    rollback_state: str,
    verdict_event_id: str,
    task_id: str | None = None,
    signing_key: bytes | None = None,
) -> dict[str, Any]:
    """Create a canonical evidence-bound attestation for one run.

    The supplied final status is accepted only when a canonical ``outcome_verdict``
    event with the same run/task/status already exists. This function never derives
    PASS from prose or from an arbitrary caller-supplied string.
    """
    run_id = _nonempty(run_id, "run_id_required")
    workspace_sha = _nonempty(workspace_sha, "workspace_sha_required")
    verdict_event_id = _nonempty(verdict_event_id, "verdict_event_id_required")
    final_status = _normalized_status(final_status)
    rollback_state = _normalized_rollback(rollback_state)
    task_id = str(task_id or "").strip() or None
    contract_hash = hash_contract(contract)

    integrity = verify_evidence_ledger(repo_root)
    if integrity.get("status") != "pass":
        return {
            "status": "fail",
            "reason": "evidence_ledger_invalid",
            "ledger_integrity": integrity,
        }

    verdict = _find_verdict_event(
        repo_root,
        verdict_event_id=verdict_event_id,
        run_id=run_id,
        task_id=task_id,
        final_status=final_status,
    )
    if verdict is None:
        return {
            "status": "fail",
            "reason": "canonical_verdict_evidence_missing_or_mismatched",
            "verdict_event_id": verdict_event_id,
        }

    payload = {
        "version": 1,
        "run_id": run_id,
        "task_id": task_id,
        "workspace_sha": workspace_sha,
        "contract_id": contract.get("contract_id"),
        "contract_hash": contract_hash,
        "verdict_event_id": verdict_event_id,
        "evidence_head_hash": integrity["head_hash"],
        "evidence_records": int(integrity.get("records", 0)),
        "final_status": final_status,
        "rollback_state": rollback_state,
    }
    attestation_hash = _sha256(_canonical(payload))
    result: dict[str, Any] = {
        "status": "ok",
        "reason": "run_attested",
        "attestation": {
            **payload,
            "attestation_hash": attestation_hash,
            "signature_algorithm": "hmac-sha256" if signing_key is not None else None,
            "signature": None,
        },
    }
    if signing_key is not None:
        if not isinstance(signing_key, (bytes, bytearray)) or not signing_key:
            raise ValueError("signing_key_must_be_nonempty_bytes")
        result["attestation"]["signature"] = hmac.new(
            bytes(signing_key), attestation_hash.encode("ascii"), hashlib.sha256
        ).hexdigest()
    return result


def verify_run_attestation(
    attestation: dict[str, Any],
    *,
    expected_contract: dict[str, Any] | None = None,
    expected_workspace_sha: str | None = None,
    expected_evidence_head_hash: str | None = None,
    expected_verdict_event_id: str | None = None,
    signing_key: bytes | None = None,
) -> dict[str, Any]:
    """Verify canonical hash, expectations, verdict binding, and optional HMAC."""
    if not isinstance(attestation, dict):
        return {"status": "fail", "reason": "attestation_must_be_mapping"}
    if attestation.get("version") != 1:
        return {"status": "fail", "reason": "unsupported_attestation_version"}

    unsigned = {
        key: attestation.get(key)
        for key in (
            "version",
            "run_id",
            "task_id",
            "workspace_sha",
            "contract_id",
            "contract_hash",
            "verdict_event_id",
            "evidence_head_hash",
            "evidence_records",
            "final_status",
            "rollback_state",
        )
    }
    try:
        _nonempty(unsigned["run_id"], "run_id_required")
        _nonempty(unsigned["workspace_sha"], "workspace_sha_required")
        _nonempty(unsigned["verdict_event_id"], "verdict_event_id_required")
        _normalized_status(str(unsigned["final_status"] or ""))
        _normalized_rollback(str(unsigned["rollback_state"] or ""))
        if int(unsigned["evidence_records"]) < 0:
            raise ValueError("evidence_records_must_be_nonnegative")
    except (TypeError, ValueError) as exc:
        return {"status": "fail", "reason": str(exc)}

    expected_hash = _sha256(_canonical(unsigned))
    if not hmac.compare_digest(str(attestation.get("attestation_hash") or ""), expected_hash):
        return {"status": "fail", "reason": "attestation_hash_mismatch"}

    if expected_contract is not None:
        try:
            expected_contract_hash = hash_contract(expected_contract)
        except ValueError as exc:
            return {"status": "fail", "reason": str(exc)}
        if unsigned["contract_hash"] != expected_contract_hash:
            return {"status": "fail", "reason": "contract_hash_mismatch"}
        if unsigned["contract_id"] != expected_contract.get("contract_id"):
            return {"status": "fail", "reason": "contract_id_mismatch"}

    if expected_workspace_sha is not None and unsigned["workspace_sha"] != str(expected_workspace_sha):
        return {"status": "fail", "reason": "workspace_sha_mismatch"}
    if expected_evidence_head_hash is not None and unsigned["evidence_head_hash"] != str(expected_evidence_head_hash):
        return {"status": "fail", "reason": "evidence_head_hash_mismatch"}
    if expected_verdict_event_id is not None and unsigned["verdict_event_id"] != str(expected_verdict_event_id):
        return {"status": "fail", "reason": "verdict_event_id_mismatch"}

    signature = attestation.get("signature")
    algorithm = attestation.get("signature_algorithm")
    if signing_key is not None:
        if not isinstance(signing_key, (bytes, bytearray)) or not signing_key:
            return {"status": "fail", "reason": "signing_key_must_be_nonempty_bytes"}
        if algorithm != "hmac-sha256" or not signature:
            return {"status": "fail", "reason": "signature_required"}
        expected_signature = hmac.new(bytes(signing_key), expected_hash.encode("ascii"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(str(signature), expected_signature):
            return {"status": "fail", "reason": "signature_mismatch"}
    elif signature is not None or algorithm is not None:
        return {"status": "partial", "reason": "signature_not_verified", "attestation_hash": expected_hash}

    return {"status": "pass", "reason": "attestation_verified", "attestation_hash": expected_hash}
