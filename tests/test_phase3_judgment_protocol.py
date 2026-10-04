from __future__ import annotations

import pytest

from uacos.judgment.heuristic import HeuristicJudgmentProvider
from uacos.judgment.protocol import JudgmentRequest, JudgmentResult, validate_judgment_result


def _request():
    return JudgmentRequest(
        question="rank context candidates",
        candidates=[
            {
                "candidate_id": "high",
                "relevance": 0.9,
                "evidence_value": 0.9,
                "confidence": 0.8,
                "deterministic_evidence": True,
            },
            {
                "candidate_id": "low",
                "relevance": 0.2,
                "evidence_value": 0.1,
                "confidence": 0.4,
            },
        ],
        evidence=[{"event_id": "EV-1", "status": "pass"}],
        task_id="task-1",
        run_id="run-1",
    )


def test_heuristic_provider_is_deterministic_and_advisory_only():
    provider = HeuristicJudgmentProvider()
    first = provider.judge(_request())
    second = provider.judge(_request())

    assert first == second
    assert first.provider == "heuristic"
    assert first.status == "fallback"
    assert first.fallback_used is True
    assert first.ranking == ["high", "low"]
    assert first.metadata == {"advisory_only": True, "deterministic": True}


def test_deterministic_evidence_bonus_never_creates_authoritative_verdict():
    result = HeuristicJudgmentProvider().judge(_request())
    assert result.scores["high"] > result.scores["low"]
    assert "verified" not in result.metadata
    assert "pass" not in result.metadata


def test_result_rejects_authoritative_runtime_fields():
    with pytest.raises(ValueError, match="authoritative_runtime_verdict"):
        JudgmentResult(
            provider="bad",
            status="ok",
            ranking=["high"],
            scores={"high": 0.9},
            metadata={"verified": True},
        )


def test_result_rejects_out_of_range_scores():
    with pytest.raises(ValueError, match="score_out_of_range"):
        JudgmentResult(
            provider="bad",
            status="ok",
            ranking=["high"],
            scores={"high": 1.1},
        )


def test_result_rejects_duplicate_ranking_ids():
    with pytest.raises(ValueError, match="duplicate_judgment_ranking_id"):
        JudgmentResult(
            provider="bad",
            status="ok",
            ranking=["high", "high"],
            scores={"high": 0.9},
        )


def test_validation_rejects_unknown_candidate():
    request = _request()
    result = JudgmentResult(
        provider="bad",
        status="ok",
        ranking=["missing"],
        scores={"missing": 0.5},
    )
    with pytest.raises(ValueError, match="unknown_candidate"):
        validate_judgment_result(request, result)


def test_tie_order_is_stable_by_candidate_id():
    request = JudgmentRequest(
        question="stable tie",
        candidates=[
            {"candidate_id": "b", "relevance": 0.5, "evidence_value": 0.5, "confidence": 0.5},
            {"candidate_id": "a", "relevance": 0.5, "evidence_value": 0.5, "confidence": 0.5},
        ],
    )
    result = HeuristicJudgmentProvider().judge(request)
    assert result.ranking == ["a", "b"]


def test_provider_does_not_mutate_request_candidates():
    request = _request()
    before = [dict(row) for row in request.candidates]
    HeuristicJudgmentProvider().judge(request)
    assert request.candidates == before
