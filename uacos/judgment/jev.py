from __future__ import annotations

from typing import Any, Callable

from uacos.judgment.heuristic import HeuristicJudgmentProvider
from uacos.judgment.protocol import (
    FORBIDDEN_AUTHORITATIVE_FIELDS,
    JudgmentProvider,
    JudgmentRequest,
    JudgmentResult,
    candidate_id,
    validate_judgment_result,
)


JevTransport = Callable[[dict[str, Any], float], dict[str, Any]]


def _payload(request: JudgmentRequest) -> dict[str, Any]:
    return {
        "question": request.question,
        "state": {
            "task_id": request.task_id,
            "run_id": request.run_id,
            "metadata": dict(request.metadata),
        },
        "choices": [
            {
                "id": candidate_id(row, index),
                "data": dict(row),
            }
            for index, row in enumerate(request.candidates)
        ],
        "evidence": [dict(row) for row in request.evidence],
    }


def _forbidden_raw_keys(raw: dict[str, Any]) -> set[str]:
    found = set(raw).intersection(FORBIDDEN_AUTHORITATIVE_FIELDS)
    metadata = raw.get("metadata")
    if isinstance(metadata, dict):
        found.update(set(metadata).intersection(FORBIDDEN_AUTHORITATIVE_FIELDS))
    return found


class JevJudgmentProvider:
    """Bounded advisory Jev adapter with deterministic fallback.

    Transport is injected so the runtime does not hard-code a Jev cloud endpoint or
    SDK. The transport contract receives a structured payload plus a timeout. Jev
    output can rank/score supplied candidates only and can never emit authoritative
    runtime verdicts.
    """

    name = "jev"

    def __init__(
        self,
        transport: JevTransport,
        *,
        timeout_seconds: float = 2.0,
        fallback: JudgmentProvider | None = None,
    ) -> None:
        timeout_seconds = float(timeout_seconds)
        if timeout_seconds <= 0:
            raise ValueError("jev_timeout_must_be_positive")
        self.transport = transport
        self.timeout_seconds = timeout_seconds
        self.fallback = fallback or HeuristicJudgmentProvider()

    def _fallback(self, request: JudgmentRequest, reason: str) -> JudgmentResult:
        base = self.fallback.judge(request)
        metadata = dict(base.metadata)
        metadata.update(
            {
                "advisory_only": True,
                "jev_fallback_reason": reason,
                "primary_provider": self.name,
            }
        )
        result = JudgmentResult(
            provider=base.provider,
            status="fallback",
            ranking=list(base.ranking),
            scores=dict(base.scores),
            rationale=dict(base.rationale),
            fallback_used=True,
            metadata=metadata,
        )
        return validate_judgment_result(request, result)

    def judge(self, request: JudgmentRequest) -> JudgmentResult:
        payload = _payload(request)
        try:
            raw = self.transport(payload, self.timeout_seconds)
        except TimeoutError:
            return self._fallback(request, "timeout")
        except Exception as exc:
            return self._fallback(request, f"transport_error:{type(exc).__name__}")

        if not isinstance(raw, dict):
            return self._fallback(request, "invalid_response_type")
        if _forbidden_raw_keys(raw):
            return self._fallback(request, "authoritative_field_rejected")

        try:
            ranking = [str(item) for item in raw.get("ranking", [])]
            raw_scores = raw.get("scores", {})
            if not isinstance(raw_scores, dict):
                raise ValueError("jev_scores_must_be_mapping")
            scores = {str(key): float(value) for key, value in raw_scores.items()}
            raw_rationale = raw.get("rationale", {})
            if not isinstance(raw_rationale, dict):
                raise ValueError("jev_rationale_must_be_mapping")
            rationale = {str(key): str(value) for key, value in raw_rationale.items()}
            metadata = dict(raw.get("metadata") or {})
            metadata.update({"advisory_only": True, "deterministic": False})
            result = JudgmentResult(
                provider=self.name,
                status="ok",
                ranking=ranking,
                scores=scores,
                rationale=rationale,
                fallback_used=False,
                metadata=metadata,
            )
            return validate_judgment_result(request, result)
        except (TypeError, ValueError):
            return self._fallback(request, "invalid_response_schema")
