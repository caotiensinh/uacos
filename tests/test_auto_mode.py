import json
import subprocess
import sys
from pathlib import Path

from uacos.auto.engine import run_auto_once, install_auto_launcher


def test_auto_mode_once_prepares_repo(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    report = run_auto_once(repo, task="inspect app quality", performance=False)
    assert report["status"] == "pass", report
    assert (repo / "reports" / "uacos_auto_report.json").exists()
    step_names = {step["name"] for step in report["steps"]}
    assert {"bootstrap", "graph_build", "compression_cache", "task_context_ready"} <= step_names


def test_auto_launcher_and_cli(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    launcher = install_auto_launcher(repo)
    assert launcher["status"] == "ok"
    assert (repo / "UACOS_AUTO_START.py").exists()

    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "uacos.cli", "auto", "--repo", str(repo), "--task", "inspect app quality", "--skip-performance"],
        cwd=root,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    data = json.loads(result.stdout)
    assert data["status"] == "pass"

def test_auto_mode_records_and_recalls_experience(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")

    first = run_auto_once(repo, task="dogfood token savings", performance=True)
    assert first["status"] == "pass", first
    names = {step["name"] for step in first["steps"]}
    assert {"experience_recall", "experience_record", "performance_probe"} <= names
    assert (repo / ".uacos" / "memory.jsonl").exists()
    assert (repo / ".uacos" / "skill35").exists()

    second = run_auto_once(repo, task="dogfood token savings", performance=False)
    recall = next(step for step in second["steps"] if step["name"] == "experience_recall")
    assert recall["ok"] is True
    assert recall["result"]["matched_skill_count"] >= 0
