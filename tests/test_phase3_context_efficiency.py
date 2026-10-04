from __future__ import annotations

from uacos.context.efficiency import admit_context_candidates, compare_context_efficiency


def test_admission_prefers_higher_evidence_value_per_token():
    result = admit_context_candidates(
        [
            {"candidate_id": "large-low", "relevance": 0.6, "evidence_value": 0.5, "token_cost": 900},
            {"candidate_id": "small-high", "relevance": 0.9, "evidence_value": 1.0, "token_cost": 300},
            {"candidate_id": "small-medium", "relevance": 0.8, "evidence_value": 0.7, "token_cost": 300},
        ],
        max_tokens=600,
    )

    assert result["status"] == "ok"
    assert result["selected_ids"] == ["small-high", "small-medium"]
    assert result["selected_tokens"] == 600
    assert result["token_savings_vs_all_unique"] == 900


def test_mandatory_context_fails_closed_when_it_cannot_fit():
    result = admit_context_candidates(
        [{"candidate_id": "contract", "relevance": 1.0, "evidence_value": 1.0, "token_cost": 501, "mandatory": True}],
        max_tokens=500,
    )

    assert result["status"] == "blocked"
    assert result["reason"] == "mandatory_context_exceeds_budget"
    assert result["selected"] == []


def test_duplicate_content_is_charged_once_and_reported():
    result = admit_context_candidates(
        [
            {"candidate_id": "slice-a", "relevance": 0.9, "evidence_value": 0.9, "token_cost": 200, "content_hash": "same"},
            {"candidate_id": "slice-b", "relevance": 0.9, "evidence_value": 0.9, "token_cost": 200, "content_hash": "same"},
        ],
        max_tokens=500,
    )

    assert result["status"] == "ok"
    assert result["unique_candidate_count"] == 1
    assert result["duplicate_candidate_count"] == 1
    assert result["selected_tokens"] == 200
    assert result["duplicate_tokens_avoided"] == 200


def test_irrelevant_context_is_measured_in_tokens_not_file_count():
    result = admit_context_candidates(
        [
            {"candidate_id": "useful", "relevance": 1.0, "evidence_value": 0.9, "token_cost": 100},
            {"candidate_id": "weak", "relevance": 0.1, "evidence_value": 0.9, "token_cost": 300},
        ],
        max_tokens=400,
        irrelevant_threshold=0.25,
    )

    assert result["selected_tokens"] == 400
    assert result["irrelevant_context_tokens"] == 300
    assert result["irrelevant_context_ratio"] == 0.75


def test_mandatory_low_relevance_context_is_not_counted_as_irrelevant_waste():
    result = admit_context_candidates(
        [{"candidate_id": "required-contract", "relevance": 0.1, "evidence_value": 1.0, "token_cost": 200, "mandatory": True}],
        max_tokens=200,
    )

    assert result["selected_tokens"] == 200
    assert result["irrelevant_context_tokens"] == 0


def test_replay_order_is_deterministic_for_equal_density():
    candidates = [
        {"candidate_id": "b", "relevance": 0.8, "evidence_value": 0.8, "token_cost": 200},
        {"candidate_id": "a", "relevance": 0.8, "evidence_value": 0.8, "token_cost": 200},
    ]
    first = admit_context_candidates(candidates, max_tokens=200)
    second = admit_context_candidates(list(reversed(candidates)), max_tokens=200)

    assert first["selected_ids"] == ["a"]
    assert second["selected_ids"] == ["a"]


def test_invalid_candidate_metrics_fail_instead_of_being_silently_clamped():
    try:
        admit_context_candidates(
            [{"candidate_id": "bad", "relevance": 1.2, "evidence_value": 0.5, "token_cost": 10}],
            max_tokens=100,
        )
    except ValueError as exc:
        assert str(exc) == "relevance_must_be_between_0_and_1"
    else:
        raise AssertionError("invalid relevance must fail")


def test_efficiency_comparison_reports_economics_without_claiming_success():
    comparison = compare_context_efficiency(
        {"selected_tokens": 1000, "irrelevant_context_tokens": 400, "weighted_relevance": 0.5, "utility_capture_ratio": 0.8},
        {"selected_tokens": 700, "irrelevant_context_tokens": 100, "weighted_relevance": 0.8, "utility_capture_ratio": 0.75},
    )

    assert comparison["token_reduction"] == 300
    assert comparison["irrelevant_token_reduction"] == 300
    assert comparison["after_weighted_relevance"] == 0.8
    assert "verified_success" not in comparison
