from __future__ import annotations

import pytest

from uacos.benchmarks.soak import SoakThresholds, evaluate_sustained_reliability


def _rows(count: int = 10):
    return [
        {
            "iteration": index,
            "status": "pass",
            "total_tokens": 100 + index,
            "latency_ms": 200 + index,
        }
        for index in range(1, count + 1)
    ]


def test_clean_ten_iteration_soak_passes():
    result = evaluate_sustained_reliability(_rows())
    assert result["status"] == "pass"
    assert result["summary"]["iterations"] == 10
    assert result["summary"]["verified_success_rate"] == 1.0
    assert result["checks"]["zero_critical_defects"] is True


def test_insufficient_iterations_fail_closed():
    result = evaluate_sustained_reliability(_rows(5))
    assert result["status"] == "fail"
    assert "insufficient_iterations:5:10" in result["findings"]


def test_any_false_completion_fails_soak():
    rows = _rows()
    rows[4]["false_completion"] = True
    result = evaluate_sustained_reliability(rows)
    assert result["status"] == "fail"
    assert result["summary"]["critical_defects"]["false_completion"] == 1
    assert "critical_defect:false_completion:1" in result["findings"]


def test_failed_rollback_and_unblocked_lease_conflict_are_critical():
    rows = _rows()
    rows[1]["rollback_failed"] = True
    rows[7]["lease_conflict_unblocked"] = True
    result = evaluate_sustained_reliability(rows)
    assert result["status"] == "fail"
    assert result["summary"]["critical_defects"]["rollback_failed"] == 1
    assert result["summary"]["critical_defects"]["lease_conflict_unblocked"] == 1


def test_success_rate_threshold_is_enforced():
    rows = _rows()
    rows[-1]["status"] = "fail"
    result = evaluate_sustained_reliability(rows)
    assert result["status"] == "fail"
    assert result["summary"]["verified_success_rate"] == 0.9
    assert "verified_success_rate_below_threshold" in result["findings"]


def test_token_drift_above_threshold_fails():
    rows = _rows()
    for row in rows[:5]:
        row["total_tokens"] = 100
    for row in rows[5:]:
        row["total_tokens"] = 140
    result = evaluate_sustained_reliability(rows)
    assert result["status"] == "fail"
    assert result["summary"]["token_drift_ratio"] == 0.4
    assert "token_drift_above_threshold" in result["findings"]


def test_missing_optional_drift_measurements_are_explicitly_unavailable():
    rows = [{"iteration": index, "status": "pass"} for index in range(1, 11)]
    result = evaluate_sustained_reliability(rows)
    assert result["status"] == "pass"
    assert result["summary"]["token_drift_ratio"] is None
    assert result["summary"]["latency_drift_ratio"] is None
    assert "token_drift_ratio" in result["unavailable_metrics"]
    assert "latency_drift_ratio" in result["unavailable_metrics"]


def test_duplicate_iteration_fails():
    rows = _rows()
    rows[-1]["iteration"] = rows[-2]["iteration"]
    result = evaluate_sustained_reliability(rows)
    assert result["status"] == "fail"
    assert any(item.startswith("duplicate_iteration:") for item in result["findings"])


def test_threshold_validation():
    with pytest.raises(ValueError, match="min_iterations_must_be_positive"):
        evaluate_sustained_reliability(_rows(), thresholds=SoakThresholds(min_iterations=0))
    with pytest.raises(ValueError, match="min_verified_success_rate_out_of_range"):
        evaluate_sustained_reliability(_rows(), thresholds=SoakThresholds(min_verified_success_rate=1.1))
