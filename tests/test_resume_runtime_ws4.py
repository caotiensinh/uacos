from pathlib import Path

import pytest

from uacos.agent.protocol import AgentCapabilities, AgentRunResult
from uacos.runtime.reliable_agent_run import run_reliable_agent_harness
from uacos.runtime.run_state import begin_iteration, create_run_state, load_run_state, transition_run


PATCH = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1 +1 @@
-VALUE = 1
+VALUE = 2
"""


class ResumePatchAdapter:
    name = "resume-fixture"
    version = "1"
    capabilities = AgentCapabilities(patches=True)

    def __init__(self):
        self.iterations = []

    def run(self, request):
        self.iterations.append(request.iteration)
        return AgentRunResult(
            adapter_name=self.name,
            adapter_version=self.version,
            status="completed",
            patch=PATCH,
            output=PATCH,
        )


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
    return repo


def _state(repo: Path, run_id: str = "RUN-resume"):
    return create_run_state(
        repo,
        "change app:VALUE",
        max_iterations=3,
        run_id=run_id,
        metadata={"adapter": "resume-fixture", "timeout_seconds": 120},
    )


def test_resume_interrupted_running_state_continues_at_next_iteration(tmp_path: Path):
    repo = _repo(tmp_path)
    _state(repo)
    begin_iteration(repo, "RUN-resume", idempotency_key="iteration:1:begin")
    assert load_run_state(repo, "RUN-resume")["status"] == "running"

    adapter = ResumePatchAdapter()
    report = run_reliable_agent_harness(
        repo,
        "change app:VALUE",
        adapter,
        allowed_files=["app.py"],
        max_iterations=3,
        run_id="RUN-resume",
    )

    assert adapter.iterations == [2]
    assert report["status"] == "passed"
    assert report["durable_status"] == "passed"
    assert report["metrics"]["resumed"] is True
    assert report["policy"]["start_iteration"] == 2
    assert report["durable_state"]["iteration"] == 2
    assert any(event["reason"] == "resume_interrupted_run" for event in report["durable_state"]["events"])


def test_resume_retrying_state_does_not_replay_completed_iteration(tmp_path: Path):
    repo = _repo(tmp_path)
    _state(repo, "RUN-retrying")
    begin_iteration(repo, "RUN-retrying", idempotency_key="iteration:1:begin")
    transition_run(
        repo,
        "RUN-retrying",
        "retrying",
        reason="synthetic_failure",
        idempotency_key="iteration:1:retrying",
    )

    adapter = ResumePatchAdapter()
    report = run_reliable_agent_harness(
        repo,
        "change app:VALUE",
        adapter,
        allowed_files=["app.py"],
        max_iterations=3,
        run_id="RUN-retrying",
    )

    assert adapter.iterations == [2]
    assert report["durable_state"]["iteration"] == 2
    assert report["durable_status"] == "passed"


def test_resume_rejects_budget_drift(tmp_path: Path):
    repo = _repo(tmp_path)
    _state(repo, "RUN-budget")

    with pytest.raises(ValueError, match="resume_max_iterations_mismatch"):
        run_reliable_agent_harness(
            repo,
            "change app:VALUE",
            ResumePatchAdapter(),
            allowed_files=["app.py"],
            max_iterations=4,
            run_id="RUN-budget",
        )


def test_terminal_run_is_not_resumed(tmp_path: Path):
    repo = _repo(tmp_path)
    _state(repo, "RUN-terminal")
    begin_iteration(repo, "RUN-terminal", idempotency_key="iteration:1:begin")
    transition_run(repo, "RUN-terminal", "passed", reason="already_done")

    with pytest.raises(ValueError, match="terminal_run_not_resumable:passed"):
        run_reliable_agent_harness(
            repo,
            "change app:VALUE",
            ResumePatchAdapter(),
            allowed_files=["app.py"],
            max_iterations=3,
            run_id="RUN-terminal",
        )
