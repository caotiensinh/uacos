from pathlib import Path
from uacos.ops.packaging import bootstrap
from uacos.memory.store import add_memory
from uacos.skill.store import add_skill
from uacos.compression.engine import build_summary_cache, project_summary, compressed_context, compression_report

def test_compression_engine_budget_and_report(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "db.py").write_text(
        "def save_user(user):\n    return True\n\n" +
        "\n".join([f"def helper_{i}(x):\n    return x + {i}\n" for i in range(15)]),
        encoding="utf-8",
    )
    (repo / "service.py").write_text("from db import save_user\n\nclass UserService:\n    def create_user(self, user):\n        return save_user(user)\n", encoding="utf-8")
    bootstrap(repo)
    add_memory(repo, "project_truth", "flow", "UserService.create_user calls save_user", tags=["user"])
    add_skill(repo, "Fix save bug", ["save_user"], "DB issue", ["inspect db.py"], [], category="debug", status="approved")
    cache = build_summary_cache(repo)
    assert cache["file_count"] >= 2
    ps = project_summary(repo)
    assert Path(ps["summary_file"]).exists()
    ctx = compressed_context(repo, "fix save_user create_user bug", max_tokens=4000, max_files=4)
    assert ctx["status"] == "ok"
    assert ctx["compressed_tokens_est"] <= 4000
    assert ctx["selected_file_count"] >= 1
    rep = compression_report(repo)
    assert rep["cache_file_count"] >= 2
