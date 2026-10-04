from __future__ import annotations

from uacos.judgment.jev import JevJudgmentProvider
from uacos.judgment.protocol import JudgmentRequest


def _request() -> JudgmentRequest:
    return JudgmentRequest(
        question="which context is most useful?",
        task_id="TASK-1",
        run_id="RUN-1",
        candidates=[
            {"candidate_id": "a", "relevance": 0.9, "evidence_value": 0.9},
            {"candidate_id": "b", "relevance": 0.3, "evidence_value": 0.2},
        ],
        evidence=[{"event_id": "EV-1", "status": "PASS"}],
        metadata={"purpose": "context_ranking"},
    )


def test_jev_adapter_returns_bounded_advisory_ranking_and_passes_timeout():
    seen = {}

    def transport(payload, timeout_seconds):
        seen["payload"] = payload
        seen["timeout"] = timeout_seconds
        return {
            "ranking": ["b", "a"],
            "scores": {"a": 0.4, "b": 0.8},
            "rationale": {"b": "bounded choice"},
            "metadata": {"model": "jev-test"},
        }

    result = JevJudgmentProvider(transport, timeout_seconds=1.25).judge(_request())

    assert result.status == "ok"
    assert result.provider == "jev"
    assert result.ranking == ["b", "a"]
    assert result.fallback_used is False
    assert result.metadata["advisory_only"] is True
    assert result.metadata["deterministic"] is False
    assert seen["timeout"] == 1.25
    assert seen["payload"]["state"]["task_id"] == "TASK-1"
    assert seen["payload"]["choices"][0]["id"] == "a"


def test_timeout_falls_back_deterministically():
    def transport(payload, timeout_seconds):
        raise TimeoutError("deadline")

    result = JevJudgmentProvider(transport).judge(_request())

    assert result.status == "fallback"
    assert result.provider == "heuristic"
    assert result.fallback_used is True
    assert result.metadata["jev_fallback_reason"] == "timeout"
    assert result.metadata["primary_provider"] == "jev"


def test_transport_exception_falls_back_without_exposing_provider_authority():
    def transport(payload, timeout_seconds):
        raise RuntimeError("provider down")

    result = JevJudgmentProvider(transport).judge(_request())

    assert result.status == "fallback"
    assert result.metadata["jev_fallback_reason"] == "transport_error:RuntimeError"
    assert "verified" not in result.metadata
    assert "policy_allow" not in result.metadata


def test_authoritative_top_level_field_is_rejected_into_fallback():
    def transport(payload, timeout_seconds):
        return {
            "ranking": ["a", "b"],
            "scores": {"a": 0.8, "b": 0.2},
            "verified": True,
        }

    result = JevJudgmentProvider(transport).judge(_request())

    assert result.status == "fallback"
    assert result.metadata["jev_fallback_reason"] == "authoritative_field_rejected"


def test_authoritative_metadata_field_is_rejected_into_fallback():
    def transport(payload, timeout_seconds):
        return {
            "ranking": ["a", "b"],
            "scores": {"a": 0.8, "b": 0.2},
            "metadata": {"rollback_verified": True},
        }

    result = JevJudgmentProvider(transport).judge(_request())

    assert result.status == "fallback"
    assert result.metadata["jev_fallback_reason"] == "authoritative_field_rejected"


def test_unknown_candidate_from_jev_falls_back():
    def transport(payload, timeout_seconds):
        return {"ranking": ["unknown"], "scores": {"unknown": 0.9}}

    result = JevJudgmentProvider(transport).judge(_request())

    assert result.status == "fallback"
    assert result.metadata["jev_fallback_reason"] == "invalid_response_schema"


def test_out_of_range_score_from_jev_falls_back():
    def transport(payload, timeout_seconds):
        return {"ranking": ["a", "b"], "scores": {"a": 1.5, "b": 0.2}}

    result = JevJudgmentProvider(transport).judge(_request())

    assert result.status == "fallback"
    assert result.metadata["jev_fallback_reason"] == "invalid_response_schema"


def test_non_mapping_response_falls_back():
    def transport(payload, timeout_seconds):
        return ["a", "b"]

    result = JevJudgmentProvider(transport).judge(_request())

    assert result.status == "fallback"
    assert result.metadata["jev_fallback_reason"] == "invalid_response_type"


def test_request_input_is_not_mutated():
    request = _request()
    before = request.to_dict()

    def transport(payload, timeout_seconds):
        payload["choices"][0]["data"]["relevance"] = 0.0
        return {"ranking": ["a", "b"], "scores": {"a": 0.7, "b": 0.3}}

    JevJudgmentProvider(transport).judge(request)

    assert request.to_dict() == before


def test_timeout_must_be_positive():
    try:
        JevJudgmentProvider(lambda payload, timeout: {}, timeout_seconds=0)
    except ValueError as exc:
        assert str(exc) == "jev_timeout_must_be_positive"
    else:
        raise AssertionError("expected timeout validation")
