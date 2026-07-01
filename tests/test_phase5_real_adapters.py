from pathlib import Path
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.agent.adapter_config import init_adapter_config, load_adapter_config
from uacos.agent.task import create_task
from uacos.agent.real_adapters import run_named_adapter, export_mcp_manifest

def test_phase5_adapter_config_and_manual_export(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def open_gate():\n    return 'GATE=UP OK'\n", encoding="utf-8")
    init_storage(repo)
    scan_repo(repo)

    cfg_path = init_adapter_config(repo)
    assert cfg_path.exists()
    cfg = load_adapter_config(repo)
    assert "manual_chat" in cfg["adapters"]
    assert cfg["adapters"]["openclaw_cli"]["dry_run"] is True

    task_file = create_task(
        repo,
        title="Fix open gate",
        objective="Fix open gate workflow safely",
        allowed_files=["app.py"],
        tests=["pytest -q"],
    )

    out = repo / "manual_context.md"
    result = run_named_adapter(repo, "manual_chat", task_file, output=out)
    assert result["status"] == "ok"
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "UACOS Agent Prompt" in text
    assert "Allowed Files" in text
    assert "app.py" in text

def test_phase5_cli_adapters_are_dry_run(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def ok():\n    return True\n", encoding="utf-8")
    init_storage(repo)
    scan_repo(repo)
    init_adapter_config(repo)
    task_file = create_task(repo, "Safe task", "Update ok safely", allowed_files=["app.py"], tests=["pytest -q"])

    openclaw = run_named_adapter(repo, "openclaw_cli", task_file)
    assert openclaw["status"] == "dry_run"
    assert "prompt_file" in openclaw
    assert "command" in openclaw

    aider = run_named_adapter(repo, "aider_cli", task_file)
    assert aider["status"] == "dry_run"
    assert "aider" in aider["command"]

    ollama = run_named_adapter(repo, "ollama_openai", task_file)
    assert ollama["status"] == "dry_run"
    assert "payload_preview" in ollama

def test_phase5_mcp_manifest_export(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    init_storage(repo)
    out = repo / ".uacos" / "mcp_manifest.json"
    result = export_mcp_manifest(repo, out)
    assert result["status"] == "ok"
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "uacos_search" in text
    assert "uacos_patch_check" in text
