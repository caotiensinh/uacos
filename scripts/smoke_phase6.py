from pathlib import Path
import tempfile
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.agent.task import create_task
from uacos.execution.artifacts import ingest_agent_output, evidence_report_v2
from uacos.execution.test_runner import run_task_tests
from uacos.execution.token_ledger import log_token_usage, ledger_summary

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        (repo / "main.py").write_text("def ok():\n    return False\n", encoding="utf-8")
        init_storage(repo)
        scan_repo(repo)
        task_file = create_task(repo, "Fix ok", "Fix ok safely", allowed_files=["main.py"], tests=["python -c \"print('ok')\""])
        agent_output = repo / "agent.md"
        agent_output.write_text(
            "Patch:\n"
            "diff --git a/main.py b/main.py\n"
            "--- a/main.py\n"
            "+++ b/main.py\n"
            "@@ -1,2 +1,2 @@\n"
            " def ok():\n"
            "-    return False\n"
            "+    return True\n",
            encoding="utf-8",
        )
        artifact = ingest_agent_output(repo, task_file, agent_output)
        tests = run_task_tests(repo, task_file)
        log_token_usage(repo, "TASK-SMOKE", "coder", "local", 1200, 300, "CTX-SMOKE")
        summary = ledger_summary(repo)
        md = evidence_report_v2(repo, task_file, agent_output, tests, summary)
        assert artifact["status"] == "pass"
        assert tests["status"] == "pass"
        assert "Final Status: PASS" in md
        print("PHASE6_SMOKE_OK")
        print("artifact_status=", artifact["status"])
        print("test_status=", tests["status"])
        print("token_records=", summary["records"])

if __name__ == "__main__":
    main()
