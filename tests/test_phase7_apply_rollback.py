from pathlib import Path
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.agent.task import create_task
from uacos.apply.patch_apply import apply_patch_with_backup, rollback_manifest, done_gate, list_manifests

def test_phase7_apply_patch_done_and_manual_rollback(tmp_path: Path):
    repo = tmp_path / "repo"; repo.mkdir()
    app = repo / "app.py"; app.write_text("def ok():\n    return False\n", encoding="utf-8")
    init_storage(repo); scan_repo(repo)
    task_file = create_task(repo, "Fix ok", "Fix ok safely", allowed_files=["app.py"], tests=["python -c \"print('ok')\""])
    patch = repo / "change.diff"
    patch.write_text("diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@ -1,2 +1,2 @@\n def ok():\n-    return False\n+    return True\n", encoding="utf-8")
    manifest = apply_patch_with_backup(repo, task_file, patch)
    assert manifest["status"] == "applied"
    assert "return True" in app.read_text(encoding="utf-8")
    assert done_gate(repo, Path(manifest["manifest_file"]))["status"] == "done"
    assert list_manifests(repo)["count"] >= 1
    rb = rollback_manifest(repo, Path(manifest["manifest_file"]))
    assert rb["rolled_back"] is True
    assert "return False" in app.read_text(encoding="utf-8")

def test_phase7_auto_rollback_on_test_fail(tmp_path: Path):
    repo = tmp_path / "repo"; repo.mkdir()
    app = repo / "app.py"; app.write_text("def ok():\n    return False\n", encoding="utf-8")
    init_storage(repo)
    task_file = create_task(repo, "Fix ok fail test", "Fix ok safely", allowed_files=["app.py"], tests=["python -c \"import sys; sys.exit(1)\""])
    patch = repo / "change.diff"
    patch.write_text("diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@ -1,2 +1,2 @@\n def ok():\n-    return False\n+    return True\n", encoding="utf-8")
    manifest = apply_patch_with_backup(repo, task_file, patch)
    assert manifest["status"] == "rolled_back"
    assert manifest["rolled_back"] is True
    assert "return False" in app.read_text(encoding="utf-8")
    assert done_gate(repo, Path(manifest["manifest_file"]))["status"] == "not_done"

def test_phase7_blocks_out_of_scope_patch(tmp_path: Path):
    repo = tmp_path / "repo"; repo.mkdir()
    (repo / "app.py").write_text("a = 1\n", encoding="utf-8")
    (repo / "other.py").write_text("b = 1\n", encoding="utf-8")
    init_storage(repo)
    task_file = create_task(repo, "Scope", "Only app", allowed_files=["app.py"], tests=[])
    patch = repo / "bad.diff"
    patch.write_text("diff --git a/other.py b/other.py\n--- a/other.py\n+++ b/other.py\n@@ -1 +1 @@\n-b = 1\n+b = 2\n", encoding="utf-8")
    result = apply_patch_with_backup(repo, task_file, patch)
    assert result["status"] == "blocked"
    assert result["reason"] == "patch_check_failed"
