from pathlib import Path
import tempfile
from uacos.patching.engine import parse_unified_diff, validate_patch, apply_patch, rollback_patch

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
        (repo / "old.py").write_text("OLD = True\n", encoding="utf-8")
        patch = repo / "change.diff"
        patch.write_text(
            "diff --git a/app.py b/app.py\n"
            "--- a/app.py\n"
            "+++ b/app.py\n"
            "@@ -1,2 +1,2 @@\n"
            " def value():\n"
            "-    return 1\n"
            "+    return 42\n"
            "diff --git a/newmod.py b/newmod.py\n"
            "new file mode 100644\n"
            "--- /dev/null\n"
            "+++ b/newmod.py\n"
            "@@ -0,0 +1,2 @@\n"
            "+def answer():\n"
            "+    return 42\n"
            "diff --git a/old.py b/old.py\n"
            "deleted file mode 100644\n"
            "--- a/old.py\n"
            "+++ /dev/null\n"
            "@@ -1 +0,0 @@\n"
            "-OLD = True\n"
            "diff --git a/app.py b/app_renamed.py\n"
            "similarity index 100%\n"
            "rename from app.py\n"
            "rename to app_renamed.py\n",
            encoding="utf-8",
        )
        parsed = parse_unified_diff(patch.read_text())
        assert len(parsed) == 4
        val = validate_patch(repo, patch.read_text(), allowed_files=["app.py", "app_renamed.py", "newmod.py", "old.py"])
        assert val["status"] == "pass", val
        dry = apply_patch(repo, patch, allowed_files=["app.py", "app_renamed.py", "newmod.py", "old.py"], dry_run=True)
        assert dry["status"] == "planned"
        result = apply_patch(repo, patch, allowed_files=["app.py", "app_renamed.py", "newmod.py", "old.py"], tests=["python -S -c \"import app_renamed, newmod; assert app_renamed.value()==42 and newmod.answer()==42\""])
        assert result["status"] == "applied", result
        assert (repo / "app_renamed.py").exists()
        assert not (repo / "app.py").exists()
        assert (repo / "newmod.py").exists()
        assert not (repo / "old.py").exists()
        rb = rollback_patch(repo, result)
        assert rb["status"] == "ok"
        assert (repo / "app.py").exists()
        assert not (repo / "newmod.py").exists()
        assert (repo / "old.py").exists()
        print("PHASE20_SMOKE_OK")
        print("files=", len(parsed))
        print("status=", result["status"])

if __name__ == "__main__":
    main()
