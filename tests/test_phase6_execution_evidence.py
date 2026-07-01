from pathlib import Path
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.agent.task import create_task
from uacos.execution.diff_extract import extract_unified_diff
from uacos.execution.artifacts import ingest_agent_output, evidence_report_v2
from uacos.execution.test_runner import run_task_tests
from uacos.execution.token_ledger import log_token_usage, ledger_summary
from uacos.execution.failed_memory import read_failures

def test_phase6_diff_extract_and_artifact_ingest(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def ok():\n    return False\n", encoding="utf-8")
    init_storage(repo)
    scan_repo(repo)
    task_file = create_task(repo, "Fix ok", "Fix ok return value", allowed_files=["app.py"], tests=["python -m pytest"])
    agent_output = repo / "agent.md"
    agent_output.write_text(
        "Here is the patch:\n```diff\n"
        "diff --git a/app.py b/app.py\n"
        "--- a/app.py\n"
        "+++ b/app.py\n"
        "@@ -1,2 +1,2 @@\n"
        " def ok():\n"
        "-    return False\n"
        "+    return True\n"
        "```\n",
        encoding="utf-8",
    )
    diff = extract_unified_diff(agent_output.read_text(encoding="utf-8"))
    assert "diff --git" in diff
    artifact = ingest_agent_output(repo, task_file, agent_output)
    assert artifact["status"] == "pass"
    assert artifact["has_diff"] is True
    assert Path(artifact["artifact_file"]).exists()
    assert Path(artifact["diff_file"]).exists()

def test_phase6_test_runner_blocks_dangerous_and_runs_safe(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "script.py").write_text("print('ok')\n", encoding="utf-8")
    init_storage(repo)
    task_file = create_task(repo, "Run tests", "Run safe command", allowed_files=["script.py"], tests=["python script.py", "rm -rf /"])
    result = run_task_tests(repo, task_file)
    assert result["status"] == "fail"
    statuses = [r["status"] for r in result["results"]]
    assert "pass" in statuses
    assert "blocked" in statuses

def test_phase6_token_ledger_failed_memory_and_evidence(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def ok():\n    return True\n", encoding="utf-8")
    init_storage(repo)
    scan_repo(repo)
    task_file = create_task(repo, "No diff", "Agent forgot diff", allowed_files=["app.py"], tests=["python -m pytest"])
    agent_output = repo / "agent_no_diff.md"
    agent_output.write_text("DONE. I changed it.", encoding="utf-8")
    log_token_usage(repo, "TASK-X", "coder", "local", 100, 50, "CTX-X")
    summary = ledger_summary(repo)
    assert summary["records"] == 1
    assert summary["estimated_cost_usd"] == 0.0
    md = evidence_report_v2(repo, task_file, agent_output, test_result=None, token_summary=summary)
    assert "Evidence Report v2" in md
    assert "PARTIAL" in md
    failures = read_failures(repo)
    assert failures
    assert failures[-1]["reason"] == "no_diff_found"
