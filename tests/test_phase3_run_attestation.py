from __future__ import annotations

from pathlib import Path

import pytest

from uacos.attestation.run_attestation import create_run_attestation, verify_run_attestation
from uacos.execution.evidence_ledger import append_evidence_event, verify_evidence_ledger
from uacos.orchestrator.contract import build_task_contract_v2


def _contract() -> dict:
    return build_task_contract_v2(
        "change service safely",
        allowed_files=["svc.py"],
        required_tests=["tests/test_svc.py"],
        required_evidence=["test:svc"],
        max_tokens=1000,
    )


def _seed_verdict(tmp_path: Path, *, status: str = "pass", task_id: str = "TASK-1", run_id: str = "RUN-1") -> str:
    append_evidence_event(
        tmp_path,
        event_type="test_result",
        source="test",
        status="pass",
        task_id=task_id,
        run_id=run_id,
        data={"check_id": "test:svc"},
    )
    verdict = append_evidence_event(
        tmp_path,
        event_type="outcome_verdict",
        source="uacos.validation.outcome_verifier",
        status=status,
        task_id=task_id,
        run_id=run_id,
        data={"overall": status.upper()},
    )
    return verdict["event_id"]


def _attest(tmp_path: Path, *, signing_key: bytes | None = None) -> dict:
    verdict_event_id = _seed_verdict(tmp_path)
    result = create_run_attestation(
        tmp_path,
        contract=_contract(),
        task_id="TASK-1",
        run_id="RUN-1",
        workspace_sha="abc123",
        final_status="pass",
        rollback_state="not_required",
        verdict_event_id=verdict_event_id,
        signing_key=signing_key,
    )
    assert result["status"] == "ok"
    return result["attestation"]


def test_unsigned_attestation_binds_contract_workspace_evidence_and_verdict(tmp_path: Path):
    attestation = _attest(tmp_path)
    ledger = verify_evidence_ledger(tmp_path)

    result = verify_run_attestation(
        attestation,
        expected_contract=_contract(),
        expected_workspace_sha="abc123",
        expected_evidence_head_hash=ledger["head_hash"],
        expected_verdict_event_id=attestation["verdict_event_id"],
    )

    assert result["status"] == "pass"
    assert attestation["contract_id"] == _contract()["contract_id"]
    assert attestation["evidence_head_hash"] == ledger["head_hash"]
    assert attestation["evidence_records"] == 2
    assert attestation["verdict_event_id"].startswith("EV-")


def test_creation_rejects_missing_or_fake_verdict_event(tmp_path: Path):
    append_evidence_event(tmp_path, event_type="test_result", source="test", status="pass", task_id="TASK-1", run_id="RUN-1")

    result = create_run_attestation(
        tmp_path,
        contract=_contract(),
        task_id="TASK-1",
        run_id="RUN-1",
        workspace_sha="abc123",
        final_status="pass",
        rollback_state="not_required",
        verdict_event_id="EV-does-not-exist",
    )

    assert result["status"] == "fail"
    assert result["reason"] == "canonical_verdict_evidence_missing_or_mismatched"


def test_creation_rejects_verdict_status_mismatch(tmp_path: Path):
    verdict_event_id = _seed_verdict(tmp_path, status="fail")

    result = create_run_attestation(
        tmp_path,
        contract=_contract(),
        task_id="TASK-1",
        run_id="RUN-1",
        workspace_sha="abc123",
        final_status="pass",
        rollback_state="not_required",
        verdict_event_id=verdict_event_id,
    )

    assert result["status"] == "fail"
    assert result["reason"] == "canonical_verdict_evidence_missing_or_mismatched"


def test_creation_rejects_verdict_run_or_task_mismatch(tmp_path: Path):
    verdict_event_id = _seed_verdict(tmp_path, task_id="OTHER", run_id="OTHER-RUN")

    result = create_run_attestation(
        tmp_path,
        contract=_contract(),
        task_id="TASK-1",
        run_id="RUN-1",
        workspace_sha="abc123",
        final_status="pass",
        rollback_state="not_required",
        verdict_event_id=verdict_event_id,
    )

    assert result["status"] == "fail"
    assert result["reason"] == "canonical_verdict_evidence_missing_or_mismatched"


