from __future__ import annotations

from pathlib import Path
import zipfile
import shutil
import sys
import json
from datetime import datetime, timezone
from uacos.config import uacos_dir
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.agent.registry import init_agent_registry
from uacos.agent.adapter_config import init_adapter_config
from uacos.dashboard.ops_summary import ops_summary
from uacos.cache.llm_cache import invalidate_cache

def utcnow():
    return datetime.now(timezone.utc).isoformat()

def bootstrap(repo_root: Path, scan: bool = True) -> dict:
    db = init_storage(repo_root)
    agent_registry = init_agent_registry(repo_root)
    adapter_config = init_adapter_config(repo_root)
    scan_result = scan_repo(repo_root) if scan else None
    changed_files = (scan_result or {}).get("changed_files", [])
    cache_invalidation = invalidate_cache(repo_root, keys=[f for f in changed_files]) if changed_files else {"status": "skipped", "removed": 0}
    return {
        "status": "ok",
        "repo": str(repo_root),
        "db": str(db),
        "agent_registry": str(agent_registry),
        "adapter_config": str(adapter_config),
        "scan_result": scan_result,
        "cache_invalidation": cache_invalidation,
        "created_at": utcnow(),
    }

def health_check(repo_root: Path) -> dict:
    udir = uacos_dir(repo_root)
    checks = []
    def add(name, ok, detail=""):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})
    add("repo_exists", repo_root.exists() and repo_root.is_dir(), str(repo_root))
    add("uacos_dir_exists", udir.exists(), str(udir))
    add("db_exists", (udir / "repo_index.sqlite").exists(), str(udir / "repo_index.sqlite"))
    add("agents_config_exists", (udir / "agents.json").exists(), str(udir / "agents.json"))
    add("adapters_config_exists", (udir / "adapters.json").exists(), str(udir / "adapters.json"))
    try:
        summary = ops_summary(repo_root)
        add("ops_summary_ok", True, json.dumps(summary, ensure_ascii=False)[:500])
    except Exception as exc:
        add("ops_summary_ok", False, f"{type(exc).__name__}:{exc}")
    return {"status": "pass" if all(c["ok"] for c in checks) else "fail", "checks": checks, "created_at": utcnow()}

def doctor(repo_root: Path, auto_fix: bool = False) -> dict:
    before = health_check(repo_root)
    actions = []
    if before["status"] != "pass" and auto_fix:
        result = bootstrap(repo_root, scan=False)
        actions.append({"action": "bootstrap", "result": result})
    after = health_check(repo_root)
    return {"status": after["status"], "before": before, "actions": actions, "after": after}

def _zip_dir(src_dir: Path, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
        for p in src_dir.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(src_dir.parent))
    return output

def backup_uacos(repo_root: Path, output: Path) -> dict:
    udir = uacos_dir(repo_root)
    if not udir.exists():
        raise FileNotFoundError(f"UACOS dir not found: {udir}")
    out = _zip_dir(udir, output)
    return {"status": "ok", "backup": str(out), "source": str(udir), "created_at": utcnow()}

def export_uacos(repo_root: Path, output: Path) -> dict:
    return backup_uacos(repo_root, output)

def import_uacos(repo_root: Path, input_zip: Path, overwrite: bool = False) -> dict:
    udir = uacos_dir(repo_root)
    if udir.exists() and overwrite:
        shutil.rmtree(udir)
    udir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(input_zip, "r") as z:
        z.extractall(repo_root)
    return {"status": "ok", "input": str(input_zip), "target": str(udir), "created_at": utcnow()}

def release_check(repo_root: Path) -> dict:
    hc = health_check(repo_root)
    summary = ops_summary(repo_root)
    findings = []
    if hc["status"] != "pass":
        findings.append({"type": "health_failed", "detail": hc})
    stats = summary.get("stats", {}) if isinstance(summary, dict) else {}
    if stats.get("file_count", 0) == 0:
        findings.append({"type": "no_indexed_files", "detail": "run uacos scan"})
    if summary.get("failure_count", 0) > 0:
        findings.append({"type": "has_failed_memory", "detail": f"failure_count={summary.get('failure_count')}"})
    return {"status": "pass" if not findings else "warn", "health": hc, "summary": summary, "findings": findings, "created_at": utcnow()}

def write_run_scripts(repo_root: Path, output_dir: Path, port: int = 8765) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    bash = output_dir / "run_uacos_dashboard.sh"
    ps1 = output_dir / "run_uacos_dashboard.ps1"
    bat = output_dir / "run_uacos_dashboard.bat"
    bash_content = "#!/usr/bin/env bash\nset -e\nREPO=\"" + str(repo_root) + "\"\npython -m uacos.cli bootstrap --repo \"$REPO\"\npython -m uacos.cli dashboard --repo \"$REPO\" --host 127.0.0.1 --port " + str(port) + "\n"
    bash.write_text(bash_content, encoding="utf-8")
    try:
        bash.chmod(0o755)
    except Exception:
        pass
    ps1_content = "$ErrorActionPreference = \"Stop\"\n$REPO = \"" + str(repo_root) + "\"\npython -m uacos.cli bootstrap --repo \"$REPO\"\npython -m uacos.cli dashboard --repo \"$REPO\" --host 127.0.0.1 --port " + str(port) + "\n"
    ps1.write_text(ps1_content, encoding="utf-8")
    bat_content = "@echo off\nset REPO=" + str(repo_root) + "\npython -m uacos.cli bootstrap --repo \"%REPO%\"\npython -m uacos.cli dashboard --repo \"%REPO%\" --host 127.0.0.1 --port " + str(port) + "\n"
    bat.write_text(bat_content, encoding="utf-8")
    return {"status": "ok", "files": [str(bash), str(ps1), str(bat)]}

def write_systemd_service(repo_root: Path, output: Path, port: int = 8765, user: str | None = None) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    user_line = ("User=" + user + "\n") if user else ""
    content = (
        "[Unit]\n"
        "Description=UACOS Dashboard\n"
        "After=network.target\n\n"
        "[Service]\n"
        "Type=simple\n"
        + user_line +
        "WorkingDirectory=" + str(repo_root) + "\n"
        "ExecStart=" + sys.executable + " -m uacos.cli dashboard --repo " + str(repo_root) + " --host 127.0.0.1 --port " + str(port) + "\n"
        "Restart=on-failure\n"
        "RestartSec=5\n\n"
        "[Install]\n"
        "WantedBy=multi-user.target\n"
    )
    output.write_text(content, encoding="utf-8")
    return {"status": "ok", "service_file": str(output)}
