from pathlib import Path
import json
from uacos.ide.vscode import write_vscode_files, write_extension_skeleton, build_workspace_file

def test_phase12_vscode_files(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    result = write_vscode_files(repo, dashboard_port=9876, overwrite=True)
    assert result["status"] == "ok"
    tasks = json.loads((repo / ".vscode" / "tasks.json").read_text(encoding="utf-8"))
    labels = [t["label"] for t in tasks["tasks"]]
    assert "UACOS: Health Check" in labels
    assert "UACOS: Skill Review" in labels
    assert "9876" in (repo / ".vscode" / "tasks.json").read_text(encoding="utf-8")
    settings = json.loads((repo / ".vscode" / "settings.json").read_text(encoding="utf-8"))
    assert settings["uacos.dashboardPort"] == 9876
    launch = json.loads((repo / ".vscode" / "launch.json").read_text(encoding="utf-8"))
    assert launch["configurations"][0]["module"] == "uacos.cli"

def test_phase12_extension_skeleton_and_workspace(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    ext = tmp_path / "vscode-uacos"
    result = write_extension_skeleton(ext, overwrite=True)
    assert result["status"] == "ok"
    assert (ext / "package.json").exists()
    assert (ext / "extension.js").exists()
    package = json.loads((ext / "package.json").read_text(encoding="utf-8"))
    commands = [c["command"] for c in package["contributes"]["commands"]]
    assert "uacos.health" in commands
    assert "uacos.skillSuggest" in commands
    workspace = tmp_path / "project.code-workspace"
    ws = build_workspace_file(repo, workspace)
    assert ws["status"] == "ok"
    data = json.loads(workspace.read_text(encoding="utf-8"))
    assert data["folders"][0]["path"] == str(repo)