def test_attestation_hash_detects_tampered_workspace(tmp_path: Path):
    attestation = _attest(tmp_path)
    attestation["workspace_sha"] = "evil"
    assert verify_run_attestation(attestation) == {"status": "fail", "reason": "attestation_hash_mismatch"}


def test_expected_workspace_rejects_stale_or_wrong_workspace(tmp_path: Path):
    attestation = _attest(tmp_path)
    assert verify_run_attestation(attestation, expected_workspace_sha="different") == {"status": "fail", "reason": "workspace_sha_mismatch"}


def test_changed_contract_is_rejected_even_when_contract_id_field_is_unchanged(tmp_path: Path):
    attestation = _attest(tmp_path)
    changed = dict(_contract())
    changed["spec"] = "different spec"
    assert verify_run_attestation(attestation, expected_contract=changed) == {"status": "fail", "reason": "contract_hash_mismatch"}


def test_new_evidence_head_can_invalidate_stale_attestation(tmp_path: Path):
    attestation = _attest(tmp_path)
    append_evidence_event(tmp_path, event_type="result_recorded", source="test", status="pass", task_id="TASK-1", run_id="RUN-1")
    current_head = verify_evidence_ledger(tmp_path)["head_hash"]
    assert verify_run_attestation(attestation, expected_evidence_head_hash=current_head) == {"status": "fail", "reason": "evidence_head_hash_mismatch"}


def test_expected_verdict_event_detects_wrong_binding(tmp_path: Path):
    attestation = _attest(tmp_path)
    assert verify_run_attestation(attestation, expected_verdict_event_id="EV-other") == {"status": "fail", "reason": "verdict_event_id_mismatch"}


def test_signed_attestation_verifies_with_exact_key(tmp_path: Path):
    key = b"test-key"
    attestation = _attest(tmp_path, signing_key=key)
    result = verify_run_attestation(attestation, signing_key=key)
    assert result["status"] == "pass"
    assert attestation["signature_algorithm"] == "hmac-sha256"
    assert attestation["signature"]


def test_signed_attestation_fails_with_wrong_key(tmp_path: Path):
    attestation = _attest(tmp_path, signing_key=b"correct")
    assert verify_run_attestation(attestation, signing_key=b"wrong") == {"status": "fail", "reason": "signature_mismatch"}


def test_signed_attestation_without_key_is_only_partial_verification(tmp_path: Path):
    attestation = _attest(tmp_path, signing_key=b"correct")
    result = verify_run_attestation(attestation)
    assert result["status"] == "partial"
    assert result["reason"] == "signature_not_verified"


def test_creation_fails_closed_when_evidence_ledger_is_tampered(tmp_path: Path):
    verdict_event_id = _seed_verdict(tmp_path)
    ledger_path = tmp_path / ".uacos" / "evidence" / "ledger.jsonl"
    text = ledger_path.read_text(encoding="utf-8")
    ledger_path.write_text(text.replace('"status":"pass"', '"status":"fail"', 1), encoding="utf-8")

    result = create_run_attestation(
        tmp_path,
        contract=_contract(),
        task_id="TASK-1",
        run_id="RUN-1",
        workspace_sha="abc123",
        final_status="pass",
        rollback_state="not_required",
        verdict_event_id=verdict_event_id,
    )
    assert result["status"] == "fail"
    assert result["reason"] == "evidence_ledger_invalid"


def test_invalid_verdict_and_rollback_state_are_rejected(tmp_path: Path):
    verdict_event_id = _seed_verdict(tmp_path)
    with pytest.raises(ValueError, match="invalid_final_status"):
        create_run_attestation(
            tmp_path,
            contract=_contract(),
            run_id="RUN-1",
            workspace_sha="abc123",
            final_status="done",
            rollback_state="not_required",
            verdict_event_id=verdict_event_id,
        )

    with pytest.raises(ValueError, match="invalid_rollback_state"):
        create_run_attestation(
            tmp_path,
            contract=_contract(),
            run_id="RUN-1",
            workspace_sha="abc123",
            final_status="pass",
            rollback_state="maybe",
            verdict_event_id=verdict_event_id,
        )
