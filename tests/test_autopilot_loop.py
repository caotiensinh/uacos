from pathlib import Path

from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.autopilot.orchestrator import autopilot_loop, list_autopilot_runs


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def ok():\n    return True\n", encoding="utf-8")
    init_storage(repo)
    scan_repo(repo)
    return repo


def test_autopilot_loop_refuses_manual_chat_adapter(tmp_path: Path):
    repo = _init_repo(tmp_path)
    result = autopilot_loop(repo, "Fix bug", "Fix the demo bug", adapter="manual_chat")
    assert result["status"] == "blocked"
    assert result["reason"] == "adapter_cannot_loop_unattended"


def test_autopilot_loop_rejects_zero_iterations(tmp_path: Path):
    repo = _init_repo(tmp_path)
    result = autopilot_loop(repo, "Fix bug", "Fix the demo bug", max_iterations=0, adapter="ollama_openai")
    assert result["status"] == "blocked"
    assert result["reason"] == "max_iterations_must_be_at_least_1"


def test_autopilot_loop_exhausts_and_records_every_attempt(tmp_path: Path):
    repo = _init_repo(tmp_path)
    result = autopilot_loop(repo, "Fix bug", "Fix the demo bug", adapter="ollama_openai", max_iterations=2)

    # Dry-run adapter (no network/config) never produces a real patch, so the
    # loop must retry up to max_iterations and then report exhaustion rather
    # than silently stopping early or claiming success.
    assert result["status"] == "exhausted"
    assert result["iterations_used"] == 2
    assert len(result["attempts"]) == 2
    assert all(a["status"] != "done" for a in result["attempts"])

    runs = list_autopilot_runs(repo)
    assert runs["count"] == 2
    recorded_ids = {r["id"] for r in runs["runs"]}
    attempted_ids = {a["run_id"] for a in result["attempts"]}
    assert recorded_ids == attempted_ids
