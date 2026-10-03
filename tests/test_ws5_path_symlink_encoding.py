from pathlib import Path

from uacos.patching.engine import apply_patch, validate_patch


def _modify_patch(path: str, old: str = "value = 1", new: str = "value = 2") -> str:
    return (
        f"diff --git a/{path} b/{path}\n"
        f"--- a/{path}\n"
        f"+++ b/{path}\n"
        "@@ -1 +1 @@\n"
        f"-{old}\n"
        f"+{new}\n"
    )


def test_validate_patch_rejects_symlink_target(tmp_path: Path):
    target = tmp_path / "real.py"
    target.write_text("value = 1\n", encoding="utf-8")
    link = tmp_path / "link.py"
    link.symlink_to(target)

    result = validate_patch(tmp_path, _modify_patch("link.py"), allowed_files=["link.py"])

    assert result["status"] == "fail"
    assert any(row["reason"] == "symlink_target" for row in result["findings"])
    assert target.read_text(encoding="utf-8") == "value = 1\n"


def test_validate_patch_rejects_non_utf8_modify_target(tmp_path: Path):
    target = tmp_path / "legacy.txt"
    original = b"caf\xe9\n"
    target.write_bytes(original)

    result = validate_patch(tmp_path, _modify_patch("legacy.txt", "caf\u00e9", "cafe"), allowed_files=["legacy.txt"])

    assert result["status"] == "fail"
    assert any(row["reason"] == "unsupported_text_encoding" for row in result["findings"])
    assert target.read_bytes() == original


def test_apply_patch_blocks_non_utf8_without_mutation(tmp_path: Path):
    target = tmp_path / "legacy.txt"
    original = b"\xff\xfelegacy\n"
    target.write_bytes(original)
    patch_file = tmp_path / "change.diff"
    patch_file.write_text(_modify_patch("legacy.txt", "legacy", "changed"), encoding="utf-8")

    result = apply_patch(tmp_path, patch_file, allowed_files=["legacy.txt"])

    assert result["status"] == "blocked"
    assert target.read_bytes() == original


def test_apply_patch_still_supports_utf8_text(tmp_path: Path):
    target = tmp_path / "app.py"
    target.write_text("value = 1\n", encoding="utf-8")
    patch_file = tmp_path / "change.diff"
    patch_file.write_text(_modify_patch("app.py"), encoding="utf-8")

    result = apply_patch(tmp_path, patch_file, allowed_files=["app.py"])

    assert result["status"] == "applied"
    assert target.read_text(encoding="utf-8") == "value = 2\n"
