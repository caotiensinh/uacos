from pathlib import Path
from uacos.security.secret_scan import security_scan
from uacos.security.command_policy import check_command
from uacos.security.patch_gate import validate_patch_text

def test_security_scan_detects_secret_like_content(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("API_KEY = 'abcdefghijklmnopqrstuvwxyz123456'\ndef ok():\n    return True\n", encoding="utf-8")
    (repo / ".env").write_text("SECRET=abc", encoding="utf-8")
    result = security_scan(repo)
    assert result["status"] == "fail"
    assert result["findings_count"] >= 2

def test_command_policy_allows_safe_blocks_dangerous():
    assert check_command("pytest -q")["allowed"] is True
    assert check_command("python -m pytest")["allowed"] is True
    assert check_command("git diff")["allowed"] is True
    assert check_command("git reset --hard")["allowed"] is False
    assert check_command("rm -rf /")["allowed"] is False

def test_patch_gate_scope_and_secret_detection():
    patch = "diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@ -1,2 +1,3 @@\n def ok():\n+    API_KEY = \"abcdefghijklmnopqrstuvwxyz123456\"\n     return True\n"
    result = validate_patch_text(patch, allowed_files=["app.py"])
    assert result["status"] == "fail"
    assert any(f["type"] == "secret_in_added_lines" for f in result["findings"])

    out_of_scope_patch = "diff --git a/other.py b/other.py\n--- a/other.py\n+++ b/other.py\n@@ -1 +1 @@\n-a = 1\n+a = 2\n"
    result2 = validate_patch_text(out_of_scope_patch, allowed_files=["app.py"])
    assert result2["status"] == "fail"
    assert any(f["type"] == "scope_violation" for f in result2["findings"])

    safe_patch = "diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@ -1 +1,2 @@\n def ok():\n+    return True\n"
    result3 = validate_patch_text(safe_patch, allowed_files=["app.py"])
    assert result3["status"] == "pass"
