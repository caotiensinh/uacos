from pathlib import Path

import pytest

from scripts.uacos_benchmark_suite import (
    load_manifest,
    summarize_suites,
    validate_manifest,
)


def test_benchmark_manifest_schema_loads():
    manifest = load_manifest(Path("evals/benchmark_suite.json"))

    assert manifest["version"] == 1
    assert manifest["suites"]
    assert manifest["pass_thresholds"]["min_task_success_rate"] == 1.0
    assert any("80-90" in note for note in manifest.get("method_notes", []))


def test_manifest_rejects_missing_suites():
    with pytest.raises(ValueError, match="suites_required"):
        validate_manifest({"version": 1, "suites": []})


def test_manifest_rejects_tiny_token_budget():
    with pytest.raises(ValueError, match="suite_max_tokens_too_low"):
        validate_manifest({
            "version": 1,
            "suites": [{"id": "bad", "tasks": ["x"], "max_tokens": 100, "max_files": 1}],
        })


def test_summarize_suites_passes_with_good_metrics():
    summary = summarize_suites([
        {
            "performance": {
                "tasks": [
                    {
                        "status": "ok",
                        "savings_percent": 60.0,
                        "full_repo_input_context_reduction_percent": 99.1,
                        "claim_classification": {"target_99_input_context_reduction_met": True},
                    },
                    {
                        "status": "ok",
                        "savings_percent": 40.0,
                        "full_repo_input_context_reduction_percent": 95.0,
                        "claim_classification": {"target_99_input_context_reduction_met": False},
                    },
                ]
            },
            "context_quality": {"pass_rate": 1.0},
        }
    ], {"min_task_success_rate": 1.0, "min_context_quality_pass_rate": 0.5, "min_average_savings_percent": 0.0})

    assert summary["status"] == "pass"
    assert summary["task_success_rate"] == 1.0
    assert summary["average_savings_percent"] == 50.0
    assert summary["average_full_repo_input_context_reduction_percent"] == 97.05
    assert summary["tasks_meeting_99_input_context_reduction"] == 1
    assert "not total AI workflow" in summary["claim_warning"]


def test_summarize_suites_fails_when_task_success_is_low():
    summary = summarize_suites([
        {
            "performance": {
                "tasks": [
                    {"status": "ok", "savings_percent": 60.0},
                    {"status": "fail", "savings_percent": 40.0},
                ]
            },
            "context_quality": {"pass_rate": 1.0},
        }
    ], {"min_task_success_rate": 1.0, "min_context_quality_pass_rate": 0.5, "min_average_savings_percent": 0.0})

    assert summary["status"] == "fail"
    assert summary["task_success_rate"] == 0.5
