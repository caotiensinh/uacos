from pathlib import Path

from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.agent.task import create_task
from uacos.apply.patch_apply import apply_patch_with_backup, rollback_manifest, done_gate


def _write_two_file_repo(repo: Path):
    (repo / "a.py").write_text("def a():\n    return False\n", encoding="utf-8")
    (repo / "b.py").write_text("def b():\n    return False\n", encoding="utf-8")


def _two_file_patch(good_b: bool) -> str:
    b_line = "    return True\n" if good_b else "    return False\n"
    return (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -1,2 +1,2 @@\n"
        " def a():\n"
        "-    return False\n"
        "+    return True\n"
        "diff --git a/b.py b/b.py\n"
        "--- a/b.py\n"
        "+++ b/b.py\n"
        "@@ -1,2 +1,2 @@\n"
        " def b():\n"
        f"-    return False\n"
        f"+{b_line}"
    )


def test_multi_file_patch_applies_both_files(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_two_file_repo(repo)
    init_storage(repo)
    scan_repo(repo)
    task_file = create_task(repo, "Fix both", "Fix a and b safely", allowed_files=["a.py", "b.py"], tests=["python -c \"print('ok')\""])

    patch = repo / "change.diff"
    patch.write_text(_two_file_patch(good_b=True), encoding="utf-8")

    manifest = apply_patch_with_backup(repo, task_file, patch)
    assert manifest["status"] == "applied"
    assert "return True" in (repo / "a.py").read_text(encoding="utf-8")
    assert "return True" in (repo / "b.py").read_text(encoding="utf-8")
    assert done_gate(repo, Path(manifest["manifest_file"]))["status"] == "done"


def test_multi_file_patch_auto_rollback_restores_every_file(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_two_file_repo(repo)
    init_storage(repo)
    scan_repo(repo)
    # Tests fail regardless of patch content, forcing auto-rollback.
    task_file = create_task(repo, "Fix both fail test", "Fix a and b safely", allowed_files=["a.py", "b.py"], tests=["python -c \"import sys; sys.exit(1)\""])

    patch = repo / "change.diff"
    patch.write_text(_two_file_patch(good_b=True), encoding="utf-8")

    manifest = apply_patch_with_backup(repo, task_file, patch)
    assert manifest["status"] == "rolled_back"
    assert manifest["rolled_back"] is True
    # Both files must be restored to their original content, not just the first one.
    assert (repo / "a.py").read_text(encoding="utf-8") == "def a():\n    return False\n"
    assert (repo / "b.py").read_text(encoding="utf-8") == "def b():\n    return False\n"


def test_multi_file_patch_manual_rollback_restores_every_file(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_two_file_repo(repo)
    init_storage(repo)
    scan_repo(repo)
    task_file = create_task(repo, "Fix both", "Fix a and b safely", allowed_files=["a.py", "b.py"], tests=["python -c \"print('ok')\""])

    patch = repo / "change.diff"
    patch.write_text(_two_file_patch(good_b=True), encoding="utf-8")

    manifest = apply_patch_with_backup(repo, task_file, patch)
    assert manifest["status"] == "applied"

    rb = rollback_manifest(repo, Path(manifest["manifest_file"]))
    assert rb["rolled_back"] is True
    assert (repo / "a.py").read_text(encoding="utf-8") == "def a():\n    return False\n"
    assert (repo / "b.py").read_text(encoding="utf-8") == "def b():\n    return False\n"
