from __future__ import annotations

from pathlib import Path
from typing import Any

from uacos.attestation.run_attestation import create_run_attestation
from uacos.validation.outcome_verifier import verify_task_outcome


def verify_and_attest_task_outcome(
    repo_root: Path,
    contract: dict[str, Any],
    *,
    task_id: str | None,
    run_id: str,
    workspace_sha: str,
    rollback_state: str,
    signing_key: bytes | None = None,
) -> dict[str, Any]:
    """Run the deterministic outcome verifier and attest exactly that verdict.

    The verifier remains the authority. This binder refuses to create an attestation
    when no canonical verdict event was recorded, and it never upgrades a FAIL verdict
    into PASS.
    """
    verdict = verify_task_outcome(
        Path(repo_root),
        contract,
        task_id=task_id,
        run_id=run_id,
        record_verdict=True,
    )
    verdict_event_id = str(verdict.get("verdict_event_id") or "").strip()
    if not verdict_event_id:
        return {
            "status": "fail",
            "reason": "canonical_outcome_verdict_not_recorded",
            "verdict": verdict,
            "attestation": None,
        }

    overall = str(verdict.get("overall") or "").strip().upper()
    if overall == "PASS":
        final_status = "pass"
    elif overall == "FAIL":
        final_status = "fail"
    else:
        return {
            "status": "fail",
            "reason": "outcome_verdict_state_invalid",
            "verdict": verdict,
            "attestation": None,
        }

    attestation_result = create_run_attestation(
        Path(repo_root),
        contract=contract,
        task_id=task_id,
        run_id=run_id,
        workspace_sha=workspace_sha,
        final_status=final_status,
        rollback_state=rollback_state,
        verdict_event_id=verdict_event_id,
        signing_key=signing_key,
    )
    if attestation_result.get("status") != "ok":
        return {
            "status": "fail",
            "reason": "run_attestation_failed",
            "verdict": verdict,
            "attestation": None,
            "attestation_result": attestation_result,
        }

    return {
        "status": "ok",
        "reason": "outcome_verified_and_attested",
        "final_status": final_status,
        "verdict": verdict,
        "attestation": attestation_result["attestation"],
    }
