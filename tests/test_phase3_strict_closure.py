from __future__ import annotations

import json
from pathlib import Path

from uacos.execution.evidence_ledger import append_evidence_event
from uacos.validation.phase3_closure import Phase3ClosurePaths, evaluate_phase3_closure


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _paths() -> Phase3ClosurePaths:
    return Phase3ClosurePaths(
        real_agent="reports/real.json",
        comparative="reports/comparative.json",
        attestation="reports/attestation.json",
        reliability_economics="reports/economics.json",
        soak="reports/soak.json",
        jev_ab="reports/jev_ab.json",
        evidence_summary="reports/evidence.json",
    )


def _seed_valid(root: Path) -> None:
    _write(root / "reports/real.json", {"status": "pass", "executed_count": 2, "passed_count": 2})
    _write(
        root / "reports/comparative.json",
        {
            "status": "pass",
            "real_provider_execution": True,
            "provider": "provider-x",
            "model": "model-y",
            "repeats": 3,
        },
    )
    _write(
        root / "reports/attestation.json",
        {
            "status": "pass",
            "reason": "attestation_verified",
            "attestation_hash": "a" * 64,
        },
    )
    _write(
        root / "reports/economics.json",
        {
            "status": "ok",
            "reason": "canonical_evidence_metrics_computed",
            "ledger": {"status": "pass", "head_hash": "b" * 64, "records": 8},
            "metrics": {"verified_success_rate": 1.0, "tokens_per_verified_success": 100.0},
        },
    )
    _write(
        root / "reports/soak.json",
        {
            "status": "pass",
            "method": "repeated_observation_sustained_reliability_v1",
            "summary": {
                "iterations": 10,
                "verified_success_rate": 1.0,
                "token_drift_ratio": 0.05,
                "latency_drift_ratio": 0.08,
                "critical_defects": {
                    "false_completion": 0,
                    "unsupported_claim": 0,
                    "bad_commit": 0,
                    "rollback_failed": 0,
                    "leaked_process": 0,
                    "stale_state": 0,
                    "corrupted_evidence": 0,
                    "lease_conflict_unblocked": 0,
                },
            },
            "checks": {
                "minimum_iterations": True,
                "verified_success_rate": True,
                "zero_critical_defects": True,
                "token_drift_bounded": True,
                "latency_drift_bounded": True,
            },
        },
    )
    observations = []
    for repeat in range(1, 4):
        observations.append({"task_id": "T1", "mode": "jev_off", "repeat": repeat})
        observations.append({"task_id": "T1", "mode": "jev_on", "repeat": repeat})
    _write(
        root / "reports/jev_ab.json",
        {
            "status": "pass",
            "method": "same-provider-model_repeated_jev_off_on_v1",
            "modes": ["jev_off", "jev_on"],
            "thresholds": {"min_repeats": 3},
            "summaries": {"jev_off": {"runs": 3}, "jev_on": {"runs": 3}},
            "checks": {
                "verified_success_not_regressed": True,
                "token_cost_bounded": True,
                "latency_cost_bounded": True,
                "ranking_quality_not_regressed": True,
            },
            "observations": observations,
        },
    )

    claim = append_evidence_event(
        root,
        event_type="claim_decision",
        source="claim_firewall",
        status="supported",
        data={"claim_id": "C1", "decision": "SUPPORTED"},
    )
    mutation_gate = append_evidence_event(
        root,
        event_type="mutation_gate",
        source="evidence_gate",
        status="pass",
        data={"decision": "allow", "reason": "evidence_requirements_satisfied"},
    )
    outcome = append_evidence_event(
        root,
        event_type="outcome_verdict",
        source="uacos.validation.outcome_verifier",
        status="pass",
        data={"overall": "PASS", "done_state": "done"},
    )
    rollback = append_evidence_event(
        root,
        event_type="recovery_decision",
        source="uacos.runtime.evidence_guided_recovery",
        status="repair",
        data={
            "real_failure_observed": True,
            "mutation_applied": True,
            "rollback_verified": True,
            "decision": {"action": "REPAIR"},
        },
    )
    lease = append_evidence_event(
        root,
        event_type="resource_lease",
        source="uacos.runtime.leased_safe_execution",
        status="blocked",
        data={"reason": "resource_lease_conflict", "owner_id": "agent-a"},
    )

    _write(
        root / "reports/evidence.json",
        {
            "contract_v2_enforced": True,
            "canonical_evidence_ledger_valid": True,
            "claim_firewall_enforced": True,
            "mutation_gate_enforced": True,
            "outcome_verification_passed": True,
            "intentional_failure_rollback_verified": True,
            "evidence_guided_repair_verified": True,
            "lease_conflict_blocked": True,
            "attestation_verified": True,
            "unsupported_claims_zero": True,
            "false_completions_zero": True,
            "wrong_changes_zero": True,
            "evidence_refs": {
                "claim_firewall_enforced": [claim["event_id"]],
                "mutation_gate_enforced": [mutation_gate["event_id"]],
                "outcome_verification_passed": [outcome["event_id"]],
                "intentional_failure_rollback_verified": [rollback["event_id"]],
                "lease_conflict_blocked": [lease["event_id"]],
            },
        },
    )


