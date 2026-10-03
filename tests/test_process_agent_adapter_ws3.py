from pathlib import Path
import sys

from uacos.agent.harness import run_agent_harness
from uacos.agent.process_adapter import SubprocessAgentAdapter, build_agent_prompt
from uacos.agent.protocol import AgentRunRequest


DIFF = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1,2 +1,2 @@
 def value():
-    return 1
+    return 42
"""


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    return repo


def test_prompt_contains_runtime_scope_and_context():
    request = AgentRunRequest(
        task="fix app:value",
        context="semantic context here",
        allowed_files=["app.py"],
        allowed_dirs=["pkg"],
        tests=["python -m pytest -q"],
        run_id="RUN-test",
        iteration=2,
    )
    prompt = build_agent_prompt(request)
    assert "RUN-test" in prompt
    assert "Iteration: 2" in prompt
    assert "app.py" in prompt
    assert "semantic context here" in prompt


def test_subprocess_adapter_runs_without_shell_and_integrates_with_harness(tmp_path: Path):
    repo = _repo(tmp_path)
    code = "import sys; sys.stdin.read(); print(" + repr(DIFF) + ")"
    adapter = SubprocessAgentAdapter(
        "fake-cli",
        [sys.executable, "-c", code],
        version="test",
        cwd=repo,
    )

    report = run_agent_harness(
        repo,
        "fix app:value",
        adapter,
        allowed_files=["app.py"],
        max_iterations=1,
    )

    assert report["status"] == "passed"
    assert report["metrics"]["first_pass_success"] is True
    result = report["attempts"][0]["adapter_result"]
    assert result["adapter_name"] == "fake-cli"
    assert result["exit_code"] == 0
    assert report["attempts"][0]["patch_validation"]["status"] == "pass"


def test_subprocess_adapter_classifies_nonzero_exit(tmp_path: Path):
    repo = _repo(tmp_path)
    adapter = SubprocessAgentAdapter(
        "failing-cli",
        [sys.executable, "-c", "import sys; print('bad', file=sys.stderr); raise SystemExit(7)"],
        cwd=repo,
    )
    result = adapter.run(AgentRunRequest(task="x", context="", timeout_seconds=5))
    assert result.status == "failed"
    assert result.exit_code == 7
    assert result.failure_class == "adapter_nonzero_exit"
    assert "bad" in result.evidence["stderr"]


def test_subprocess_adapter_classifies_timeout(tmp_path: Path):
    repo = _repo(tmp_path)
    adapter = SubprocessAgentAdapter(
        "slow-cli",
        [sys.executable, "-c", "import time; time.sleep(2)"],
        cwd=repo,
    )
    result = adapter.run(AgentRunRequest(task="x", context="", timeout_seconds=1))
    assert result.status == "timeout"
    assert result.failure_class == "adapter_timeout"
