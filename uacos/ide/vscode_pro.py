from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json

EXTENSION_JS = 'const vscode = require(\'vscode\');\nconst cp = require(\'child_process\');\n\nfunction workspaceFolder() {\n  const folders = vscode.workspace.workspaceFolders;\n  if (!folders || folders.length === 0) {\n    vscode.window.showErrorMessage(\'UACOS: open a workspace folder first.\');\n    return null;\n  }\n  return folders[0].uri.fsPath;\n}\n\nfunction cfg() {\n  return vscode.workspace.getConfiguration(\'uacos\');\n}\n\nfunction quote(s) {\n  return \'"\' + String(s).replace(/"/g, \'\\\\"\') + \'"\';\n}\n\nfunction cli() {\n  return cfg().get(\'command\') || \'uacos\';\n}\n\nfunction runTerminal(name, args) {\n  const repo = workspaceFolder();\n  if (!repo) return;\n  const terminal = vscode.window.createTerminal(name);\n  terminal.show();\n  terminal.sendText(cli() + \' \' + args.replaceAll(\'{repo}\', quote(repo)));\n}\n\nfunction runCapture(args, cb) {\n  const repo = workspaceFolder();\n  if (!repo) return;\n  const cmd = cli() + \' \' + args.replaceAll(\'{repo}\', quote(repo));\n  cp.exec(cmd, {cwd: repo, maxBuffer: 1024 * 1024 * 8}, (err, stdout, stderr) => {\n    cb(err, stdout, stderr, cmd);\n  });\n}\n\nasync function askTask(prompt) {\n  return await vscode.window.showInputBox({prompt: prompt || \'UACOS task/objective\'});\n}\n\nfunction statusPanel(context) {\n  const panel = vscode.window.createWebviewPanel(\'uacosStatus\', \'UACOS Status\', vscode.ViewColumn.One, {enableScripts: false});\n  panel.webview.html = \'<html><body><h2>UACOS Status</h2><p>Loading...</p></body></html>\';\n  runCapture(\'health --repo {repo}\', (err, stdout, stderr, cmd) => {\n    const safe = (stdout || stderr || String(err || \'\')).replace(/[<>&]/g, c => ({\'<\':\'&lt;\',\'>\':\'&gt;\',\'&\':\'&amp;\'}[c]));\n    panel.webview.html = \'<html><body><h2>UACOS Status</h2><pre>\' + safe + \'</pre><p><code>\' + cmd + \'</code></p></body></html>\';\n  });\n}\n\nfunction activate(context) {\n  const reg = (name, fn) => context.subscriptions.push(vscode.commands.registerCommand(name, fn));\n\n  reg(\'uacos.bootstrap\', () => runTerminal(\'UACOS Bootstrap\', \'bootstrap --repo {repo}\'));\n  reg(\'uacos.health\', () => runTerminal(\'UACOS Health\', \'health --repo {repo}\'));\n  reg(\'uacos.scan\', () => runTerminal(\'UACOS Scan\', \'scan --repo {repo}\'));\n  reg(\'uacos.astScan\', () => runTerminal(\'UACOS AST Scan\', \'ast-scan --repo {repo}\'));\n  reg(\'uacos.semanticIndex\', () => runTerminal(\'UACOS Semantic Index\', \'semantic-index --repo {repo}\'));\n  reg(\'uacos.skillReview\', () => runTerminal(\'UACOS Skill Review\', \'skill-review --repo {repo}\'));\n  reg(\'uacos.providerHealth\', () => runTerminal(\'UACOS Provider Health\', \'provider-health --repo {repo}\'));\n  reg(\'uacos.autopilotStatus\', () => runTerminal(\'UACOS Autopilot Status\', \'autopilot-status --repo {repo}\'));\n\n  reg(\'uacos.contextBudget\', async () => {\n    const task = await askTask(\'Task for budgeted context\');\n    if (!task) return;\n    const profile = cfg().get(\'contextProfile\') || \'medium\';\n    runTerminal(\'UACOS Context Budget\', \'context-budget --repo {repo} --task \' + quote(task) + \' --profile \' + quote(profile));\n  });\n\n  reg(\'uacos.contextSmart\', async () => {\n    const task = await askTask(\'Task for smart context\');\n    if (!task) return;\n    runTerminal(\'UACOS Smart Context\', \'context-smart --repo {repo} --task \' + quote(task));\n  });\n\n  reg(\'uacos.feedbackRecommend\', async () => {\n    const task = await askTask(\'Task for skill recommendation\');\n    if (!task) return;\n    runTerminal(\'UACOS Feedback Recommend\', \'feedback-recommend --repo {repo} --task \' + quote(task));\n  });\n\n  reg(\'uacos.autopilotPlan\', async () => {\n    const title = await vscode.window.showInputBox({prompt: \'Autopilot task title\'});\n    if (!title) return;\n    const objective = await vscode.window.showInputBox({prompt: \'Autopilot objective\'});\n    if (!objective) return;\n    runTerminal(\'UACOS Autopilot Plan\', \'autopilot-plan --repo {repo} --title \' + quote(title) + \' --objective \' + quote(objective));\n  });\n\n  reg(\'uacos.patch20Validate\', async () => {\n    const patch = cfg().get(\'patchFile\') || \'change.diff\';\n    runTerminal(\'UACOS Patch20 Validate\', \'patch20-validate --repo {repo} --patch \' + quote(patch));\n  });\n\n  reg(\'uacos.openStatusPanel\', () => statusPanel(context));\n}\n\nfunction deactivate() {}\n\nmodule.exports = { activate, deactivate };\n'
CHECK_JS = "const fs = require('fs');\n\nfunction fail(msg) {\n  console.error('FAIL:', msg);\n  process.exit(1);\n}\n\nfor (const f of ['package.json', 'extension.js', 'README.md']) {\n  if (!fs.existsSync(f)) fail('missing ' + f);\n}\n\nconst pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));\nif (!pkg.contributes || !pkg.contributes.commands || pkg.contributes.commands.length < 10) {\n  fail('not enough commands');\n}\nconst ext = fs.readFileSync('extension.js', 'utf8');\nfor (const key of ['context-budget', 'context-smart', 'autopilot-plan', 'patch20-validate', 'provider-health']) {\n  if (!ext.includes(key)) fail('extension missing ' + key);\n}\nconsole.log('EXTENSION_CHECK_OK');\n"

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def extension_package() -> dict:
    commands = [
        ("uacos.bootstrap", "UACOS: Bootstrap Repo"),
        ("uacos.health", "UACOS: Health Check"),
        ("uacos.scan", "UACOS: Scan Repo"),
        ("uacos.contextBudget", "UACOS: Build Budgeted Context"),
        ("uacos.contextSmart", "UACOS: Build Smart Context"),
        ("uacos.astScan", "UACOS: AST Scan / Graph Build"),
        ("uacos.semanticIndex", "UACOS: Semantic Index"),
        ("uacos.skillReview", "UACOS: Skill Review"),
        ("uacos.feedbackRecommend", "UACOS: Feedback Recommend Skill"),
        ("uacos.providerHealth", "UACOS: Provider Health"),
        ("uacos.autopilotPlan", "UACOS: Autopilot Plan"),
        ("uacos.autopilotStatus", "UACOS: Autopilot Status"),
        ("uacos.patch20Validate", "UACOS: Patch20 Validate"),
        ("uacos.openStatusPanel", "UACOS: Open Status Panel"),
    ]
    return {
        "name": "uacos-vscode",
        "displayName": "UACOS",
        "description": "Universal AI Context OS integration for VSCode",
        "version": "0.2.0",
        "publisher": "uacos-local",
        "engines": {"vscode": "^1.85.0"},
        "categories": ["Other"],
        "activationEvents": [f"onCommand:{c[0]}" for c in commands],
        "main": "./extension.js",
        "contributes": {
            "commands": [{"command": c, "title": t} for c, t in commands],
            "configuration": {
                "title": "UACOS",
                "properties": {
                    "uacos.command": {"type": "string", "default": "uacos"},
                    "uacos.defaultRepo": {"type": "string", "default": "${workspaceFolder}"},
                    "uacos.dashboardPort": {"type": "number", "default": 8765},
                    "uacos.contextProfile": {"type": "string", "default": "medium"},
                    "uacos.agentOutput": {"type": "string", "default": "agent_response.md"},
                    "uacos.patchFile": {"type": "string", "default": "change.diff"}
                }
            },
            "menus": {
                "commandPalette": [{"command": c} for c, _ in commands]
            }
        },
        "scripts": {
            "check": "node ./scripts/check-extension.js",
            "package": "echo package-with-vsce-if-needed"
        },
        "devDependencies": {}
    }