def test_full_phase3_evidence_set_passes(tmp_path: Path):
    _seed_valid(tmp_path)
    result = evaluate_phase3_closure(tmp_path, paths=_paths())
    assert result["status"] == "pass"
    assert all(result["checks"].values())
    assert result["blockers"] == []


def test_missing_report_fails_closed(tmp_path: Path):
    _seed_valid(tmp_path)
    (tmp_path / "reports/soak.json").unlink()
    result = evaluate_phase3_closure(tmp_path, paths=_paths())
    assert result["status"] == "fail"
    assert any(item.startswith("missing_or_invalid_report:soak:missing") for item in result["blockers"])


def test_unverified_attestation_cannot_close_phase3(tmp_path: Path):
    _seed_valid(tmp_path)
    _write(
        tmp_path / "reports/attestation.json",
        {"status": "pass", "reason": "signature_not_verified", "attestation_hash": "a" * 64},
    )
    result = evaluate_phase3_closure(tmp_path, paths=_paths())
    assert result["status"] == "fail"
    assert "closure_check_failed:run_attestation" in result["blockers"]


def test_attestation_without_hash_fails(tmp_path: Path):
    _seed_valid(tmp_path)
    _write(tmp_path / "reports/attestation.json", {"status": "pass", "reason": "attestation_verified"})
    result = evaluate_phase3_closure(tmp_path, paths=_paths())
    assert result["status"] == "fail"


def test_economics_requires_canonical_schema_and_valid_ledger(tmp_path: Path):
    _seed_valid(tmp_path)
    _write(
        tmp_path / "reports/economics.json",
        {
            "status": "ok",
            "reason": "canonical_evidence_metrics_computed",
            "ledger": {"status": "fail"},
            "metrics": {"verified_success_rate": 1.0, "tokens_per_verified_success": 100.0},
        },
    )
    result = evaluate_phase3_closure(tmp_path, paths=_paths())
    assert result["status"] == "fail"
    assert "closure_check_failed:reliability_economics" in result["blockers"]


def test_soak_with_too_few_iterations_fails(tmp_path: Path):
    _seed_valid(tmp_path)
    soak = json.loads((tmp_path / "reports/soak.json").read_text())
    soak["summary"]["iterations"] = 9
    _write(tmp_path / "reports/soak.json", soak)
    result = evaluate_phase3_closure(tmp_path, paths=_paths())
    assert result["status"] == "fail"
    assert "closure_check_failed:sustained_reliability_soak" in result["blockers"]


def test_any_soak_critical_defect_fails(tmp_path: Path):
    _seed_valid(tmp_path)
    soak = json.loads((tmp_path / "reports/soak.json").read_text())
    soak["summary"]["critical_defects"]["unsupported_claim"] = 1
    _write(tmp_path / "reports/soak.json", soak)
    result = evaluate_phase3_closure(tmp_path, paths=_paths())
    assert result["status"] == "fail"


def test_soak_requires_measured_token_and_latency_drift(tmp_path: Path):
    _seed_valid(tmp_path)
    soak = json.loads((tmp_path / "reports/soak.json").read_text())
    soak["summary"]["token_drift_ratio"] = None
    soak["summary"]["latency_drift_ratio"] = None
    _write(tmp_path / "reports/soak.json", soak)
    result = evaluate_phase3_closure(tmp_path, paths=_paths())
    assert result["status"] == "fail"
    assert "closure_check_failed:sustained_reliability_soak" in result["blockers"]


