import json
from pathlib import Path

from scripts.final_closure_check import evaluate_closure


def _real_comparative_pass_report() -> dict:
    return {
        "status": "pass",
        "real_provider_execution": True,
        "provider": "codex",
        "model": "test-model",
        "repeats": 3,
    }


def test_non_strict_closure_keeps_implementation_green_but_reports_missing_evidence(tmp_path: Path):
    report = evaluate_closure(tmp_path, strict_evidence=False)
    assert report["status"] == "pass"
    assert report["implementation_status"] == "pass"
    assert report["evidence_status"] == "incomplete"
    assert "real_agent_report:missing" in report["blockers"]
    assert "comparative_report:missing" in report["blockers"]


def test_strict_closure_fails_when_evidence_is_missing(tmp_path: Path):
    report = evaluate_closure(tmp_path, strict_evidence=True)
    assert report["status"] == "fail"
    assert report["evidence_status"] == "incomplete"


def test_strict_closure_rejects_incomplete_real_agent_evidence(tmp_path: Path):
    real = tmp_path / "reports" / "real-agent-e2e" / "summary.json"
    comp = tmp_path / "reports" / "comparative_ground_truth_benchmark.json"
    real.parent.mkdir(parents=True)
    comp.parent.mkdir(parents=True, exist_ok=True)
    real.write_text(json.dumps({"status": "incomplete", "executed_count": 0, "passed_count": 0}), encoding="utf-8")
    comp.write_text(json.dumps(_real_comparative_pass_report()), encoding="utf-8")

    report = evaluate_closure(tmp_path, strict_evidence=True)
    assert report["status"] == "fail"
    assert "real_agent_provider_execution_not_passed" in report["blockers"]
    assert report["checks"]["comparative_benchmark_passed"] is True


def test_strict_closure_rejects_fixture_or_offline_comparative_pass(tmp_path: Path):
    real = tmp_path / "reports" / "real-agent-e2e" / "summary.json"
    comp = tmp_path / "reports" / "comparative_ground_truth_benchmark.json"
    real.parent.mkdir(parents=True)
    comp.parent.mkdir(parents=True, exist_ok=True)
    real.write_text(json.dumps({"status": "pass", "executed_count": 1, "passed_count": 1}), encoding="utf-8")
    comp.write_text(json.dumps({"status": "pass"}), encoding="utf-8")

    report = evaluate_closure(tmp_path, strict_evidence=True)
    assert report["status"] == "fail"
    assert "real_comparative_benchmark_not_passed" in report["blockers"]
    assert report["checks"]["comparative_real_provider_execution"] is False


def test_strict_closure_rejects_real_comparative_with_too_few_repeats(tmp_path: Path):
    real = tmp_path / "reports" / "real-agent-e2e" / "summary.json"
    comp = tmp_path / "reports" / "comparative_ground_truth_benchmark.json"
    real.parent.mkdir(parents=True)
    comp.parent.mkdir(parents=True, exist_ok=True)
    real.write_text(json.dumps({"status": "pass", "executed_count": 1, "passed_count": 1}), encoding="utf-8")
    comparative = _real_comparative_pass_report()
    comparative["repeats"] = 2
    comp.write_text(json.dumps(comparative), encoding="utf-8")

    report = evaluate_closure(tmp_path, strict_evidence=True)
    assert report["status"] == "fail"
    assert report["checks"]["comparative_minimum_repeats"] is False


def test_strict_closure_passes_only_with_real_agent_and_real_comparative_pass(tmp_path: Path):
    real = tmp_path / "reports" / "real-agent-e2e" / "summary.json"
    comp = tmp_path / "reports" / "comparative_ground_truth_benchmark.json"
    real.parent.mkdir(parents=True)
    comp.parent.mkdir(parents=True, exist_ok=True)
    real.write_text(json.dumps({"status": "pass", "executed_count": 2, "passed_count": 2}), encoding="utf-8")
    comp.write_text(json.dumps(_real_comparative_pass_report()), encoding="utf-8")

    report = evaluate_closure(tmp_path, strict_evidence=True)
    assert report["status"] == "pass"
    assert report["evidence_status"] == "pass"
    assert report["blockers"] == []
