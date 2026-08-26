from pathlib import Path

import pytest

from scripts.uacos_benchmark_suite import (
    load_manifest,
    run_suite,
    summarize_suites,
    validate_manifest,
)


def test_benchmark_manifest_schema_loads():
    manifest = load_manifest(Path("evals/benchmark_suite.json"))

    assert manifest["version"] == 1
    assert manifest["suites"]
    assert manifest["pass_thresholds"]["min_task_success_rate"] == 1.0
    assert any("80-90" in note for note in manifest.get("method_notes", []))


def test_multi_repo_example_manifest_schema_loads():
    manifest = load_manifest(Path("evals/multi_repo_benchmark.example.json"))

    assert manifest["version"] == 1
    assert len(manifest["suites"]) >= 5
    assert any(suite["repo_label"] == "Bear Detector" for suite in manifest["suites"])
    assert any(suite.get("skip_if_missing") for suite in manifest["suites"])


def test_manifest_rejects_missing_suites():
    with pytest.raises(ValueError, match="suites_required"):
        validate_manifest({"version": 1, "suites": []})


def test_manifest_rejects_tiny_token_budget():
    with pytest.raises(ValueError, match="suite_max_tokens_too_low"):
        validate_manifest({
            "version": 1,
            "suites": [{"id": "bad", "tasks": ["x"], "max_tokens": 100, "max_files": 1}],
        })


def test_manifest_rejects_repo_and_repo_path_together():
    with pytest.raises(ValueError, match="suite_repo_or_repo_path_not_both"):
        validate_manifest({
            "version": 1,
            "suites": [{"id": "bad", "tasks": ["x"], "max_tokens": 1000, "max_files": 1, "repo": ".", "repo_path": "../x"}],
        })


def test_optional_missing_repo_suite_is_skipped(tmp_path):
    suite = {
        "id": "missing_optional",
        "repo_label": "Missing Optional",
        "repo_path": "../does-not-exist",
        "required": False,
        "skip_if_missing": True,
        "tasks": ["x"],
        "max_tokens": 1000,
        "max_files": 1,
    }

    result = run_suite(tmp_path, suite)

    assert result["status"] == "skipped"
    assert result["reason"] == "optional_repo_missing"
    assert result["required"] is False


def test_required_missing_repo_suite_fails(tmp_path):
    suite = {
        "id": "missing_required",
        "repo_label": "Missing Required",
        "repo_path": "../does-not-exist",
        "required": True,
        "tasks": ["x"],
        "max_tokens": 1000,
        "max_files": 1,
    }

    result = run_suite(tmp_path, suite)

    assert result["status"] == "fail"
    assert result["reason"] == "required_repo_missing"
    assert result["required"] is True


def test_summarize_suites_passes_with_good_metrics():
    summary = summarize_suites([
        {
            "status": "pass",
            "repo_label": "Repo A",
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
        },
        {
            "status": "skipped",
            "id": "missing_optional",
            "repo_label": "Missing Optional",
            "reason": "optional_repo_missing",
            "performance": {"tasks": []},
            "context_quality": {"pass_rate": 0.0},
        },
    ], {"min_task_success_rate": 1.0, "min_context_quality_pass_rate": 0.5, "min_average_savings_percent": 0.0, "min_benchmarked_suite_count": 1})

    assert summary["status"] == "pass"
    assert summary["task_success_rate"] == 1.0
    assert summary["average_savings_percent"] == 50.0
    assert summary["average_full_repo_input_context_reduction_percent"] == 97.05
    assert summary["tasks_meeting_99_input_context_reduction"] == 1
    assert summary["benchmarked_suite_count"] == 1
    assert summary["skipped_suite_count"] == 1
    assert summary["benchmarked_repos"] == ["Repo A"]
    assert summary["skipped_repos"][0]["reason"] == "optional_repo_missing"
    assert "not total AI workflow" in summary["claim_warning"]


def test_summarize_suites_fails_when_task_success_is_low():
    summary = summarize_suites([
        {
            "status": "pass",
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


def test_summarize_suites_fails_without_minimum_benchmarked_coverage():
    summary = summarize_suites([
        {
            "status": "skipped",
            "id": "missing_optional",
            "repo_label": "Missing Optional",
            "reason": "optional_repo_missing",
            "performance": {"tasks": []},
            "context_quality": {"pass_rate": 0.0},
        }
    ], {"min_task_success_rate": 0.0, "min_context_quality_pass_rate": 0.0, "min_average_savings_percent": 0.0, "min_benchmarked_suite_count": 1})

    assert summary["status"] == "fail"
    assert summary["benchmarked_suite_count"] == 0
