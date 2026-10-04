from __future__ import annotations

from pathlib import Path

from uacos.attestation.run_attestation import create_run_attestation, verify_run_attestation
from uacos.execution.evidence_ledger import append_evidence_event
from uacos.orchestrator.contract import build_task_contract_v2


def _contract() -> dict:
    return build_task_contract_v2(
        "attest safely",
        allowed_files=["svc.py"],
        required_tests=["tests/test_svc.py"],
        required_evidence=["test:svc"],
    )


def _verdict(tmp_path: Path, *, task_id: str | None, run_id: str = "RUN-1") -> str:
    event = append_evidence_event(
        tmp_path,
        event_type="outcome_verdict",
        source="uacos.validation.outcome_verifier",
        status="pass",
        task_id=task_id,
        run_id=run_id,
        data={"overall": "PASS"},
    )
    return event["event_id"]


def test_signed_attestation_cannot_be_downgraded_by_stripping_signature_fields(tmp_path: Path):
    verdict = _verdict(tmp_path, task_id="TASK-1")
    result = create_run_attestation(
        tmp_path,
        contract=_contract(),
        task_id="TASK-1",
        run_id="RUN-1",
        workspace_sha="abc123",
        final_status="pass",
        rollback_state="not_required",
        verdict_event_id=verdict,
        signing_key=b"secret",
    )
    attestation = dict(result["attestation"])
    attestation["signature"] = None
    attestation["signature_algorithm"] = None

    verification = verify_run_attestation(attestation)

    assert verification == {"status": "fail", "reason": "attestation_hash_mismatch"}


def test_signed_attestation_with_algorithm_but_missing_signature_fails(tmp_path: Path):
    verdict = _verdict(tmp_path, task_id="TASK-1")
    result = create_run_attestation(
        tmp_path,
        contract=_contract(),
        task_id="TASK-1",
        run_id="RUN-1",
        workspace_sha="abc123",
        final_status="pass",
        rollback_state="not_required",
        verdict_event_id=verdict,
        signing_key=b"secret",
    )
    attestation = dict(result["attestation"])
    attestation["signature"] = None

    verification = verify_run_attestation(attestation)

    assert verification == {"status": "fail", "reason": "signature_missing"}


def test_omitted_task_id_cannot_bind_task_scoped_verdict(tmp_path: Path):
    verdict = _verdict(tmp_path, task_id="TASK-1")

    result = create_run_attestation(
        tmp_path,
        contract=_contract(),
        task_id=None,
        run_id="RUN-1",
        workspace_sha="abc123",
        final_status="pass",
        rollback_state="not_required",
        verdict_event_id=verdict,
    )

    assert result["status"] == "fail"
    assert result["reason"] == "canonical_verdict_evidence_missing_or_mismatched"
