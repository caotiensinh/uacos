from __future__ import annotations

from pathlib import Path

from uacos.agent import safe_execution as safe_module
from uacos.runtime.leased_safe_execution import _resource_scope, run_leased_safe_agent_execution
from uacos.runtime.resource_lease import SQLiteResourceLeaseStore


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
        "run_id": "RUN-1",
        "attempts": [
            {
                "status": "passed",
                "adapter_result": {"patch": PATCH, "output": ""},
            }
        ],
    }


def test_mutation_guard_failure_before_preconditions_prevents_apply(monkeypatch, tmp_path: Path):
    calls = {"capture": 0, "apply": 0}
    monkeypatch.setattr(safe_module, "run_agent_harness", lambda *args, **kwargs: _harness())

    def capture(*args, **kwargs):
        calls["capture"] += 1
        return {"status": "pass"}

    def apply(*args, **kwargs):
        calls["apply"] += 1
        return {"status": "applied"}

    monkeypatch.setattr(safe_module, "capture_patch_preconditions", capture)
    monkeypatch.setattr(safe_module, "apply_patch", apply)

    result = safe_module.run_safe_agent_execution(
        tmp_path,
        "task",
        object(),
        allowed_files=["app.py"],
        mutation_guard=lambda: {"status": "fail", "reason": "lease_fenced"},
    )

    assert result["status"] == "blocked"
    assert result["reason"] == "mutation_guard_blocked"
    assert result["mutation_guard"][0]["stage"] == "before_preconditions"
    assert calls == {"capture": 0, "apply": 0}


def test_second_mutation_guard_failure_prevents_apply(monkeypatch, tmp_path: Path):
    calls = {"guard": 0, "apply": 0}
    monkeypatch.setattr(safe_module, "run_agent_harness", lambda *args, **kwargs: _harness())
    monkeypatch.setattr(safe_module, "capture_patch_preconditions", lambda *args, **kwargs: {"status": "pass"})
    monkeypatch.setattr(safe_module, "verify_patch_preconditions", lambda *args, **kwargs: {"status": "pass"})

    def apply(*args, **kwargs):
        calls["apply"] += 1
        return {"status": "applied"}

    def guard():
        calls["guard"] += 1
        return {"status": "pass"} if calls["guard"] == 1 else {"status": "fail", "reason": "lease_lost"}

    monkeypatch.setattr(safe_module, "apply_patch", apply)
    result = safe_module.run_safe_agent_execution(
        tmp_path,
        "task",
        object(),
        allowed_files=["app.py"],
        mutation_guard=guard,
    )

    assert result["status"] == "blocked"
    assert result["reason"] == "mutation_guard_blocked"
    assert [row["stage"] for row in result["mutation_guard"]] == ["before_preconditions", "before_apply"]
    assert calls["guard"] == 2
    assert calls["apply"] == 0


def test_scope_collapses_files_and_nested_dirs_under_parent_directory():
    scope = _resource_scope(
        ["src/app.py", "README.md", "src/core/x.py"],
        ["src", "src/core", "src"],
    )
    assert scope == [("dir", "src"), ("file", "README.md")]


def test_conflict_blocks_before_safe_execution(tmp_path: Path):
    store = SQLiteResourceLeaseStore(tmp_path)
    store.acquire(resource_type="dir", resource_key="src", owner_id="other", ttl_seconds=30)
    called = {"safe": 0}

    def fake_safe(*args, **kwargs):
        called["safe"] += 1
        return {"status": "passed", "reason": "should_not_run"}

    result = run_leased_safe_agent_execution(
        tmp_path,
        "task",
        object(),
        owner_id="agent-a",
        lease_store=store,
        safe_execution_fn=fake_safe,
        allowed_files=["src/app.py"],
    )

    assert result["status"] == "blocked"
    assert result["reason"] == "resource_lease_conflict"
    assert called["safe"] == 0


def test_wrapper_passes_fencing_guard_and_releases_lease(tmp_path: Path):
    store = SQLiteResourceLeaseStore(tmp_path)
    seen = {"guards": 0}

    def fake_safe(repo_root, task, adapter, **kwargs):
        guard = kwargs["mutation_guard"]
        first = guard()
        second = guard()
        seen["guards"] = 2
        assert first["status"] == "pass"
        assert second["status"] == "pass"
        return {"status": "passed", "reason": "ok"}

    result = run_leased_safe_agent_execution(
        tmp_path,
        "task",
        object(),
        owner_id="agent-a",
        lease_ttl_seconds=30,
        heartbeat_interval_seconds=10,
        lease_store=store,
        safe_execution_fn=fake_safe,
        allowed_dirs=["src"],
        allowed_files=["src/app.py"],
    )

    assert result["status"] == "passed"
    assert result["lease_report"]["status"] == "pass"
    assert result["lease_report"]["scope"] == [("dir", "src")]
    assert seen["guards"] == 2
    assert store.list_active() == []