def extension_readme() -> str:
    return """# UACOS VSCode Extension

Generated by UACOS Phase 23.

## Commands

Bootstrap, health, scan, context-budget, context-smart, AST graph, semantic index, skill review,
feedback recommendation, provider health, autopilot plan/status, patch validation, and status panel.

## Check

```bash
node scripts/check-extension.js
```
"""

def write_vscode_pro_extension(output_dir: Path, overwrite: bool = False) -> dict:
    if output_dir.exists() and any(output_dir.iterdir()) and not overwrite:
        return {"status": "exists_skipped", "output_dir": str(output_dir)}
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "scripts").mkdir(exist_ok=True)
    (output_dir / "package.json").write_text(json.dumps(extension_package(), ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "extension.js").write_text(EXTENSION_JS, encoding="utf-8")
    (output_dir / "README.md").write_text(extension_readme(), encoding="utf-8")
    (output_dir / "scripts" / "check-extension.js").write_text(CHECK_JS, encoding="utf-8")
    (output_dir / ".vscode").mkdir(exist_ok=True)
    (output_dir / ".vscode" / "launch.json").write_text(json.dumps({
        "version": "0.2.0",
        "configurations": [{
            "name": "Run UACOS Extension",
            "type": "extensionHost",
            "request": "launch",
            "args": ["--extensionDevelopmentPath=${workspaceFolder}"]
        }]
    }, indent=2), encoding="utf-8")
    return {"status": "ok", "output_dir": str(output_dir), "files": [str(p) for p in output_dir.rglob("*") if p.is_file()], "created_at": utcnow()}

def validate_vscode_pro_extension(output_dir: Path) -> dict:
    required = ["package.json", "extension.js", "README.md", "scripts/check-extension.js"]
    findings = []
    for rel in required:
        if not (output_dir / rel).exists():
            findings.append({"severity": "error", "reason": "missing_file", "file": rel})
    if (output_dir / "package.json").exists():
        try:
            pkg = json.loads((output_dir / "package.json").read_text(encoding="utf-8"))
            commands = pkg.get("contributes", {}).get("commands", [])
            if len(commands) < 10:
                findings.append({"severity": "error", "reason": "too_few_commands", "count": len(commands)})
            ids = [c.get("command") for c in commands]
            for must in ["uacos.contextBudget", "uacos.autopilotPlan", "uacos.patch20Validate", "uacos.providerHealth"]:
                if must not in ids:
                    findings.append({"severity": "error", "reason": "missing_command", "command": must})
        except Exception as exc:
            findings.append({"severity": "error", "reason": "package_json_invalid", "message": str(exc)})
    if (output_dir / "extension.js").exists():
        text = (output_dir / "extension.js").read_text(encoding="utf-8")
        for must in ["context-budget", "context-smart", "autopilot-plan", "patch20-validate", "provider-health"]:
            if must not in text:
                findings.append({"severity": "error", "reason": "extension_missing_cli", "needle": must})
    return {"status": "pass" if not any(f["severity"] == "error" for f in findings) else "fail", "findings": findings, "output_dir": str(output_dir)}
