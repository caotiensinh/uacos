from __future__ import annotations

from io import BytesIO
from urllib import error
import json

import pytest

from uacos.judgment.typesafe_http import TypeSafeSystemOneJevTransport


class Response:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.payload


def _payload():
    return {
        "question": "Which context is most useful?",
        "state": {"task_id": "TASK-1", "run_id": "RUN-1"},
        "choices": [
            {"id": "a", "data": {"relevance": 0.9}},
            {"id": "b", "data": {"relevance": 0.4}},
        ],
        "evidence": [{"event_id": "EV-1", "status": "PASS"}],
    }


def test_transport_posts_official_systemone_shape_and_ranks_probabilities():
    seen = {}

    def opener(req, timeout):
        seen["url"] = req.full_url
        seen["timeout"] = timeout
        seen["authorization"] = req.headers["Authorization"]
        seen["body"] = json.loads(req.data.decode("utf-8"))
        return Response(
            {
                "model": "jev-1.13.0",
                "usage": {"input_tokens": 42, "output_tokens": 0},
                "answers": {
                    "uacos_ranking": {
                        "type": "choice",
                        "choice": "b",
                        "confidence": 0.7,
                        "probabilities": {"a": 0.25, "b": 0.75},
                    }
                },
            }
        )

    transport = TypeSafeSystemOneJevTransport("secret", urlopen_fn=opener)
    result = transport(_payload(), 1.5)

    assert seen["url"] == "https://api.typesafe.ai/v1/systemone"
    assert seen["timeout"] == 1.5
    assert seen["authorization"] == "Bearer secret"
    body = seen["body"]
    assert body["model"] == "jev-latest"
    assert body["questions"]["uacos_ranking"]["type"] == "choice"
    assert set(body["questions"]["uacos_ranking"]["criteria"]) == {"a", "b"}
    assert result["ranking"] == ["b", "a"]
    assert result["scores"] == {"a": 0.25, "b": 0.75}
    assert result["metadata"]["typesafe_choice"] == "b"
    assert result["metadata"]["typesafe_model"] == "jev-1.13.0"


def test_ties_are_ranked_deterministically_by_candidate_id():
    def opener(req, timeout):
        return Response(
            {
                "answers": {
                    "uacos_ranking": {
                        "type": "choice",
                        "choice": "a",
                        "confidence": 0.0,
                        "probabilities": {"b": 0.5, "a": 0.5},
                    }
                }
            }
        )

    result = TypeSafeSystemOneJevTransport("secret", urlopen_fn=opener)(_payload(), 1)
    assert result["ranking"] == ["a", "b"]


def test_unknown_or_missing_probability_candidate_fails_closed():
    def opener(req, timeout):
        return Response(
            {
                "answers": {
                    "uacos_ranking": {
                        "type": "choice",
                        "choice": "a",
                        "confidence": 0.8,
                        "probabilities": {"a": 1.0, "c": 0.0},
                    }
                }
            }
        )

    with pytest.raises(ValueError, match="typesafe_probability_candidates_mismatch"):
        TypeSafeSystemOneJevTransport("secret", urlopen_fn=opener)(_payload(), 1)


def test_out_of_range_probability_fails_closed():
    def opener(req, timeout):
        return Response(
            {
                "answers": {
                    "uacos_ranking": {
                        "type": "choice",
                        "choice": "a",
                        "confidence": 0.8,
                        "probabilities": {"a": 1.2, "b": -0.2},
                    }
                }
            }
        )

    with pytest.raises(ValueError, match="typesafe_probability_out_of_range"):
        TypeSafeSystemOneJevTransport("secret", urlopen_fn=opener)(_payload(), 1)


def test_http_errors_do_not_leak_api_key():
    def opener(req, timeout):
        raise error.HTTPError(req.full_url, 401, "unauthorized", hdrs=None, fp=None)

    transport = TypeSafeSystemOneJevTransport("super-secret", urlopen_fn=opener)
    with pytest.raises(RuntimeError) as exc:
        transport(_payload(), 1)
    assert str(exc.value) == "typesafe_http_error:401"
    assert "super-secret" not in str(exc.value)


def test_timeout_maps_to_timeout_error_for_deterministic_fallback():
    def opener(req, timeout):
        raise TimeoutError("slow")

    with pytest.raises(TimeoutError, match="typesafe_request_timeout"):
        TypeSafeSystemOneJevTransport("secret", urlopen_fn=opener)(_payload(), 1)


def test_invalid_json_fails_closed():
    class BadResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b"not-json"

    with pytest.raises(ValueError, match="typesafe_response_invalid_json"):
        TypeSafeSystemOneJevTransport("secret", urlopen_fn=lambda req, timeout: BadResponse())(_payload(), 1)


def test_constructor_requires_api_key_and_https_endpoint():
    with pytest.raises(ValueError, match="typesafe_api_key_required"):
        TypeSafeSystemOneJevTransport("")
    with pytest.raises(ValueError, match="typesafe_endpoint_must_use_https"):
        TypeSafeSystemOneJevTransport("x", endpoint="http://example.com")


def test_requires_at_least_two_candidates():
    payload = _payload()
    payload["choices"] = [{"id": "only", "data": {}}]
    transport = TypeSafeSystemOneJevTransport("secret", urlopen_fn=lambda req, timeout: None)
    with pytest.raises(ValueError, match="jev_requires_at_least_two_candidates"):
        transport(payload, 1)
