from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Protocol


ALLOWED_JUDGMENT_STATUSES = {"ok", "fallback", "unavailable", "error"}
FORBIDDEN_AUTHORITATIVE_FIELDS = {
    "pass",
    "passed",
    "verified",
    "test_pass",
    "policy_allow",
    "rollback_verified",
    "mutation_allowed",
}


@dataclass(frozen=True)
class JudgmentRequest:
    question: str
    candidates: list[dict[str, Any]]
    evidence: list[dict[str, Any]] = field(default_factory=list)
    task_id: str | None = None
    run_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class JudgmentResult:
    provider: str
    status: str
    ranking: list[str]
    scores: dict[str, float]
    rationale: dict[str, str] = field(default_factory=dict)
    fallback_used: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status not in ALLOWED_JUDGMENT_STATUSES:
            raise ValueError(f"invalid_judgment_status:{self.status}")
        if len(self.ranking) != len(set(self.ranking)):
            raise ValueError("duplicate_judgment_ranking_id")
        if any(key in FORBIDDEN_AUTHORITATIVE_FIELDS for key in self.metadata):
            raise ValueError("judgment_cannot_emit_authoritative_runtime_verdict")
        for key, value in self.scores.items():
            score = float(value)
            if score < 0.0 or score > 1.0:
                raise ValueError(f"judgment_score_out_of_range:{key}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class JudgmentProvider(Protocol):
    name: str

    def judge(self, request: JudgmentRequest) -> JudgmentResult:
        ...


def candidate_id(row: dict[str, Any], index: int) -> str:
    return str(row.get("candidate_id") or row.get("id") or row.get("name") or f"candidate-{index}")


def validate_judgment_result(request: JudgmentRequest, result: JudgmentResult) -> JudgmentResult:
    candidate_ids = {candidate_id(row, index) for index, row in enumerate(request.candidates)}
    if any(item not in candidate_ids for item in result.ranking):
        raise ValueError("judgment_ranked_unknown_candidate")
    if any(item not in candidate_ids for item in result.scores):
        raise ValueError("judgment_scored_unknown_candidate")
    return result
