from pathlib import Path

from uacos.patching.preconditions import capture_patch_preconditions, verify_patch_preconditions


MODIFY_PATCH = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1 +1 @@
-VALUE = 1
+VALUE = 2
"""

NEW_PATCH = """diff --git a/new.py b/new.py
new file mode 100644
--- /dev/null
+++ b/new.py
@@ -0,0 +1 @@
+VALUE = 1
"""


def test_unchanged_source_precondition_passes(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("VALUE = 1\n", encoding="utf-8")

    snapshot = capture_patch_preconditions(repo, MODIFY_PATCH)
    result = verify_patch_preconditions(repo, snapshot)

    assert snapshot["status"] == "pass"
    assert result == {"status": "pass", "stale": False, "findings": []}


def test_modified_source_is_detected_as_stale(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "app.py"
    target.write_text("VALUE = 1\n", encoding="utf-8")

    snapshot = capture_patch_preconditions(repo, MODIFY_PATCH)
    target.write_text("VALUE = 99\n", encoding="utf-8")
    result = verify_patch_preconditions(repo, snapshot)

    assert result["status"] == "fail"
    assert result["stale"] is True
    assert result["findings"][0]["reason"] == "stale_source_modified"
    assert result["findings"][0]["expected_sha256"] != result["findings"][0]["actual_sha256"]


def test_deleted_source_is_detected_as_stale(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "app.py"
    target.write_text("VALUE = 1\n", encoding="utf-8")

    snapshot = capture_patch_preconditions(repo, MODIFY_PATCH)
    target.unlink()
    result = verify_patch_preconditions(repo, snapshot)

    assert result["status"] == "fail"
    assert result["findings"][0]["reason"] == "stale_source_missing"


def test_new_file_target_must_remain_absent(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    snapshot = capture_patch_preconditions(repo, NEW_PATCH)
    (repo / "new.py").write_text("raced = True\n", encoding="utf-8")
    result = verify_patch_preconditions(repo, snapshot)

    assert result["status"] == "fail"
    assert result["findings"][0] == {"path": "new.py", "reason": "stale_target_created"}


def test_symlink_precondition_fails_closed(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "app.py").symlink_to(outside)

    snapshot = capture_patch_preconditions(repo, MODIFY_PATCH)

    assert snapshot["status"] == "fail"
    assert snapshot["findings"][0]["reason"] == "precondition_capture_symlink"
