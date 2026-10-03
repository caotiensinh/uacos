from pathlib import Path

from uacos.agent.harness import run_agent_harness
from uacos.agent.protocol import AgentCapabilities, AgentRunResult, AgentRunRequest


VALID_DIFF = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1,2 +1,2 @@
 def value():
-    return 1
+    return 42
"""


class RetryAdapter:
    name = "fake-retry"
    version = "1.0"
    capabilities = AgentCapabilities(patches=True, token_usage=True)

    def __init__(self):
        self.requests = []

    def run(self, request: AgentRunRequest):
        self.requests.append(request)
        if request.iteration == 1:
            return {
                "status": "completed",
                "diff": """diff --git a/other.py b/other.py
--- a/other.py
+++ b/other.py
@@ -1 +1 @@
-x = 1
+x = 2
""",
                "tokens_in": 100,
                "tokens_out": 20,
                "tool_calls": 1,
            }
        return AgentRunResult(
            adapter_name=self.name,
            adapter_version=self.version,
            status="diff_ready",
            patch=VALID_DIFF,
            tokens_in=80,
            tokens_out=10,
            tool_calls=2,
        )


class NoPatchAdapter:
    name = "fake-no-patch"

    def run(self, request: AgentRunRequest):
        return {"status": "completed", "output": "I think this is done."}


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    (repo / "other.py").write_text("x = 1\n", encoding="utf-8")
    return repo


def test_harness_retries_validation_failure_then_passes(tmp_path: Path):
    repo = _repo(tmp_path)
    adapter = RetryAdapter()

    report = run_agent_harness(
        repo,
        "fix app:value",
        adapter,
        allowed_files=["app.py"],
        tests=["python -m pytest -q"],
        max_iterations=3,
    )

    assert report["status"] == "passed"
    assert report["reason"] == "patch_validated"
    assert report["metrics"]["attempt_count"] == 2
    assert report["metrics"]["retry_count"] == 1
    assert report["metrics"]["first_pass_success"] is False
    assert report["metrics"]["tokens_in"] == 180
    assert report["metrics"]["tokens_out"] == 30
    assert report["metrics"]["tool_calls"] == 3
    assert report["attempts"][0]["failure_class"] == "patch_validation_failed"
    assert report["attempts"][1]["patch_validation"]["status"] == "pass"
    assert report["policy"]["validate_only"] is True
    assert Path(report["evidence_file"]).exists()
    assert adapter.requests[0].run_id == adapter.requests[1].run_id
    assert adapter.requests[0].metadata["context_model"] == "dynamic_semantic_budget_v1"


def test_harness_stops_at_bounded_iteration_limit(tmp_path: Path):
    repo = _repo(tmp_path)
    report = run_agent_harness(
        repo,
        "fix app:value",
        NoPatchAdapter(),
        allowed_files=["app.py"],
        max_iterations=2,
    )

    assert report["status"] == "failed"
    assert report["reason"] == "no_patch"
    assert report["metrics"]["attempt_count"] == 2
    assert report["metrics"]["retry_count"] == 1
    assert all(row["failure_class"] == "no_patch" for row in report["attempts"])


def test_harness_honors_cancellation_before_agent_call(tmp_path: Path):
    repo = _repo(tmp_path)
    adapter = NoPatchAdapter()
    calls = {"count": 0}

    def cancelled():
        calls["count"] += 1
        return True

    report = run_agent_harness(
        repo,
        "fix app:value",
        adapter,
        allowed_files=["app.py"],
        cancel_check=cancelled,
    )

    assert report["status"] == "cancelled"
    assert report["reason"] == "cancel_requested"
    assert report["metrics"]["attempt_count"] == 0
    assert calls["count"] == 1
