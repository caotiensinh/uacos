from scripts.uacos_performance_benchmark import classify_input_context_reduction, summarize_report


def test_claim_classifier_marks_99_as_input_context_only():
    result = classify_input_context_reduction(99.1)

    assert result["tier"] == "research_target_met_input_context_only"
    assert result["target_99_input_context_reduction_met"] is True
    assert "not total AI workflow token savings" in result["warning"]


def test_claim_classifier_keeps_95_below_99():
    result = classify_input_context_reduction(95.0)

    assert result["tier"] == "strong_input_context_reduction"
    assert result["target_99_input_context_reduction_met"] is False


def test_claim_classifier_blocks_weak_marketing_claims():
    result = classify_input_context_reduction(42.0)

    assert result["tier"] == "needs_better_context_selection_or_task_scope"
    assert "Do not use" in result["public_claim_guidance"]


def test_summary_preserves_new_token_metrics(tmp_path):
    report = {
        "status": "pass",
        "repo": "/repo",
        "summary": {
            "task_local_savings_percent": 50.0,
            "average_full_repo_input_context_reduction_percent": 99.2,
            "tasks_meeting_99_input_context_reduction": 2,
        },
        "tasks": [{"status": "ok"}, {"status": "ok"}],
        "cache_session_probe": {"status": "skipped"},
    }

    summary = summarize_report(report, tmp_path / "report.json")

    assert summary["status"] == "pass"
    assert summary["summary"]["average_full_repo_input_context_reduction_percent"] == 99.2
    assert summary["summary"]["tasks_meeting_99_input_context_reduction"] == 2
