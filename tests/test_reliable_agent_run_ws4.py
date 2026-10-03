from pathlib import Path

from uacos.agent.protocol import AgentCapabilities, AgentRunResult
from uacos.runtime.reliable_agent_run import run_reliable_agent_harness
from uacos.runtime.run_state import load_run_state


VALID_DIFF = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1 +1 @@
-VALUE = 1
+VALUE = 2
"""

OUT_OF_SCOPE_DIFF = """diff --git a/other.py b/other.py
--- a/other.py
+++ b/other.py
@@ -1 +1 @@
-x = 1
+x = 2
"""


class RetryThenPassAdapter:
    name = "retry-then-pass"
    version = "1"
    capabilities = AgentCapabilities(patches=True)

    def run(self, request):
        patch = OUT_OF_SCOPE_DIFF if request.iteration == 1 else VALID_DIFF
        return AgentRunResult(
            adapter_name=self.name,
            adapter_version=self.version,
            status="completed",
            patch=patch,
            output=patch,
        )


class NeverCalledAdapter:
    name = "never-called"
    capabilities = AgentCapabilities(patches=True)

    def __init__(self):
        self.calls = 0

    def run(self, request):
        self.calls += 1
        return AgentRunResult(adapter_name=self.name, status="completed", output="no patch")


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "other.py").write_text("x = 1\n", encoding="utf-8")
    return repo


def test_reliable_harness_persists_retry_then_pass(tmp_path: Path):
    repo = _repo(tmp_path)
    report = run_reliable_agent_harness(
        repo,
        "change app:VALUE to 2",
        RetryThenPassAdapter(),
        allowed_files=["app.py"],
        max_iterations=3,
        run_id="RUN-ws4-retry-pass",
    )

    assert report["status"] == "passed"
    assert report["durable_status"] == "passed"
    assert report["run_id"] == "RUN-ws4-retry-pass"
    state = load_run_state(repo, report["run_id"])
    assert state["iteration"] == 2
    transitions = [(event["from"], event["to"]) for event in state["events"]]
    assert ("running", "retrying") in transitions
    assert ("retrying", "running") in transitions
    assert ("running", "validating") in transitions
    assert ("validating", "passed") in transitions
    assert len(state["idempotency_keys"]) == len(set(state["idempotency_keys"]))


def test_reliable_harness_enforces_expired_deadline_before_agent_call(tmp_path: Path):
    repo = _repo(tmp_path)
    adapter = NeverCalledAdapter()
    report = run_reliable_agent_harness(
        repo,
        "change app:VALUE",
        adapter,
        allowed_files=["app.py"],
        max_iterations=2,
        deadline_seconds=-1,
        run_id="RUN-ws4-expired",
    )

    assert adapter.calls == 0
    assert report["status"] == "timed_out"
    assert report["durable_status"] == "timed_out"
    state = load_run_state(repo, report["run_id"])
    assert state["iteration"] == 0
    assert state["events"][-1]["reason"] == "deadline_exceeded"


def test_harness_accepts_injected_run_id_without_durable_wrapper(tmp_path: Path):
    from uacos.agent.harness import run_agent_harness

    repo = _repo(tmp_path)
    report = run_agent_harness(
        repo,
        "change app:VALUE to 2",
        RetryThenPassAdapter(),
        allowed_files=["app.py"],
        max_iterations=3,
        run_id="RUN-injected",
    )

    assert report["run_id"] == "RUN-injected"
    assert report["status"] == "passed"
