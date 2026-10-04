from __future__ import annotations

from pathlib import Path

from uacos.execution.evidence_ledger import append_evidence_event
from uacos.metrics.reliability_economics import collect_reliability_economics


def _verdict(root: Path, run_id: str, status: str) -> None:
    append_evidence_event(
        root,
        event_type="outcome_verdict",
        source="test",
        status=status,
        run_id=run_id,
        data={"overall": status.upper()},
    )


def _tokens(root: Path, run_id: str, total: int, **data) -> None:
    append_evidence_event(
        root,
        event_type="token_usage_settled",
        source="test",
        status="pass",
        run_id=run_id,
        token_usage={"total_tokens": total},
        data=data,
    )


def test_verified_success_and_token_economics_use_canonical_events(tmp_path: Path):
    _verdict(tmp_path, "R1", "pass")
    _verdict(tmp_path, "R2", "fail")
    _tokens(tmp_path, "R1", 100)
    _tokens(tmp_path, "R2", 50)

    result = collect_reliability_economics(tmp_path)
    metrics = result["metrics"]

    assert result["status"] == "ok"
    assert metrics["verified_runs"] == 2
    assert metrics["verified_successes"] == 1
    assert metrics["verified_failures"] == 1
    assert metrics["verified_success_rate"] == 0.5
    assert metrics["total_settled_tokens"] == 150
    assert metrics["tokens_per_verified_run"] == 75.0
    assert metrics["tokens_per_verified_success"] == 150.0


def test_latest_outcome_verdict_per_run_is_authoritative(tmp_path: Path):
    _verdict(tmp_path, "R1", "fail")
    _verdict(tmp_path, "R1", "pass")

    metrics = collect_reliability_economics(tmp_path)["metrics"]

    assert metrics["verified_runs"] == 1
    assert metrics["verified_successes"] == 1
    assert metrics["verified_failures"] == 0


def test_retry_token_ratio_is_measured_only_from_explicit_retry_markers(tmp_path: Path):
    _verdict(tmp_path, "R1", "pass")
    _tokens(tmp_path, "R1", 80)
    _tokens(tmp_path, "R1", 20, retry=True)

    metrics = collect_reliability_economics(tmp_path)["metrics"]

    assert metrics["total_settled_tokens"] == 100
    assert metrics["retry_tokens"] == 20
    assert metrics["retry_token_ratio"] == 0.2


def test_recovery_and_rollback_metrics_use_recovery_decision_evidence(tmp_path: Path):
    append_evidence_event(
        tmp_path,
        event_type="recovery_decision",
        source="test",
        status="repair",
        run_id="R1",
        data={
            "real_failure_observed": True,
            "mutation_applied": True,
            "rollback_verified": True,
            "repeated_failure": False,
            "decision": {"action": "REPAIR"},
        },
    )
    append_evidence_event(
        tmp_path,
        event_type="recovery_decision",
        source="test",
        status="stop",
        run_id="R2",
        data={
            "real_failure_observed": True,
            "mutation_applied": True,
            "rollback_verified": False,
            "repeated_failure": True,
            "decision": {"action": "STOP"},
        },
    )

    metrics = collect_reliability_economics(tmp_path)["metrics"]

    assert metrics["recovery_decisions"] == 2
    assert metrics["recovery_actions"] == {"REPAIR": 1, "STOP": 1}
    assert metrics["repair_decisions"] == 1
    assert metrics["repeated_failures"] == 1
    assert metrics["mutation_failures_requiring_rollback"] == 2
    assert metrics["verified_rollbacks"] == 1
    assert metrics["rollback_success_rate"] == 0.5


def test_missing_denominators_are_none_not_optimistic_zero(tmp_path: Path):
    result = collect_reliability_economics(tmp_path)
    metrics = result["metrics"]

    assert metrics["verified_runs"] == 0
    assert metrics["verified_success_rate"] is None
    assert metrics["tokens_per_verified_success"] is None
    assert metrics["rollback_success_rate"] is None
    assert "false_completion_rate" in result["unavailable_metrics"]
    assert "unsupported_claim_rate" in result["unavailable_metrics"]


def test_corrupt_ledger_fails_metrics_closed(tmp_path: Path):
    _verdict(tmp_path, "R1", "pass")
    ledger = tmp_path / ".uacos" / "evidence" / "ledger.jsonl"
    ledger.write_text(ledger.read_text(encoding="utf-8").replace('"status":"pass"', '"status":"fail"', 1), encoding="utf-8")

    result = collect_reliability_economics(tmp_path)

    assert result["status"] == "fail"
    assert result["reason"] == "evidence_ledger_invalid"
    assert result["metrics"] is None
