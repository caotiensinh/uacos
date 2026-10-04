from __future__ import annotations

from pathlib import Path

import uacos.context.efficient_planner as efficient


def test_wrapper_keeps_target_and_contract_and_drops_low_value_support(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(
        efficient,
        "build_context_plan",
        lambda *args, **kwargs: {
            "status": "ok",
            "planner": "dynamic_semantic_budget_v1",
            "entries": [
                {"symbol_id": "svc:run", "file": "svc.py", "role": "target", "start_line": 1, "content": "target " * 80},
                {"symbol_id": "svc:Runner", "file": "svc.py", "role": "contract", "start_line": 1, "content": "contract " * 60},
                {"file": "docs.md", "role": "support", "start_line": 1, "content": "weak " * 300},
            ],
        },
    )

    # target ~= 140 tokens and contract ~= 135 tokens with the repo's
    # conservative len(text)/4 estimator. The budget must fit mandatory
    # context while remaining too small for the low-value support entry.
    result = efficient.build_efficient_context_plan(tmp_path, {"task": "fix run"}, max_tokens=300)

    assert result["status"] == "ok"
    roles = [row["role"] for row in result["entries"]]
    assert "target" in roles
    assert "contract" in roles
    assert "support" not in roles
    assert result["token_count"] <= 300
    assert result["token_savings_vs_all_unique"] > 0


def test_wrapper_fails_closed_when_required_context_exceeds_budget(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(
        efficient,
        "build_context_plan",
        lambda *args, **kwargs: {
            "status": "ok",
            "planner": "dynamic_semantic_budget_v1",
            "entries": [
                {"symbol_id": "svc:run", "file": "svc.py", "role": "target", "start_line": 1, "content": "required " * 400},
            ],
        },
    )

    result = efficient.build_efficient_context_plan(tmp_path, {"task": "fix run"}, max_tokens=20)

    assert result["status"] == "blocked"
    assert result["reason"] == "mandatory_context_exceeds_budget"
    assert result["entries"] == []
    assert result["content"] == ""


def test_wrapper_exposes_canonical_efficiency_metrics(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(
        efficient,
        "build_context_plan",
        lambda *args, **kwargs: {
            "status": "ok",
            "planner": "dynamic_semantic_budget_v1",
            "entries": [
                {"symbol_id": "svc:run", "file": "svc.py", "role": "target", "start_line": 1, "content": "target code"},
                {"file": "tests/test_svc.py", "role": "test_support", "start_line": 1, "content": "assert run"},
            ],
        },
    )

    result = efficient.build_efficient_context_plan(tmp_path, {"task": "fix run"}, max_tokens=100)

    assert result["status"] == "ok"
    assert result["planner"] == "dynamic_semantic_budget_v1+value_per_token_v1"
    assert 0.0 <= result["weighted_relevance"] <= 1.0
    assert 0.0 <= result["weighted_evidence_value"] <= 1.0
    assert 0.0 <= result["utility_capture_ratio"] <= 1.0
    assert result["irrelevant_context_tokens"] == 0
