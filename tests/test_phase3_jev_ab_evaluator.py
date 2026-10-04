from __future__ import annotations

import pytest

from uacos.benchmarks.jev_ab import evaluate_jev_ab


def _rows():
    rows = []
    for repeat in (1, 2, 3):
        rows.append({
            "task_id": "TASK-1",
            "mode": "jev_off",
            "repeat": repeat,
            "provider": "provider-a",
            "model": "model-a",
            "verified_status": "pass",
            "total_tokens": 100,
            "latency_ms": 100,
            "ranking_quality": 0.7,
            "fallback_used": False,
        })
        rows.append({
            "task_id": "TASK-1",
            "mode": "jev_on",
            "repeat": repeat,
            "provider": "provider-a",
            "model": "model-a",
            "verified_status": "pass",
            "total_tokens": 105,
            "latency_ms": 120,
            "ranking_quality": 0.8,
            "fallback_used": False,
        })
    return rows


def test_clean_jev_ab_passes():
    result = evaluate_jev_ab(_rows())
    assert result["status"] == "pass"
    assert result["checks"]["verified_success_not_regressed"] is True
    assert result["checks"]["ranking_quality_not_regressed"] is True
    assert result["deltas"]["token_delta_ratio"] == 0.05
    assert result["deltas"]["latency_delta_ratio"] == 0.2


def test_provider_model_mismatch_fails():
    rows = _rows()
    rows[-1]["model"] = "model-b"
    result = evaluate_jev_ab(rows)
    assert result["status"] == "fail"
    assert "provider_or_model_mismatch:TASK-1" in result["findings"]


def test_insufficient_repeats_fails_closed():
    result = evaluate_jev_ab(_rows()[:4])
    assert result["status"] == "fail"
    assert "insufficient_repeats:TASK-1:jev_off:2" in result["findings"]
    assert "insufficient_repeats:TASK-1:jev_on:2" in result["findings"]


def test_verified_success_regression_fails():
    rows = _rows()
    rows[-1]["verified_status"] = "fail"
    result = evaluate_jev_ab(rows)
    assert result["status"] == "fail"
    assert "verified_success_regressed" in result["findings"]


def test_token_cost_increase_above_threshold_fails():
    rows = _rows()
    for row in rows:
        if row["mode"] == "jev_on":
            row["total_tokens"] = 150
    result = evaluate_jev_ab(rows)
    assert result["status"] == "fail"
    assert "token_cost_increase_above_threshold" in result["findings"]


def test_latency_increase_above_threshold_fails():
    rows = _rows()
    for row in rows:
        if row["mode"] == "jev_on":
            row["latency_ms"] = 200
    result = evaluate_jev_ab(rows)
    assert result["status"] == "fail"
    assert "latency_increase_above_threshold" in result["findings"]


def test_ranking_quality_regression_fails():
    rows = _rows()
    for row in rows:
        if row["mode"] == "jev_on":
            row["ranking_quality"] = 0.6
    result = evaluate_jev_ab(rows)
    assert result["status"] == "fail"
    assert "ranking_quality_regressed" in result["findings"]


def test_missing_cost_measurements_fail_closed():
    rows = _rows()
    for row in rows:
        row.pop("total_tokens")
    result = evaluate_jev_ab(rows)
    assert result["status"] == "fail"
    assert "token_cost_unavailable" in result["findings"]


def test_duplicate_repeat_fails():
    rows = _rows()
    rows.append(dict(rows[0]))
    result = evaluate_jev_ab(rows)
    assert result["status"] == "fail"
    assert "duplicate_repeat:TASK-1:jev_off:1" in result["findings"]


def test_threshold_validation():
    with pytest.raises(ValueError, match="min_repeats_must_be_positive"):
        evaluate_jev_ab(_rows(), min_repeats=0)
    with pytest.raises(ValueError, match="increase_threshold_must_be_nonnegative"):
        evaluate_jev_ab(_rows(), max_token_increase_ratio=-0.1)
