from pathlib import Path
from uacos.ops.packaging import bootstrap
from uacos.memory.store import add_memory
from uacos.budget.optimizer import classify_task, update_summary_cache, build_budgeted_context, budget_report

def test_budget_optimizer_builds_budgeted_context(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "db.py").write_text("def save_user(user):\n    return True\n", encoding="utf-8")
    (repo / "service.py").write_text("from db import save_user\n\ndef create_user(user):\n    return save_user(user)\n", encoding="utf-8")
    bootstrap(repo)
    add_memory(repo, "project_truth", "flow", "create_user calls save_user", tags=["user"])
    cls = classify_task("fix db save_user error")
    assert cls["size"] in {"tiny", "small", "medium", "large"}
    cache = update_summary_cache(repo)
    assert cache["file_count"] >= 2
    ctx = build_budgeted_context(repo, "fix db save_user error", profile="small", max_tokens=4500)
    assert ctx["status"] == "ok"
    assert ctx["tokens_est"] <= 4500
    assert ctx["selected_file_count"] >= 1
    assert "db.py" in ctx["content"] or "service.py" in ctx["content"]
    rep = budget_report(repo)
    assert rep["status"] == "ok"
