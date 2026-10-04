from __future__ import annotations

from typing import Any


def _bounded01(value: Any, name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name}_must_be_number") from exc
    if result < 0.0 or result > 1.0:
        raise ValueError(f"{name}_must_be_between_0_and_1")
    return result


def _nonnegative_int(value: Any, name: str) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name}_must_be_integer") from exc
    if result < 0:
        raise ValueError(f"{name}_must_be_nonnegative")
    return result


def _normalized_candidate(row: dict[str, Any], index: int) -> dict[str, Any]:
    candidate_id = str(row.get("candidate_id") or row.get("id") or row.get("file") or f"candidate-{index}")
    relevance = _bounded01(row.get("relevance", 0.0), "relevance")
    evidence_value = _bounded01(row.get("evidence_value", relevance), "evidence_value")
    reuse_probability = _bounded01(row.get("reuse_probability", 0.0), "reuse_probability")
    token_cost = _nonnegative_int(row.get("token_cost", 0), "token_cost")
    mandatory = bool(row.get("mandatory", False))
    content_hash = str(row.get("content_hash") or "") or None

    # Value is intentionally deterministic and bounded. Evidence value dominates,
    # relevance is next, and reuse is a small tie-breaker / economics bonus.
    utility = (0.50 * evidence_value) + (0.40 * relevance) + (0.10 * reuse_probability)
    density = utility * 1000.0 / max(1, token_cost)
    normalized = dict(row)
    normalized.update(
        {
            "candidate_id": candidate_id,
            "relevance": relevance,
            "evidence_value": evidence_value,
            "reuse_probability": reuse_probability,
            "token_cost": token_cost,
            "mandatory": mandatory,
            "content_hash": content_hash,
            "utility": round(utility, 6),
            "value_per_1k_tokens": round(density, 6),
        }
    )
    return normalized


def admit_context_candidates(
    candidates: list[dict[str, Any]],
    *,
    max_tokens: int,
    irrelevant_threshold: float = 0.25,
) -> dict[str, Any]:
    """Admit context by evidence/relevance value per token under a hard budget.

    Mandatory context is selected first and fails closed when it cannot fit.
    Duplicate content hashes are charged once. Remaining candidates are selected
    deterministically by value density, utility, then stable candidate id.
    """
    budget = _nonnegative_int(max_tokens, "max_tokens")
    threshold = _bounded01(irrelevant_threshold, "irrelevant_threshold")
    normalized = [_normalized_candidate(row, i) for i, row in enumerate(candidates)]

    seen_hashes: set[str] = set()
    unique: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []
    for row in normalized:
        digest = row.get("content_hash")
        if digest and digest in seen_hashes:
            duplicates.append(row)
            continue
        if digest:
            seen_hashes.add(digest)
        unique.append(row)

    mandatory = sorted(
        (row for row in unique if row["mandatory"]),
        key=lambda row: (-row["utility"], row["candidate_id"]),
    )
    optional = sorted(
        (row for row in unique if not row["mandatory"]),
        key=lambda row: (-row["value_per_1k_tokens"], -row["utility"], row["candidate_id"]),
    )

    mandatory_tokens = sum(row["token_cost"] for row in mandatory)
    candidate_tokens = sum(row["token_cost"] for row in unique)
    duplicate_tokens_avoided = sum(row["token_cost"] for row in duplicates)
    if mandatory_tokens > budget:
        return {
            "status": "blocked",
            "reason": "mandatory_context_exceeds_budget",
            "max_tokens": budget,
            "candidate_count": len(candidates),
            "unique_candidate_count": len(unique),
            "duplicate_candidate_count": len(duplicates),
            "candidate_tokens": candidate_tokens,
            "mandatory_tokens": mandatory_tokens,
            "selected_tokens": 0,
            "selected": [],
            "rejected": unique,
            "duplicate_tokens_avoided": duplicate_tokens_avoided,
        }

    selected = list(mandatory)
    selected_ids = {row["candidate_id"] for row in selected}
    used = mandatory_tokens
    rejected: list[dict[str, Any]] = []
    for row in optional:
        cost = row["token_cost"]
        if used + cost <= budget:
            selected.append(row)
            selected_ids.add(row["candidate_id"])
            used += cost
        else:
            rejected.append(row)

    selected_relevance_weight = sum(row["relevance"] * row["token_cost"] for row in selected)
    selected_evidence_weight = sum(row["evidence_value"] * row["token_cost"] for row in selected)
    irrelevant_tokens = sum(
        row["token_cost"] for row in selected if row["relevance"] < threshold and not row["mandatory"]
    )
    selected_utility = sum(row["utility"] for row in selected)
    all_utility = sum(row["utility"] for row in unique)

    return {
        "status": "ok",
        "reason": "context_admitted_by_value_per_token",
        "max_tokens": budget,
        "candidate_count": len(candidates),
        "unique_candidate_count": len(unique),
        "duplicate_candidate_count": len(duplicates),
        "candidate_tokens": candidate_tokens,
        "selected_tokens": used,
        "rejected_tokens": max(0, candidate_tokens - used),
        "token_savings_vs_all_unique": max(0, candidate_tokens - used),
        "duplicate_tokens_avoided": duplicate_tokens_avoided,
        "budget_utilization": round(used / budget, 6) if budget else 0.0,
        "weighted_relevance": round(selected_relevance_weight / used, 6) if used else 0.0,
        "weighted_evidence_value": round(selected_evidence_weight / used, 6) if used else 0.0,
        "irrelevant_context_tokens": irrelevant_tokens,
        "irrelevant_context_ratio": round(irrelevant_tokens / used, 6) if used else 0.0,
        "utility_capture_ratio": round(selected_utility / all_utility, 6) if all_utility else 1.0,
        "selected_ids": [row["candidate_id"] for row in selected],
        "selected": selected,
        "rejected": rejected,
        "duplicates": duplicates,
    }


def compare_context_efficiency(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """Return deterministic before/after economics without claiming quality gain."""
    before_tokens = _nonnegative_int(before.get("selected_tokens", 0), "before_selected_tokens")
    after_tokens = _nonnegative_int(after.get("selected_tokens", 0), "after_selected_tokens")
    before_irrelevant = _nonnegative_int(before.get("irrelevant_context_tokens", 0), "before_irrelevant_context_tokens")
    after_irrelevant = _nonnegative_int(after.get("irrelevant_context_tokens", 0), "after_irrelevant_context_tokens")
    return {
        "status": "ok",
        "token_delta": after_tokens - before_tokens,
        "token_reduction": max(0, before_tokens - after_tokens),
        "irrelevant_token_delta": after_irrelevant - before_irrelevant,
        "irrelevant_token_reduction": max(0, before_irrelevant - after_irrelevant),
        "before_weighted_relevance": float(before.get("weighted_relevance", 0.0) or 0.0),
        "after_weighted_relevance": float(after.get("weighted_relevance", 0.0) or 0.0),
        "before_utility_capture_ratio": float(before.get("utility_capture_ratio", 0.0) or 0.0),
        "after_utility_capture_ratio": float(after.get("utility_capture_ratio", 0.0) or 0.0),
    }
