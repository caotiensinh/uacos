from __future__ import annotations

from typing import Any

from uacos.judgment.protocol import (
    JudgmentRequest,
    JudgmentResult,
    candidate_id,
    validate_judgment_result,
)


def _bounded(value: Any, default: float = 0.0) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        score = default
    return max(0.0, min(1.0, score))


class HeuristicJudgmentProvider:
    """Deterministic advisory fallback; never emits an authoritative runtime verdict."""

    name = "heuristic"

    def judge(self, request: JudgmentRequest) -> JudgmentResult:
        ranked_rows = []
        rationale: dict[str, str] = {}
        scores: dict[str, float] = {}

        for index, row in enumerate(request.candidates):
            cid = candidate_id(row, index)
            relevance = _bounded(row.get("relevance", row.get("score", 0.0)))
            evidence_value = _bounded(row.get("evidence_value", relevance))
            confidence = _bounded(row.get("confidence", 0.5), 0.5)
            deterministic_bonus = 0.05 if bool(row.get("deterministic_evidence", False)) else 0.0
            score = min(1.0, (0.45 * evidence_value) + (0.40 * relevance) + (0.15 * confidence) + deterministic_bonus)
            score = round(score, 6)
            scores[cid] = score
            rationale[cid] = (
                f"evidence_value={evidence_value:.3f};relevance={relevance:.3f};"
                f"confidence={confidence:.3f};deterministic_bonus={deterministic_bonus:.3f}"
            )
            ranked_rows.append((cid, score))

        ranked_rows.sort(key=lambda item: (-item[1], item[0]))
        result = JudgmentResult(
            provider=self.name,
            status="fallback",
            ranking=[cid for cid, _ in ranked_rows],
            scores=scores,
            rationale=rationale,
            fallback_used=True,
            metadata={"advisory_only": True, "deterministic": True},
        )
        return validate_judgment_result(request, result)
