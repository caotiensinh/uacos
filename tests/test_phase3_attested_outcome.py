from __future__ import annotations

from pathlib import Path

from uacos.attestation.attested_outcome import verify_and_attest_task_outcome
from uacos.execution.evidence_ledger import append_evidence_event
from uacos.orchestrator.contract import build_task_contract_v2


def _contract() -> dict:
    return build_task_contract_v2(
        "verify and attest",
        required_tests=["test:ok"],
        required_evidence=["test:ok"],
    )


def _seed_result(tmp_path: Path, *, test_status: str = "pass") -> None:
    append_evidence_event(
        tmp_path,
        event_type="test_result",
        source="test",
        status=test_status,
        task_id="TASK-1",
        run_id="RUN-1",
        data={"check_id": "test:ok"},
    )
    append_evidence_event(
        tmp_path,
        event_type="result_recorded",
        source="test",
        status="pass",
        task_id="TASK-1",
        run_id="RUN-1",
    )


def test_pass_outcome_is_attested_as_pass_from_exact_verdict_event(tmp_path: Path):
    _seed_result(tmp_path, test_status="pass")

    result = verify_and_attest_task_outcome(
        tmp_path,
        _contract(),
        task_id="TASK-1",
        run_id="RUN-1",
        workspace_sha="abc123",
        rollback_state="not_required",
    )

    assert result["status"] == "ok"
    assert result["final_status"] == "pass"
    assert result["verdict"]["overall"] == "PASS"
    assert result["attestation"]["final_status"] == "pass"
    assert result["attestation"]["verdict_event_id"] == result["verdict"]["verdict_event_id"]


def test_fail_outcome_is_attested_as_fail_never_upgraded_to_pass(tmp_path: Path):
    _seed_result(tmp_path, test_status="fail")

    result = verify_and_attest_task_outcome(
        tmp_path,
        _contract(),
        task_id="TASK-1",
        run_id="RUN-1",
        workspace_sha="abc123",
        rollback_state="not_required",
    )

    assert result["status"] == "ok"
    assert result["final_status"] == "fail"
    assert result["verdict"]["overall"] == "FAIL"
    assert result["attestation"]["final_status"] == "fail"
    assert result["attestation"]["verdict_event_id"] == result["verdict"]["verdict_event_id"]


def test_invalid_ledger_cannot_produce_attestation(tmp_path: Path):
    _seed_result(tmp_path)
    ledger_path = tmp_path / ".uacos" / "evidence" / "ledger.jsonl"
    text = ledger_path.read_text(encoding="utf-8")
    ledger_path.write_text(text.replace('"status":"pass"', '"status":"fail"', 1), encoding="utf-8")

    result = verify_and_attest_task_outcome(
        tmp_path,
        _contract(),
        task_id="TASK-1",
        run_id="RUN-1",
        workspace_sha="abc123",
        rollback_state="not_required",
    )

    assert result["status"] == "fail"
    assert result["reason"] == "canonical_outcome_verdict_not_recorded"
    assert result["attestation"] is None


def test_signed_attested_outcome_preserves_signature_intent(tmp_path: Path):
    _seed_result(tmp_path)

    result = verify_and_attest_task_outcome(
        tmp_path,
        _contract(),
        task_id="TASK-1",
        run_id="RUN-1",
        workspace_sha="abc123",
        rollback_state="not_required",
        signing_key=b"secret",
    )

    assert result["status"] == "ok"
    assert result["attestation"]["signature_algorithm"] == "hmac-sha256"
    assert result["attestation"]["signature"]