def test_jev_ab_requires_canonical_modes(tmp_path: Path):
    _seed_valid(tmp_path)
    report = json.loads((tmp_path / "reports/jev_ab.json").read_text())
    report["modes"] = ["jev_off"]
    _write(tmp_path / "reports/jev_ab.json", report)
    result = evaluate_phase3_closure(tmp_path, paths=_paths())
    assert result["status"] == "fail"
    assert "closure_check_failed:jev_off_on_comparison" in result["blockers"]


def test_jev_ab_requires_minimum_repeats_even_if_report_claims_pass(tmp_path: Path):
    _seed_valid(tmp_path)
    report = json.loads((tmp_path / "reports/jev_ab.json").read_text())
    report["thresholds"]["min_repeats"] = 1
    report["summaries"]["jev_off"]["runs"] = 1
    report["summaries"]["jev_on"]["runs"] = 1
    report["observations"] = report["observations"][:2]
    _write(tmp_path / "reports/jev_ab.json", report)
    result = evaluate_phase3_closure(tmp_path, paths=_paths())
    assert result["status"] == "fail"
    assert "closure_check_failed:jev_off_on_comparison" in result["blockers"]


def test_jev_ab_failed_check_cannot_close_phase3(tmp_path: Path):
    _seed_valid(tmp_path)
    report = json.loads((tmp_path / "reports/jev_ab.json").read_text())
    report["checks"]["token_cost_bounded"] = False
    _write(tmp_path / "reports/jev_ab.json", report)
    result = evaluate_phase3_closure(tmp_path, paths=_paths())
    assert result["status"] == "fail"


def test_missing_safety_evidence_flag_fails(tmp_path: Path):
    _seed_valid(tmp_path)
    evidence = json.loads((tmp_path / "reports/evidence.json").read_text())
    evidence["lease_conflict_blocked"] = False
    _write(tmp_path / "reports/evidence.json", evidence)
    result = evaluate_phase3_closure(tmp_path, paths=_paths())
    assert result["status"] == "fail"
    assert "required_evidence_flag_not_true:lease_conflict_blocked" in result["blockers"]


def test_true_boolean_without_canonical_ref_fails_provenance(tmp_path: Path):
    _seed_valid(tmp_path)
    evidence = json.loads((tmp_path / "reports/evidence.json").read_text())
    evidence["evidence_refs"].pop("lease_conflict_blocked")
    _write(tmp_path / "reports/evidence.json", evidence)
    result = evaluate_phase3_closure(tmp_path, paths=_paths())
    assert result["status"] == "fail"
    assert "evidence_provenance_failed:canonical_evidence_refs_missing:lease_conflict_blocked" in result["blockers"]


def test_wrong_event_type_cannot_support_lease_conflict_flag(tmp_path: Path):
    _seed_valid(tmp_path)
    evidence = json.loads((tmp_path / "reports/evidence.json").read_text())
    evidence["evidence_refs"]["lease_conflict_blocked"] = evidence["evidence_refs"]["outcome_verification_passed"]
    _write(tmp_path / "reports/evidence.json", evidence)
    result = evaluate_phase3_closure(tmp_path, paths=_paths())
    assert result["status"] == "fail"
    assert "evidence_provenance_failed:canonical_evidence_ref_mismatch:lease_conflict_blocked" in result["blockers"]


def test_unsupported_claim_decision_blocks_zero_unsupported_claims(tmp_path: Path):
    _seed_valid(tmp_path)
    append_evidence_event(
        tmp_path,
        event_type="claim_decision",
        source="claim_firewall",
        status="unsupported",
        data={"claim_id": "C-BAD", "decision": "UNSUPPORTED"},
    )
    result = evaluate_phase3_closure(tmp_path, paths=_paths())
    assert result["status"] == "fail"
    assert "evidence_provenance_failed:unsupported_claim_decision_present" in result["blockers"]


def test_comparative_requires_real_provider_and_minimum_repeats(tmp_path: Path):
    _seed_valid(tmp_path)
    _write(
        tmp_path / "reports/comparative.json",
        {
            "status": "pass",
            "real_provider_execution": False,
            "provider": "provider-x",
            "model": "model-y",
            "repeats": 2,
        },
    )
    result = evaluate_phase3_closure(tmp_path, paths=_paths())
    assert result["status"] == "fail"
    assert "closure_check_failed:real_comparative_benchmark" in result["blockers"]
