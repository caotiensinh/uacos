from pathlib import Path
import tempfile
from uacos.ops.packaging import bootstrap, health_check
from uacos.autopilot.orchestrator import autopilot_plan, autopilot_run, list_autopilot_runs

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "sample"
        repo.mkdir()
        (repo / "app.py").write_text("def open_gate():\n    return 'GATE=DOWN'\n", encoding="utf-8")
        (repo / "test_app.py").write_text("from app import open_gate\n\ndef test_open_gate():\n    assert open_gate() == 'GATE=UP'\n", encoding="utf-8")
        assert bootstrap(repo)["status"] == "ok"
        assert health_check(repo)["status"] == "pass"
        plan = autopilot_plan(repo, "Fix open gate", "Fix open_gate to return GATE=UP", allowed_files=["app.py"], tests=["python -m pytest -q"])
        task = Path(plan["task_file"])
        out = repo / "agent_response.md"
        out.write_text("```diff\ndiff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@ -1,2 +1,2 @@\n def open_gate():\n-    return 'GATE=DOWN'\n+    return 'GATE=UP'\n```\n", encoding="utf-8")
        run = autopilot_run(repo, task, agent_output=out, apply_changes=True, auto_learn=True)
        assert run["status"] == "done", run
        assert "GATE=UP" in (repo / "app.py").read_text(encoding="utf-8")
        assert list_autopilot_runs(repo)["count"] >= 1
        print("V2_E2E_OK")
        print("status=", run["status"])

if __name__ == "__main__":
    main()
