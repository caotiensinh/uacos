from pathlib import Path
import tempfile
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.agent.registry import init_agent_registry
from uacos.agent.task import create_task
from uacos.agent.coordinator import run_workflow, evidence_markdown

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
        init_agent_registry(repo)
        task_file = create_task(
            repo,
            title="Coordinate barrier fix",
            objective="Fix barrier open workflow safely",
            allowed_files=["main.py"],
            tests=["pytest -q"],
        )
        run = run_workflow(repo, task_file)
        assert run["status"] == "pass"
        assert len(run["steps"]) >= 4
        md = evidence_markdown(run)
        assert "Evidence Report" in md
        print("PHASE4_SMOKE_OK")
        print("run_id=", run["id"])
        print("context_id=", run["context_id"])
        print("steps=", len(run["steps"]))

if __name__ == "__main__":
    main()
