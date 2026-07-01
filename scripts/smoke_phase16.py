from pathlib import Path
import tempfile
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.llm.providers import init_llm_config, run_llm
from uacos.compression.context import compress_context
from uacos.agent.task import create_task
from uacos.apply.patch_apply import apply_patch_with_backup, done_gate

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        (repo / "app.py").write_text("def ok():\n    return True\n", encoding="utf-8")
        init_storage(repo)
        scan_repo(repo)
        assert init_llm_config(repo)["status"] == "ok"
        llm = run_llm(repo, "hello", provider="dry_run")
        assert llm["status"] == "dry_run"
        comp = compress_context(repo, "ok function", max_files=5)
        assert comp["status"] == "ok"
        assert "app.py" in comp["content"]

        task = create_task(repo, "Create util", "Create util file", allowed_files=["utils.py"], tests=["python -S -c \"import utils; assert utils.answer()==42\""])
        patch = repo / "new.diff"
        patch.write_text(
            "diff --git a/utils.py b/utils.py\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            "+++ b/utils.py\n"
            "@@ -0,0 +1,2 @@\n"
            "+def answer():\n"
            "+    return 42\n",
            encoding="utf-8",
        )
        manifest = apply_patch_with_backup(repo, task, patch)
        assert manifest["status"] == "applied", manifest
        assert (repo / "utils.py").exists()
        gate = done_gate(repo, Path(manifest["manifest_file"]))
        assert gate["status"] == "done", gate
        print("PHASE16_SMOKE_OK")
        print("llm=", llm["status"])
        print("new_file=", (repo / "utils.py").exists())

if __name__ == "__main__":
    main()
