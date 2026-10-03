from pathlib import Path

from uacos.agent.protocol import AgentCapabilities, AgentRunResult
from uacos.agent.harness import run_agent_harness
from uacos.runtime.reliable_agent_run import run_reliable_agent_harness


class RepeatingNoPatchAdapter:
    name = "repeating-no-patch"
    version = "1"
    capabilities = AgentCapabilities(patches=True)

    def __init__(self):
        self.calls = 0

    def run(self, request):
        self.calls += 1
        return AgentRunResult(
            adapter_name=self.name,
            adapter_version=self.version,
            status="completed",
            output="same non-patch answer",
        )


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
    return repo


def test_live_harness_stops_after_repeated_identical_outcome(tmp_path: Path):
    repo = _repo(tmp_path)
    adapter = RepeatingNoPatchAdapter()

    report = run_agent_harness(
        repo,
        "change app:VALUE",
        adapter,
        allowed_files=["app.py"],
        max_iterations=5,
        no_progress_threshold=2,
    )

    assert adapter.calls == 2
    assert report["status"] == "failed"
    assert report["reason"] == "no_progress_repeated_identical_outcome"
    assert report["metrics"]["bounded_stop"] is True
    assert report["metrics"]["attempt_count"] == 2
    assert report["no_progress"]["consecutive_same_outcome"] == 2
    assert report["attempts"][-1]["no_progress"]["stalled"] is True


def test_threshold_three_allows_two_identical_attempts(tmp_path: Path):
    repo = _repo(tmp_path)
    adapter = RepeatingNoPatchAdapter()

    report = run_agent_harness(
        repo,
        "change app:VALUE",
        adapter,
        allowed_files=["app.py"],
        max_iterations=2,
        no_progress_threshold=3,
    )

    assert adapter.calls == 2
    assert report["reason"] == "no_patch"
    assert report["metrics"]["bounded_stop"] is False
    assert report["no_progress"] is None


def test_durable_wrapper_persists_bounded_stop_as_terminal_failure(tmp_path: Path):
    repo = _repo(tmp_path)
    adapter = RepeatingNoPatchAdapter()

    report = run_reliable_agent_harness(
        repo,
        "change app:VALUE",
        adapter,
        allowed_files=["app.py"],
        max_iterations=5,
        run_id="RUN-no-progress-live",
    )

    assert adapter.calls == 2
    assert report["status"] == "failed"
    assert report["durable_status"] == "failed"
    assert report["reason"] == "no_progress_repeated_identical_outcome"
    assert report["durable_state"]["events"][-1]["reason"] == "no_progress_repeated_identical_outcome"
