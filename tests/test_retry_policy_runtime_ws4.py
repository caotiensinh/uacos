from pathlib import Path

from uacos.agent.protocol import AgentCapabilities, AgentRunResult
from uacos.runtime.reliable_agent_run import run_reliable_agent_harness


PATCH = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1 +1 @@
-VALUE = 1
+VALUE = 2
"""


class TimeoutThenPatchAdapter:
    name = "timeout-then-patch"
    version = "1"
    capabilities = AgentCapabilities(patches=True)

    def __init__(self):
        self.calls = 0

    def run(self, request):
        self.calls += 1
        if self.calls == 1:
            raise TimeoutError("synthetic timeout")
        return AgentRunResult(
            adapter_name=self.name,
            adapter_version=self.version,
            status="completed",
            patch=PATCH,
            output=PATCH,
        )


class UnknownFailureAdapter:
    name = "unknown-failure"
    version = "1"
    capabilities = AgentCapabilities(patches=True)

    def __init__(self):
        self.calls = 0

    def run(self, request):
        self.calls += 1
        return AgentRunResult(
            adapter_name=self.name,
            adapter_version=self.version,
            status="error",
            failure_class="mystery_failure",
            output="failed without patch",
        )


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
    return repo


def test_transient_timeout_retries_then_passes(tmp_path: Path):
    repo = _repo(tmp_path)
    adapter = TimeoutThenPatchAdapter()

    report = run_reliable_agent_harness(
        repo,
        "change app:VALUE",
        adapter,
        allowed_files=["app.py"],
        max_iterations=3,
        run_id="RUN-retry-timeout",
    )

    assert adapter.calls == 2
    assert report["status"] == "passed"
    assert report["durable_status"] == "passed"
    retry_events = [e for e in report["durable_state"]["events"] if e["status"] == "retrying"]
    assert retry_events
    assert retry_events[0]["reason"] == "retryable:adapter_timeout"
    assert retry_events[0]["evidence"]["retry_decision"]["delay_ms"] == 250


def test_unknown_failure_fails_closed_before_next_agent_call(tmp_path: Path):
    repo = _repo(tmp_path)
    adapter = UnknownFailureAdapter()

    report = run_reliable_agent_harness(
        repo,
        "change app:VALUE",
        adapter,
        allowed_files=["app.py"],
        max_iterations=4,
        run_id="RUN-retry-unknown",
    )

    assert adapter.calls == 1
    assert report["durable_status"] == "failed"
    assert report["durable_state"]["events"][-1]["reason"] == "unknown_failure_fail_closed:mystery_failure"
