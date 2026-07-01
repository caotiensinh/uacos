from pathlib import Path
import tempfile
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.agent.adapter_config import init_adapter_config
from uacos.agent.task import create_task
from uacos.agent.real_adapters import run_named_adapter, export_mcp_manifest

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        (repo / "main.py").write_text(
            "class BarrierService:\n"
            "    def open_gate(self):\n"
            "        return 'GATE=UP OK'\n",
            encoding="utf-8",
        )
        init_storage(repo)
        scan_repo(repo)
        init_adapter_config(repo)
        task_file = create_task(
            repo,
            title="Adapter barrier task",
            objective="Fix barrier open adapter workflow safely",
            allowed_files=["main.py"],
            tests=["pytest -q"],
        )
        manual_out = repo / "context_for_chatgpt_claude.md"
        manual = run_named_adapter(repo, "manual_chat", task_file, output=manual_out)
        openclaw = run_named_adapter(repo, "openclaw_cli", task_file)
        ollama = run_named_adapter(repo, "ollama_openai", task_file)
        mcp = export_mcp_manifest(repo, repo / ".uacos" / "mcp_manifest.json")

        assert manual["status"] == "ok"
        assert manual_out.exists()
        assert openclaw["status"] == "dry_run"
        assert ollama["status"] == "dry_run"
        assert mcp["status"] == "ok"

        print("PHASE5_SMOKE_OK")
        print("manual_context=", manual["output"])
        print("openclaw_status=", openclaw["status"])
        print("ollama_status=", ollama["status"])
        print("mcp_manifest=", mcp["output"])

if __name__ == "__main__":
    main()
