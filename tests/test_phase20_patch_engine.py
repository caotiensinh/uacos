from pathlib import Path
from uacos.patching.engine import parse_unified_diff, validate_patch, apply_patch, rollback_patch

def test_patch20_modify_new_delete_rename_and_rollback(tmp_path: Path):
    repo = tmp_path / "repo"
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
        "-OLD = True\n",
        encoding="utf-8",
    )
    parsed = parse_unified_diff(patch.read_text(encoding="utf-8"))
    assert len(parsed) == 3
    validation = validate_patch(repo, patch.read_text(encoding="utf-8"), allowed_files=["app.py", "newmod.py", "old.py"])
    assert validation["status"] == "pass"
    dry = apply_patch(repo, patch, allowed_files=["app.py", "newmod.py", "old.py"], dry_run=True)
    assert dry["status"] == "planned"
    applied = apply_patch(repo, patch, allowed_files=["app.py", "newmod.py", "old.py"], tests=["python -S -c \"import app, newmod; assert app.value()==42 and newmod.answer()==42\""])
    assert applied["status"] == "applied", applied
    assert "return 42" in (repo / "app.py").read_text(encoding="utf-8")
    assert (repo / "newmod.py").exists()
    assert not (repo / "old.py").exists()
    rb = rollback_patch(repo, applied)
    assert rb["status"] == "ok"
    assert "return 1" in (repo / "app.py").read_text(encoding="utf-8")
    assert not (repo / "newmod.py").exists()
    assert (repo / "old.py").exists()

def test_patch20_rejects_out_of_scope(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("x=1\n", encoding="utf-8")
    patch = repo / "bad.diff"
    patch.write_text(
        "diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@ -1 +1 @@\n-x=1\n+x=2\n",
        encoding="utf-8",
    )
    validation = validate_patch(repo, patch.read_text(encoding="utf-8"), allowed_files=["other.py"])
    assert validation["status"] == "fail"
