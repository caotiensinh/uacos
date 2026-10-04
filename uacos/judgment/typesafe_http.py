from __future__ import annotations

from typing import Any, Callable
from urllib import error, request
import json
import socket


DEFAULT_TYPESAFE_ENDPOINT = "https://api.typesafe.ai/v1/systemone"
DEFAULT_TYPESAFE_MODEL = "jev-latest"
QUESTION_ID = "uacos_ranking"


UrlopenFn = Callable[..., Any]


def _candidate_map(payload: dict[str, Any]) -> dict[str, Any]:
    choices = payload.get("choices")
    if not isinstance(choices, list) or len(choices) < 2:
        raise ValueError("jev_requires_at_least_two_candidates")
    criteria: dict[str, Any] = {}
    for row in choices:
        if not isinstance(row, dict):
            raise ValueError("jev_choice_must_be_mapping")
        candidate_id = str(row.get("id") or "").strip()
        if not candidate_id:
            raise ValueError("jev_candidate_id_required")
        if candidate_id in criteria:
            raise ValueError("jev_candidate_id_duplicate")
        criteria[candidate_id] = row.get("data")
    return criteria


def _transport_request(payload: dict[str, Any], model: str) -> dict[str, Any]:
    criteria = _candidate_map(payload)
    state = {
        "question": payload.get("question"),
        "state": payload.get("state"),
        "evidence": payload.get("evidence"),
    }
    return {
        "state": state,
        "model": model,
        "questions": {
            QUESTION_ID: {
                "type": "choice",
                "instructions": (
                    "Choose the candidate that best answers the requested UACOS advisory judgment. "
                    "Use only the supplied state and evidence. This is ranking advice only; do not "
                    "decide test PASS, policy approval, mutation permission, rollback verification, or DONE."
                ),
                "criteria": criteria,
            }
        },
    }


def _parse_response(raw: dict[str, Any], candidate_ids: list[str]) -> dict[str, Any]:
    answers = raw.get("answers")
    if not isinstance(answers, dict):
        raise ValueError("typesafe_answers_missing")
    answer = answers.get(QUESTION_ID)
    if not isinstance(answer, dict):
        raise ValueError("typesafe_choice_answer_missing")
    if str(answer.get("type") or "") != "choice":
        raise ValueError("typesafe_choice_answer_type_invalid")

    probabilities = answer.get("probabilities")
    if not isinstance(probabilities, dict):
        raise ValueError("typesafe_probabilities_missing")
    expected = set(candidate_ids)
    returned = {str(key) for key in probabilities}
    if returned != expected:
        raise ValueError("typesafe_probability_candidates_mismatch")

    scores: dict[str, float] = {}
    for candidate_id in candidate_ids:
        value = float(probabilities[candidate_id])
        if value < 0.0 or value > 1.0:
            raise ValueError("typesafe_probability_out_of_range")
        scores[candidate_id] = value

    ranking = sorted(candidate_ids, key=lambda item: (-scores[item], item))
    choice = str(answer.get("choice") or "").strip()
    if choice not in expected:
        raise ValueError("typesafe_choice_unknown_candidate")
    confidence = float(answer.get("confidence"))
    if confidence < 0.0 or confidence > 1.0:
        raise ValueError("typesafe_confidence_out_of_range")

    rationale = {
        candidate_id: (
            f"TypeSafe Jev probability={scores[candidate_id]:.6f}; "
            f"selected={candidate_id == choice}; confidence={confidence:.6f}"
        )
        for candidate_id in candidate_ids
    }
    metadata = {
        "typesafe_model": raw.get("model"),
        "typesafe_usage": raw.get("usage"),
        "typesafe_choice": choice,
        "typesafe_confidence": confidence,
    }
    return {
        "ranking": ranking,
        "scores": scores,
        "rationale": rationale,
        "metadata": metadata,
    }


class TypeSafeSystemOneJevTransport:
    """HTTP transport for TypeSafe System One / Jev using only the stdlib.

    The API key is supplied by the caller and is never included in returned metadata
    or exception messages. The transport converts UACOS candidates into one TypeSafe
    Choice question and converts Jev probabilities into advisory ranking scores.
    """

    def __init__(
        self,
        api_key: str,
        *,
        model: str = DEFAULT_TYPESAFE_MODEL,
        endpoint: str = DEFAULT_TYPESAFE_ENDPOINT,
        urlopen_fn: UrlopenFn | None = None,
    ) -> None:
        self.api_key = str(api_key or "").strip()
        if not self.api_key:
            raise ValueError("typesafe_api_key_required")
        self.model = str(model or "").strip()
        if not self.model:
            raise ValueError("typesafe_model_required")
        self.endpoint = str(endpoint or "").strip()
        if not self.endpoint.startswith("https://"):
            raise ValueError("typesafe_endpoint_must_use_https")
        self.urlopen_fn = urlopen_fn or request.urlopen

    def __call__(self, payload: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
        timeout = float(timeout_seconds)
        if timeout <= 0:
            raise ValueError("typesafe_timeout_must_be_positive")
        body = _transport_request(payload, self.model)
        encoded = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        req = request.Request(
            self.endpoint,
            data=encoded,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "uacos-phase3-jev/1",
            },
        )
        try:
            response = self.urlopen_fn(req, timeout=timeout)
            with response:
                raw_bytes = response.read()
        except (TimeoutError, socket.timeout) as exc:
            raise TimeoutError("typesafe_request_timeout") from exc
        except error.HTTPError as exc:
            raise RuntimeError(f"typesafe_http_error:{exc.code}") from exc
        except error.URLError as exc:
            if isinstance(getattr(exc, "reason", None), (TimeoutError, socket.timeout)):
                raise TimeoutError("typesafe_request_timeout") from exc
            raise RuntimeError("typesafe_transport_unavailable") from exc

        try:
            raw = json.loads(raw_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("typesafe_response_invalid_json") from exc
        if not isinstance(raw, dict):
            raise ValueError("typesafe_response_must_be_mapping")
        candidate_ids = list(_candidate_map(payload).keys())
        return _parse_response(raw, candidate_ids)
