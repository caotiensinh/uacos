from pathlib import Path
import tempfile
from uacos.storage import init_storage
from uacos.memory.store import add_memory
from uacos.skill.store import add_skill
from uacos.budget.optimizer import classify_task, update_summary_cache, build_budgeted_context, budget_report

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        (repo / "db.py").write_text("def save_user(user):\n    return True\n", encoding="utf-8")
        (repo / "service.py").write_text("from db import save_user\n\ndef create_user(user):\n    return save_user(user)\n", encoding="utf-8")
        init_storage(repo)
        add_memory(repo, "project_truth", "user_flow", "create_user calls save_user in db.py", tags=["user", "db"])
        add_skill(repo, "Fix user save flow", ["save_user error"], "DB save failure", ["Check db.py and service.py"], ["python -S -c \"import service\""], category="debug", status="approved")
        cls = classify_task("fix db save_user error")
        assert cls["size"] in {"tiny", "small", "medium", "large"}
        cache = update_summary_cache(repo)
        assert cache["file_count"] >= 2
        ctx = build_budgeted_context(repo, "fix db save_user error", profile="small")
        assert ctx["status"] == "ok"
        assert ctx["selected_file_count"] >= 1
        assert "db.py" in ctx["content"] or "service.py" in ctx["content"]
        rep = budget_report(repo)
        assert rep["status"] == "ok"
        print("PHASE22_SMOKE_OK")
        print("profile=", ctx["profile"])
        print("files=", ctx["selected_file_count"])
        print("tokens=", ctx["tokens_est"])

if __name__ == "__main__":
    main()
