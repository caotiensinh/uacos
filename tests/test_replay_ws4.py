from pathlib import Path
import json

from uacos.config import uacos_dir
from uacos.runtime.replay import build_run_replay, verify_run_replay, write_run_replay
from uacos.runtime.run_state import begin_iteration, create_run_state, transition_run


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    return repo


def test_replay_reconstructs_durable_timeline_without_agent_evidence(tmp_path: Path):
    repo = _repo(tmp_path)
    create_run_state(repo, "demo task", max_iterations=3, run_id="RUN-replay")
    begin_iteration(repo, "RUN-replay", idempotency_key="iteration:1:begin")
    transition_run(repo, "RUN-replay", "failed", reason="synthetic_failure")

    replay = build_run_replay(repo, "RUN-replay")

    assert replay["run_id"] == "RUN-replay"
    assert replay["durable_status"] == "failed"
    assert replay["verification"]["status"] == "pass"
    assert replay["verification"]["event_count"] >= 3
    assert replay["agent_evidence"] is None
    assert replay["source_hashes"]["run_state_sha256"]


def test_replay_includes_agent_attempts_and_detects_status_mismatch(tmp_path: Path):
    repo = _repo(tmp_path)
    create_run_state(repo, "demo task", max_iterations=2, run_id="RUN-evidence")
    begin_iteration(repo, "RUN-evidence", idempotency_key="iteration:1:begin")
    transition_run(repo, "RUN-evidence", "failed", reason="no_patch")

    evidence_dir = uacos_dir(repo) / "agent_runs"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "RUN-evidence.json").write_text(
        json.dumps({
            "run_id": "RUN-evidence",
            "task": "demo task",
            "status": "passed",
            "attempts": [{"iteration": 1, "status": "failed", "failure_class": "no_patch"}],
        }),
        encoding="utf-8",
    )

    replay = build_run_replay(repo, "RUN-evidence")

    assert replay["verification"]["status"] == "fail"
    assert replay["verification"]["attempt_count"] == 1
    assert any(row["reason"] == "terminal_status_mismatch" for row in replay["verification"]["findings"])
    assert replay["source_hashes"]["agent_evidence_sha256"]


def test_write_replay_persists_verifiable_bundle(tmp_path: Path):
    repo = _repo(tmp_path)
    create_run_state(repo, "demo task", max_iterations=1, run_id="RUN-write")
    begin_iteration(repo, "RUN-write", idempotency_key="iteration:1:begin")
    transition_run(repo, "RUN-write", "passed", reason="patch_validated")

    path = Path(write_run_replay(repo, "RUN-write"))
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert path.exists()
    assert payload["verification"]["status"] == "pass"
    assert verify_run_replay(payload)["status"] == "pass"
