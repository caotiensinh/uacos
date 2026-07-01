from pathlib import Path
import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

from uacos.ops.packaging import bootstrap, health_check, backup_uacos, release_check
from uacos.memory.store import add_memory, search_memories
from uacos.memory.regression import add_regression_rule, regression_check_patch
from uacos.agent.task import create_task
from uacos.agent.registry import init_agent_registry, load_agents
from uacos.agent.adapter_config import init_adapter_config
from uacos.agent.real_adapters import run_named_adapter
from uacos.execution.artifacts import ingest_agent_output, evidence_report_v2
from uacos.execution.test_runner import run_task_tests
from uacos.execution.token_ledger import log_token_usage, ledger_summary
from uacos.apply.patch_apply import apply_patch_with_backup, done_gate
from uacos.dashboard.server import DashboardHandler


def test_v1_normal_user_workflow(tmp_path: Path):
    repo = tmp_path / "sample_project"
    repo.mkdir()

    # A realistic small project.
    (repo / "app.py").write_text(
        "def open_gate():\n"
        "    return 'GATE=DOWN'\n\n"
        "def barrier_status():\n"
        "    return 'OK'\n",
        encoding="utf-8",
    )
    (repo / "test_app.py").write_text(
        "from app import open_gate\n\n"
        "def test_open_gate():\n"
        "    assert open_gate() == 'GATE=UP'\n",
        encoding="utf-8",
    )

    # 1. Bootstrap like a normal user.
    boot = bootstrap(repo)
    assert boot["status"] == "ok"
    assert health_check(repo)["status"] == "pass"

    # 2. Add project truth and regression guard.
    mem = add_memory(
        repo,
        "project_truth",
        "barrier_open_contract",
        "open_gate must return GATE=UP when open command succeeds",
        tags=["barrier", "gate"],
        applies_to=["app.py"],
    )
    assert search_memories(repo, "barrier open")

    add_regression_rule(
        repo,
        title="Be careful touching app barrier logic",
        pattern="app.py",
        severity="medium",
        reason="core gate behavior",
    )

    # 3. Create task as user would.
    task_file = create_task(
        repo,
        title="Fix open gate result",
        objective="Fix open_gate to return GATE=UP and keep barrier_status unchanged",
        allowed_files=["app.py"],
        tests=["python -S -c \"import app; assert app.open_gate()=='GATE=UP'\""],
    )
    assert task_file.exists()

    # 4. Init agents/adapters.
    init_agent_registry(repo)
    init_adapter_config(repo)
    assert len(load_agents(repo)) >= 4

    # 5. Export manual context for cloud agents.
    manual_context = repo / "context_for_cloud_agent.md"
    export_result = run_named_adapter(repo, "manual_chat", task_file, output=manual_context)
    assert export_result["status"] == "ok"
    assert manual_context.exists()
    assert "Relevant Memory" in manual_context.read_text(encoding="utf-8")
    assert "barrier_open_contract" in manual_context.read_text(encoding="utf-8")

    # 6. Simulate an AI agent response with unified diff.
    agent_output = repo / "agent_response.md"
    agent_output.write_text(
        "I found the bug. Here is the patch:\n\n"
        "```diff\n"
        "diff --git a/app.py b/app.py\n"
        "--- a/app.py\n"
        "+++ b/app.py\n"
        "@@ -1,5 +1,5 @@\n"
        " def open_gate():\n"
        "-    return 'GATE=DOWN'\n"
        "+    return 'GATE=UP'\n"
        " \n"
        " def barrier_status():\n"
        "     return 'OK'\n"
        "```\n",
        encoding="utf-8",
    )

    # 7. Ingest output and verify patch gate.
    artifact = ingest_agent_output(repo, task_file, agent_output)
    assert artifact["status"] == "pass"
    assert artifact["has_diff"] is True

    diff_file = Path(artifact["diff_file"])
    reg = regression_check_patch(repo, diff_file)
    # Medium regression warning should not block.
    assert reg["status"] == "pass"
    assert reg["findings"]

    # 8. Apply patch safely, run tests, and done-gate.
    manifest = apply_patch_with_backup(repo, task_file, diff_file)
    assert manifest["status"] == "applied"
    assert "GATE=UP" in (repo / "app.py").read_text(encoding="utf-8")

    gate = done_gate(repo, Path(manifest["manifest_file"]))
    assert gate["status"] == "done"

    # 9. Record token/cost and evidence v2.
    log_token_usage(repo, task_id="TASK-E2E", agent="manual_chat", model="local", input_tokens=1500, output_tokens=350, context_id=export_result["context_id"])
    summary = ledger_summary(repo)
    assert summary["records"] >= 1

    test_result = run_task_tests(repo, task_file)
    assert test_result["status"] == "pass"

    evidence = evidence_report_v2(repo, task_file, agent_output, test_result, summary)
    assert "Final Status: PASS" in evidence

    # 10. Dashboard API smoke.
    handler_cls = type("E2EDashboardHandler", (DashboardHandler,), {"repo_root": repo})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
    port = server.server_address[1]
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/summary", timeout=5) as resp:
            dash = json.loads(resp.read().decode("utf-8"))
        assert dash["repo"] == str(repo)
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/search?q=open_gate", timeout=5) as resp:
            search = json.loads(resp.read().decode("utf-8"))
        assert search["results"]
    finally:
        server.shutdown()
        server.server_close()

    # 11. Backup/release check.
    backup = backup_uacos(repo, tmp_path / "uacos_backup.zip")
    assert Path(backup["backup"]).exists()
    rel = release_check(repo)
    assert rel["status"] in {"pass", "warn"}
