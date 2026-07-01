from pathlib import Path
import tempfile
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.memory.store import add_memory, search_memories, memory_summary_for_task
from uacos.memory.regression import add_regression_rule, regression_check_patch
from uacos.retrieval.context_pack import build_context_pack

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"; repo.mkdir()
        (repo / "barrier.py").write_text("def open_gate():\n    return True\n", encoding="utf-8")
        init_storage(repo); scan_repo(repo)
        add_memory(repo, "project_truth", "barrier_safety", "Lower barrier must obey safe ROI", tags=["barrier", "safety"])
        add_regression_rule(repo, "Do not break barrier safety", "barrier.py", severity="high")
        found = search_memories(repo, "barrier safety")
        pack = build_context_pack(repo, "fix barrier safety", max_tokens=3000)
        patch = repo / "change.diff"
        patch.write_text("diff --git a/barrier.py b/barrier.py\n--- a/barrier.py\n+++ b/barrier.py\n@@ -1 +1 @@\n-def open_gate():\n+def open_gate():\n", encoding="utf-8")
        reg = regression_check_patch(repo, patch)
        assert found
        assert "Lower barrier must obey safe ROI" in pack["content"]
        assert reg["status"] == "fail"
        print("PHASE8_SMOKE_OK")
        print("memories=", len(found))
        print("regression_status=", reg["status"])

if __name__ == "__main__":
    main()
