from __future__ import annotations

from pathlib import Path
import json
from datetime import datetime, timezone

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def vscode_dir(repo_root: Path) -> Path:
    p = repo_root / ".vscode"
    p.mkdir(parents=True, exist_ok=True)
    return p

def build_tasks(dashboard_port: int = 8765) -> dict:
    repo = "${workspaceFolder}"
    return {
        "version": "2.0.0",
        "tasks": [
            {"label": "UACOS: Bootstrap", "type": "shell", "command": f"uacos bootstrap --repo \"{repo}\"", "problemMatcher": [], "group": "build"},
            {"label": "UACOS: Health Check", "type": "shell", "command": f"uacos health --repo \"{repo}\"", "problemMatcher": [], "group": "test"},
            {"label": "UACOS: Scan Repo", "type": "shell", "command": f"uacos scan --repo \"{repo}\"", "problemMatcher": [], "group": "build"},
            {"label": "UACOS: Open Dashboard", "type": "shell", "command": f"uacos dashboard --repo \"{repo}\" --host 127.0.0.1 --port {dashboard_port}", "problemMatcher": [], "isBackground": True},
            {"label": "UACOS: Ops Summary", "type": "shell", "command": f"uacos ops-summary --repo \"{repo}\"", "problemMatcher": []},
            {"label": "UACOS: Memory List", "type": "shell", "command": f"uacos memory-list --repo \"{repo}\"", "problemMatcher": []},
            {"label": "UACOS: Skill Review", "type": "shell", "command": f"uacos skill-review --repo \"{repo}\"", "problemMatcher": []},
            {"label": "UACOS: Manifest List", "type": "shell", "command": f"uacos manifest-list --repo \"{repo}\"", "problemMatcher": []}
        ]
    }

def build_settings(dashboard_port: int = 8765) -> dict:
    return {
        "uacos.enabled": True,
        "uacos.dashboardPort": dashboard_port,
        "uacos.defaultRepo": "${workspaceFolder}",
        "uacos.contextOutput": "${workspaceFolder}/.uacos/context_for_ai.md",
        "uacos.agentOutput": "${workspaceFolder}/agent_response.md",
        "uacos.diffOutput": "${workspaceFolder}/extracted.diff"
    }

def build_launch(dashboard_port: int = 8765) -> dict:
    return {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "UACOS: Dashboard",
                "type": "python",
                "request": "launch",
                "module": "uacos.cli",
                "args": ["dashboard", "--repo", "${workspaceFolder}", "--port", str(dashboard_port)],
                "console": "integratedTerminal"
            }
        ]
    }

def write_vscode_files(repo_root: Path, dashboard_port: int = 8765, overwrite: bool = False) -> dict:
    vd = vscode_dir(repo_root)
    specs = {
        "tasks.json": build_tasks(dashboard_port),
        "settings.json": build_settings(dashboard_port),
        "launch.json": build_launch(dashboard_port)
    }
    files = []
    for name, data in specs.items():
        path = vd / name
        if path.exists() and not overwrite:
            files.append({"path": str(path), "status": "exists_skipped"})
            continue
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        files.append({"path": str(path), "status": "written"})
    return {"status": "ok", "vscode_dir": str(vd), "files": files, "created_at": utcnow()}

def build_extension_package_json() -> dict:
    return {
        "name": "uacos-vscode",
        "displayName": "UACOS",
        "description": "Universal AI Context OS integration for VSCode",
        "version": "0.1.0",
        "engines": {"vscode": "^1.85.0"},
        "categories": ["Other"],
        "activationEvents": ["onCommand:uacos.health", "onCommand:uacos.scan", "onCommand:uacos.dashboard"],
        "main": "./extension.js",
        "contributes": {
            "commands": [
                {"command": "uacos.health", "title": "UACOS: Health Check"},
                {"command": "uacos.scan", "title": "UACOS: Scan Repo"},
                {"command": "uacos.dashboard", "title": "UACOS: Open Dashboard"},
                {"command": "uacos.context", "title": "UACOS: Build Context Pack"},
                {"command": "uacos.skillSuggest", "title": "UACOS: Suggest Skills"},
                {"command": "uacos.patchCheck", "title": "UACOS: Patch Check"}
            ],
            "configuration": {
                "title": "UACOS",
                "properties": {
                    "uacos.command": {"type": "string", "default": "uacos"},
                    "uacos.dashboardPort": {"type": "number", "default": 8765},
                    "uacos.contextOutput": {"type": "string", "default": ".uacos/context_for_ai.md"},
                    "uacos.agentOutput": {"type": "string", "default": "agent_response.md"},
                    "uacos.diffOutput": {"type": "string", "default": "extracted.diff"}
                }
            }
        },
        "scripts": {"package": "echo extension-skeleton-only"},
        "devDependencies": {}
    }

