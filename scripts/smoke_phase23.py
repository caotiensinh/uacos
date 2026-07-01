from pathlib import Path
import tempfile, json, subprocess
from uacos.ide.vscode_pro import write_vscode_pro_extension, validate_vscode_pro_extension

def main():
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "vscode-uacos"
        result = write_vscode_pro_extension(out, overwrite=True)
        assert result["status"] == "ok"
        check = validate_vscode_pro_extension(out)
        assert check["status"] == "pass", check
        pkg = json.loads((out / "package.json").read_text(encoding="utf-8"))
        ids = [c["command"] for c in pkg["contributes"]["commands"]]
        assert "uacos.contextBudget" in ids
        assert "uacos.autopilotPlan" in ids
        assert "uacos.patch20Validate" in ids
        assert "uacos.providerHealth" in ids
        node = subprocess.run(["node", "scripts/check-extension.js"], cwd=out, capture_output=True, text=True)
        if node.returncode != 0:
            raise AssertionError(node.stderr or node.stdout)
        assert "EXTENSION_CHECK_OK" in node.stdout
        print("PHASE23_SMOKE_OK")
        print("commands=", len(ids))

if __name__ == "__main__":
    main()
