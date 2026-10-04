from __future__ import annotations

from pathlib import Path

from uacos.agent import safe_execution as safe_module


PATCH = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1 +1 @@
-old
+new
"""


def _harness() -> dict:
    return {
        "status": "passed",
        "reason": "validated",
        "run_id": "RUN-POST-APPLY",
        "attempts": [
            {
                "status": "passed",
                "adapter_result": {"patch": PATCH, "output": ""},
            }
        ],
    }


def test_guard_loss_after_apply_rolls_back_before_return(monkeypatch, tmp_path: Path):
    calls = {"guard": 0, "rollback": 0}
    monkeypatch.setattr(safe_module, "run_agent_harness", lambda *args, **kwargs: _harness())
    monkeypatch.setattr(safe_module, "capture_patch_preconditions", lambda *args, **kwargs: {"status": "pass", "files": {"app.py": "old-hash"}})
    monkeypatch.setattr(safe_module, "verify_patch_preconditions", lambda *args, **kwargs: {"status": "pass"})
    monkeypatch.setattr(safe_module, "apply_patch", lambda *args, **kwargs: {"status": "applied", "files": ["app.py"]})
    monkeypatch.setattr(safe_module, "_run_policy_tests", lambda *args, **kwargs: {"status": "pass", "results": []})

    def rollback(*args, **kwargs):
        calls["rollback"] += 1
        return {"status": "ok", "rolled_back": 1}

    def guard():
        calls["guard"] += 1
        if calls["guard"] < 3:
            return {"status": "pass", "reason": "lease_owned"}
        return {"status": "fail", "reason": "lease_fenced"}

    monkeypatch.setattr(safe_module, "rollback_patch", rollback)

    result = safe_module.run_safe_agent_execution(
        tmp_path,
        "task",
        object(),
        allowed_files=["app.py"],
        mutation_guard=guard,
    )

    assert calls["guard"] == 3
    assert calls["rollback"] == 1
    assert result["status"] == "blocked"
    assert result["reason"] == "mutation_guard_lost_after_apply"
    assert result["rollback"]["status"] == "rolled_back"
    assert [row["stage"] for row in result["mutation_guard"]] == [
        "before_preconditions",
        "before_apply",
        "before_success",
    ]


def test_guard_loss_after_apply_with_failed_rollback_never_reports_blocked_success(monkeypatch, tmp_path: Path):
    calls = {"guard": 0}
    monkeypatch.setattr(safe_module, "run_agent_harness", lambda *args, **kwargs: _harness())
    monkeypatch.setattr(safe_module, "capture_patch_preconditions", lambda *args, **kwargs: {"status": "pass"})
    monkeypatch.setattr(safe_module, "verify_patch_preconditions", lambda *args, **kwargs: {"status": "fail", "reason": "state_mismatch"})

    verification_calls = {"count": 0}

    def verify(*args, **kwargs):
        verification_calls["count"] += 1
        if verification_calls["count"] == 1:
            return {"status": "pass"}
        return {"status": "fail", "reason": "state_mismatch"}

    monkeypatch.setattr(safe_module, "verify_patch_preconditions", verify)
    monkeypatch.setattr(safe_module, "apply_patch", lambda *args, **kwargs: {"status": "applied"})
    monkeypatch.setattr(safe_module, "_run_policy_tests", lambda *args, **kwargs: {"status": "pass", "results": []})
    monkeypatch.setattr(safe_module, "rollback_patch", lambda *args, **kwargs: {"status": "ok", "rolled_back": 1})

    def guard():
        calls["guard"] += 1
        return {"status": "pass"} if calls["guard"] < 3 else {"status": "fail", "reason": "lease_lost"}

    result = safe_module.run_safe_agent_execution(
        tmp_path,
        "task",
        object(),
        allowed_files=["app.py"],
        mutation_guard=guard,
    )

    assert result["status"] == "failed"
    assert result["reason"] == "rollback_verification_failed"
    assert result["rollback"]["status"] == "rollback_failed"