def build_extension_js() -> str:
    return """
const vscode = require('vscode');

function workspaceFolder() {
  const folders = vscode.workspace.workspaceFolders;
  if (!folders || folders.length === 0) {
    vscode.window.showErrorMessage('UACOS: open a workspace folder first.');
    return null;
  }
  return folders[0].uri.fsPath;
}

function cfg() {
  return vscode.workspace.getConfiguration('uacos');
}

function quote(s) {
  return '"' + String(s).replace(/"/g, '\\\\"') + '"';
}

function runInTerminal(name, args) {
  const repo = workspaceFolder();
  if (!repo) return;
  const cmd = cfg().get('command') || 'uacos';
  const terminal = vscode.window.createTerminal(name);
  terminal.show();
  terminal.sendText(cmd + ' ' + args.replace('{repo}', quote(repo)));
}

function activate(context) {
  context.subscriptions.push(vscode.commands.registerCommand('uacos.health', function () {
    runInTerminal('UACOS Health', 'health --repo {repo}');
  }));
  context.subscriptions.push(vscode.commands.registerCommand('uacos.scan', function () {
    runInTerminal('UACOS Scan', 'scan --repo {repo}');
  }));
  context.subscriptions.push(vscode.commands.registerCommand('uacos.dashboard', function () {
    const port = cfg().get('dashboardPort') || 8765;
    runInTerminal('UACOS Dashboard', 'dashboard --repo {repo} --host 127.0.0.1 --port ' + port);
    vscode.env.openExternal(vscode.Uri.parse('http://127.0.0.1:' + port + '/'));
  }));
  context.subscriptions.push(vscode.commands.registerCommand('uacos.context', async function () {
    const task = await vscode.window.showInputBox({ prompt: 'Task for UACOS context pack' });
    if (!task) return;
    runInTerminal('UACOS Context', 'context --repo {repo} --task ' + quote(task));
  }));
  context.subscriptions.push(vscode.commands.registerCommand('uacos.skillSuggest', async function () {
    const task = await vscode.window.showInputBox({ prompt: 'Task/error text for skill suggestion' });
    if (!task) return;
    runInTerminal('UACOS Skill Suggest', 'skill-suggest --repo {repo} --task ' + quote(task));
  }));
  context.subscriptions.push(vscode.commands.registerCommand('uacos.patchCheck', function () {
    const diffOutput = cfg().get('diffOutput') || 'extracted.diff';
    runInTerminal('UACOS Patch Check', 'patch-check --repo {repo} --patch ' + quote(diffOutput));
  }));
}
function deactivate() {}
module.exports = { activate, deactivate };
""".strip() + "\n"

def write_extension_skeleton(output_dir: Path, overwrite: bool = False) -> dict:
    if output_dir.exists() and any(output_dir.iterdir()) and not overwrite:
        return {"status": "exists_skipped", "output_dir": str(output_dir)}
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "package.json").write_text(json.dumps(build_extension_package_json(), ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "extension.js").write_text(build_extension_js(), encoding="utf-8")
    (output_dir / "README.md").write_text("# UACOS VSCode Extension Skeleton\n\nOpen this folder in VSCode and press F5 to run an Extension Development Host.\n", encoding="utf-8")
    return {"status": "ok", "output_dir": str(output_dir), "files": [str(output_dir / "package.json"), str(output_dir / "extension.js"), str(output_dir / "README.md")], "created_at": utcnow()}

def build_workspace_file(repo_root: Path, output: Path, dashboard_port: int = 8765) -> dict:
    data = {
        "folders": [{"path": str(repo_root)}],
        "settings": build_settings(dashboard_port),
        "extensions": {"recommendations": []}
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "ok", "workspace_file": str(output)}
