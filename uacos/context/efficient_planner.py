from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any

from uacos.context.efficiency import admit_context_candidates
from uacos.context.planner import build_context_plan
from uacos.llm.hardened import estimate_tokens


ROLE_RELEVANCE = {
    "target": 1.0,
    "contract": 0.95,
    "test_support": 0.85,
    "neighbor": 0.75,
    "support": 0.35,
}

ROLE_EVIDENCE_VALUE = {
    "target": 1.0,
    "contract": 0.95,
    "test_support": 0.95,
    "neighbor": 0.75,
    "support": 0.30,
}

MANDATORY_ROLES = {"target", "contract"}


def _candidate_from_entry(entry: dict[str, Any], index: int) -> dict[str, Any]:
    role = str(entry.get("role") or "support")
    content = str(entry.get("content") or "")
    token_cost = max(0, estimate_tokens(content))
    candidate_id = str(entry.get("symbol_id") or f"{entry.get('file') or 'entry'}:{entry.get('start_line') or index}:{index}")
    digest = sha256(content.encode("utf-8")).hexdigest() if content else None
    return {
        "candidate_id": candidate_id,
        "relevance": ROLE_RELEVANCE.get(role, 0.25),
        "evidence_value": ROLE_EVIDENCE_VALUE.get(role, 0.25),
        "reuse_probability": 0.20 if role in {"contract", "test_support"} else 0.05,
        "token_cost": token_cost,
        "mandatory": role in MANDATORY_ROLES,
        "content_hash": digest,
        "entry": entry,
    }


def build_efficient_context_plan(
    repo_root: Path,
    impact: dict[str, Any],
    *,
    max_tokens: int,
    planner_max_chars: int | None = None,
    max_files: int = 8,
    max_symbols_per_file: int = 2,
) -> dict[str, Any]:
    """Reuse the existing semantic planner, then admit entries by value/token.

    This is additive: the legacy planner remains authoritative for candidate
    discovery and slicing. Phase 3 only adds deterministic economics, hard token
    admission and canonical efficiency metrics on top.
    """
    max_tokens = int(max_tokens)
    if max_tokens < 0:
        raise ValueError("max_tokens_must_be_nonnegative")
    char_budget = planner_max_chars if planner_max_chars is not None else max(1000, max_tokens * 4)
    plan = build_context_plan(
        repo_root,
        impact,
        max_chars=char_budget,
        max_files=max_files,
        max_symbols_per_file=max_symbols_per_file,
    )
    candidates = [_candidate_from_entry(entry, i) for i, entry in enumerate(plan.get("entries", []))]
    admission = admit_context_candidates(candidates, max_tokens=max_tokens)
    if admission.get("status") != "ok":
        return {
            "status": "blocked",
            "reason": admission.get("reason"),
            "planner": "dynamic_semantic_budget_v1+value_per_token_v1",
            "base_plan": plan,
            "admission": admission,
            "entries": [],
            "content": "",
            "token_count": 0,
        }

    selected = [row["entry"] for row in admission["selected"]]
    content = "\n\n".join(str(row.get("content") or "") for row in selected if row.get("content"))
    token_count = estimate_tokens(content)
    return {
        "status": "ok",
        "planner": "dynamic_semantic_budget_v1+value_per_token_v1",
        "base_plan": plan,
        "admission": admission,
        "entries": selected,
        "content": content,
        "token_count": token_count,
        "selected_file_count": len({str(row.get("file")) for row in selected}),
        "entry_count": len(selected),
        "tokens_to_context": token_count,
        "irrelevant_context_tokens": admission["irrelevant_context_tokens"],
        "irrelevant_context_ratio": admission["irrelevant_context_ratio"],
        "weighted_relevance": admission["weighted_relevance"],
        "weighted_evidence_value": admission["weighted_evidence_value"],
        "utility_capture_ratio": admission["utility_capture_ratio"],
        "duplicate_tokens_avoided": admission["duplicate_tokens_avoided"],
        "token_savings_vs_all_unique": admission["token_savings_vs_all_unique"],
    }
