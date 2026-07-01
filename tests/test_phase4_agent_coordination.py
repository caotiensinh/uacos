from pathlib import Path
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.agent.registry import init_agent_registry, load_agents
from uacos.agent.task import create_task
from uacos.agent.coordinator import create_plan, run_workflow, evidence_markdown

def test_phase4_agent_registry_task_plan_run(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def open_gate():\n    return 'GATE=UP OK'\n", encoding="utf-8")
    init_storage(repo)
    scan_repo(repo)

    reg = init_agent_registry(repo)
    assert reg.exists()
    agents = load_agents(repo)
    assert len(agents) >= 4
    assert any(a["role"] == "coder" for a in agents)

    task_file = create_task(
        repo,
        title="Fix open gate",
        objective="Fix open gate button and keep scope safe",
        allowed_files=["app.py"],
        tests=["pytest -q"],
    )
    assert task_file.exists()

    plan_file = create_plan(repo, task_file)
    assert plan_file.exists()

    result = run_workflow(repo, task_file)
    assert result["status"] == "pass"
    assert result["context_id"]
    assert result["context_token_count"] > 0
    assert len(result["steps"]) >= 4

    report = evidence_markdown(result)
    assert "Evidence Report" in report
    assert "Fix open gate" in report

def test_phase4_workflow_blocks_bad_command(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def ok():\n    return True\n", encoding="utf-8")
    init_storage(repo)
    scan_repo(repo)
    init_agent_registry(repo)

    task_file = create_task(
        repo,
        title="Bad command",
        objective="Try dangerous command",
        allowed_files=["app.py"],
        tests=["rm -rf /"],
    )

    result = run_workflow(repo, task_file)
    assert result["status"] == "fail"
    assert result["preflight"]["status"] == "fail"
    assert result["preflight"]["findings"][0]["type"] == "command_blocked"
