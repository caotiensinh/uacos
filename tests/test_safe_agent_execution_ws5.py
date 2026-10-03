from pathlib import Path

import uacos.agent.safe_execution as safe_execution
from uacos.agent.protocol import AgentCapabilities, AgentRunResult
from uacos.agent.safe_execution import run_safe_agent_execution


PATCH = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1 +1 @@
-VALUE = 1
+VALUE = 2
"""


class PatchAdapter:
    name = "fixture"
    version = "1"
    capabilities = AgentCapabilities(patches=True)

    def run(self, request):
        return AgentRunResult(
            adapter_name=self.name,
            adapter_version=self.version,
            status="completed",
            patch=PATCH,
            output=PATCH,
        )


def test_safe_execution_applies_patch_and_runs_allowed_test(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "app.py"
    target.write_text("VALUE = 1\n", encoding="utf-8")

    result = run_safe_agent_execution(
        repo,
        "change app:VALUE to 2",
        PatchAdapter(),
        allowed_files=["app.py"],
        tests=["python -c \"from pathlib import Path; assert 'VALUE = 2' in Path('app.py').read_text()\""],
        max_iterations=1,
    )

    assert result["status"] == "passed"
    assert result["reason"] == "patch_applied_tests_passed"
    assert result["preconditions"]["status"] == "pass"
    assert result["precondition_verification"]["status"] == "pass"
    assert result["tests"]["status"] == "pass"
    assert target.read_text(encoding="utf-8") == "VALUE = 2\n"


def test_blocked_test_command_rolls_patch_back(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "app.py"
    target.write_text("VALUE = 1\n", encoding="utf-8")

    result = run_safe_agent_execution(
        repo,
        "change app:VALUE to 2",
        PatchAdapter(),
        allowed_files=["app.py"],
        tests=["rm -rf /"],
        max_iterations=1,
    )

    assert result["status"] == "failed"
    assert result["reason"] == "test_command_blocked"
    assert result["tests"]["results"][0]["status"] == "blocked"
    assert result["rollback"]["status"] == "rolled_back"
    assert result["rollback"]["rolled_back"] == 1
    assert result["rollback"]["engine_result"]["status"] == "ok"
    assert result["rollback"]["verification"]["status"] == "pass"
    assert target.read_text(encoding="utf-8") == "VALUE = 1\n"


def test_out_of_scope_agent_patch_never_applies(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("VALUE = 1\n", encoding="utf-8")

    result = run_safe_agent_execution(
        repo,
        "change value",
        PatchAdapter(),
        allowed_files=["other.py"],
        max_iterations=1,
    )

    assert result["status"] == "failed"
    assert result["patch_apply"] is None
    assert (repo / "app.py").read_text(encoding="utf-8") == "VALUE = 1\n"


def test_workspace_race_is_blocked_before_apply(tmp_path: Path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "app.py"
    target.write_text("VALUE = 1\n", encoding="utf-8")
    original_capture = safe_execution.capture_patch_preconditions

    def capture_then_race(repo_root: Path, patch_text: str):
        snapshot = original_capture(repo_root, patch_text)
        target.write_text("VALUE = 99\n", encoding="utf-8")
        return snapshot

    monkeypatch.setattr(safe_execution, "capture_patch_preconditions", capture_then_race)
    result = run_safe_agent_execution(
        repo,
        "change app:VALUE to 2",
        PatchAdapter(),
        allowed_files=["app.py"],
        max_iterations=1,
    )

    assert result["status"] == "failed"
    assert result["reason"] == "stale_patch_precondition_failed"
    assert result["precondition_verification"]["stale"] is True
    assert result["precondition_verification"]["findings"][0]["reason"] == "stale_source_modified"
    assert result["patch_apply"] is None
    assert target.read_text(encoding="utf-8") == "VALUE = 99\n"


def test_rollback_success_claim_must_match_preapply_hash(tmp_path: Path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "app.py"
    target.write_text("VALUE = 1\n", encoding="utf-8")

    monkeypatch.setattr(
        safe_execution,
        "rollback_patch",
        lambda repo_root, applied: {"status": "ok", "rolled_back": 1},
    )
    result = run_safe_agent_execution(
        repo,
        "change app:VALUE to 2",
        PatchAdapter(),
        allowed_files=["app.py"],
        tests=["rm -rf /"],
        max_iterations=1,
    )

    assert result["status"] == "failed"
    assert result["reason"] == "rollback_verification_failed"
    assert result["rollback"]["status"] == "rollback_failed"
    assert result["rollback"]["engine_result"]["status"] == "ok"
    assert result["rollback"]["verification"]["status"] == "fail"
    assert result["rollback"]["verification"]["findings"][0]["reason"] == "stale_source_modified"
    assert target.read_text(encoding="utf-8") == "VALUE = 2\n"
