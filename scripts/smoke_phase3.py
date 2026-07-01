from pathlib import Path
import tempfile
from uacos.security.secret_scan import security_scan
from uacos.security.command_policy import check_command
from uacos.security.patch_gate import validate_patch_text

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        (repo / "main.py").write_text("def ok():\n    return True\n", encoding="utf-8")
        (repo / ".env").write_text("SECRET=abc", encoding="utf-8")

        scan = security_scan(repo)
        assert scan["status"] == "fail"
        assert check_command("pytest -q")["allowed"] is True
        assert check_command("rm -rf /")["allowed"] is False

        patch = "diff --git a/main.py b/main.py\n--- a/main.py\n+++ b/main.py\n@@ -1,2 +1,3 @@\n def ok():\n+    value = True\n     return True\n"
        result = validate_patch_text(patch, allowed_files=["main.py"])
        assert result["status"] == "pass"

        print("PHASE3_SMOKE_OK")
        print("security_findings=", scan["findings_count"])
        print("patch_status=", result["status"])

if __name__ == "__main__":
    main()
