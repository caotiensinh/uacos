
from pathlib import Path
import tempfile
from uacos.ops.packaging import bootstrap
from uacos.memory.store import add_memory
from uacos.skill.store import add_skill
from uacos.compression.engine import build_summary_cache, project_summary, compressed_context, compression_report

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        # Use enough code to test actual compression behavior.
        (repo / "db.py").write_text(
            "def save_user(user):\n"
            "    # save user to database\n"
            "    return True\n\n" +
            "\n".join([f"def helper_{i}(x):\n    return x + {i}\n" for i in range(20)]),
            encoding="utf-8",
        )
        (repo / "service.py").write_text(
            "from db import save_user\n\n"
            "class UserService:\n"
            "    def create_user(self, user):\n"
            "        return save_user(user)\n\n" +
            "\n".join([f"    def method_{i}(self, x):\n        return x\n" for i in range(20)]),
            encoding="utf-8",
        )
        (repo / "README.md").write_text("# Demo\n\nThis project handles users.\n", encoding="utf-8")
        bootstrap(repo)
        add_memory(repo, "project_truth", "user_flow", "UserService.create_user calls save_user", tags=["user"])
        add_skill(repo, "Fix user save bug", ["save_user", "create_user"], "DB save issue", ["Inspect db.py and service.py"], ["python -S -c \"import service\""], category="debug", status="approved")
        cache = build_summary_cache(repo)
        assert cache["file_count"] >= 3
        assert cache["summary_tokens_est"] > 0
        ps = project_summary(repo)
        assert Path(ps["summary_file"]).exists()
        ctx = compressed_context(repo, "fix save_user create_user bug", max_tokens=4000, max_files=5)
        assert ctx["status"] == "ok"
        assert ctx["selected_file_count"] >= 1
        assert ctx["compressed_tokens_est"] <= 4000
        assert "db.py" in ctx["content"] or "service.py" in ctx["content"]
        rep = compression_report(repo)
        assert rep["cache_file_count"] >= 3
        print("PHASE26_SMOKE_OK")
        print("files=", cache["file_count"])
        print("cache_ratio=", cache["compression_ratio"])
        print("context_tokens=", ctx["compressed_tokens_est"])

if __name__ == "__main__":
    main()
