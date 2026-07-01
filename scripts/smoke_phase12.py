from pathlib import Path
import tempfile, json
from uacos.ide.vscode import write_vscode_files, write_extension_skeleton

def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        repo = root / "repo"
        repo.mkdir()
        files = write_vscode_files(repo, dashboard_port=8765, overwrite=True)
        ext = write_extension_skeleton(root / "vscode-uacos", overwrite=True)
        tasks = json.loads((repo / ".vscode" / "tasks.json").read_text(encoding="utf-8"))
        assert files["status"] == "ok"
        assert ext["status"] == "ok"
        assert any(t["label"] == "UACOS: Health Check" for t in tasks["tasks"])
        print("PHASE12_SMOKE_OK")
        print("vscode_files=", len(files["files"]))
        print("extension_files=", len(ext["files"]))

if __name__ == "__main__":
    main()
