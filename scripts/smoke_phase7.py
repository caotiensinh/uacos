from pathlib import Path
import tempfile
from uacos.storage import init_storage
from uacos.agent.task import create_task
from uacos.apply.patch_apply import apply_patch_with_backup, done_gate

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"; repo.mkdir()
        app = repo / "main.py"; app.write_text("def ok():\n    return False\n", encoding="utf-8")
        init_storage(repo)
        task_file = create_task(repo, "Fix ok", "Fix ok safely", allowed_files=["main.py"], tests=["python -c \"print('ok')\""])
        patch = repo / "change.diff"
        patch.write_text("diff --git a/main.py b/main.py\n--- a/main.py\n+++ b/main.py\n@@ -1,2 +1,2 @@\n def ok():\n-    return False\n+    return True\n", encoding="utf-8")
        manifest = apply_patch_with_backup(repo, task_file, patch)
        gate = done_gate(repo, Path(manifest["manifest_file"]))
        assert manifest["status"] == "applied"
        assert gate["status"] == "done"
        print("PHASE7_SMOKE_OK")
        print("manifest=", manifest["manifest_file"])
        print("done_gate=", gate["status"])

if __name__ == "__main__":
    main()
