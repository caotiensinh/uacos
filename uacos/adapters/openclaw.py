from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import subprocess
import uuid
import os
import re

from uacos.config import uacos_dir
from uacos.retrieval.context_pack import build_context_pack
from uacos.budget.optimizer import build_budgeted_context
from uacos.impact.analyzer import smart_context

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def new_run_id() -> str:
    return "OCLAW-" + uuid.uuid4().hex[:12]

def openclaw_dir(repo_root: Path) -> Path:
    p = uacos_dir(repo_root) / "openclaw"
    p.mkdir(parents=True, exist_ok=True)
    return p

def openclaw_config_path(repo_root: Path) -> Path:
    return openclaw_dir(repo_root) / "openclaw_adapter.json"

def history_path(repo_root: Path) -> Path:
    return openclaw_dir(repo_root) / "openclaw_history.jsonl"

DEFAULT_CONFIG = {
    "version": 1,
    "command": "openclaw",
    "chat_script": "",
    "default_agent": "leader",
    "mode": "dry_run",
    "timeout_sec": 300,
    "context_mode": "budget",
    "context_profile": "medium",
    "max_prompt_chars": 120000,
    "output_file": "agent_response.md",
    "allowed_real_run": False,
    "notes": "Use dry_run until command path/agent are validated."
}

def init_openclaw_adapter(repo_root: Path) -> dict:
    path = openclaw_config_path(repo_root)
    if not path.exists():
        path.write_text(json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "ok", "config": str(path), "config_data": json.loads(path.read_text(encoding="utf-8"))}

def load_openclaw_config(repo_root: Path) -> dict:
    path = openclaw_config_path(repo_root)
    if not path.exists():
        init_openclaw_adapter(repo_root)
    return json.loads(path.read_text(encoding="utf-8"))

def save_openclaw_config(repo_root: Path, cfg: dict) -> dict:
    path = openclaw_config_path(repo_root)
    path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "ok", "config": str(path)}

def validate_openclaw_config(repo_root: Path) -> dict:
    cfg = load_openclaw_config(repo_root)
    findings = []
    if cfg.get("mode") not in {"dry_run", "real"}:
        findings.append({"severity": "error", "reason": "invalid_mode", "value": cfg.get("mode")})
    if cfg.get("context_mode") not in {"budget", "smart", "classic"}:
        findings.append({"severity": "error", "reason": "invalid_context_mode", "value": cfg.get("context_mode")})
    if int(cfg.get("timeout_sec", 0)) <= 0:
        findings.append({"severity": "error", "reason": "invalid_timeout"})
    if int(cfg.get("max_prompt_chars", 0)) < 1000:
        findings.append({"severity": "warning", "reason": "max_prompt_chars_too_low"})
    cmd = cfg.get("command", "openclaw")
    script = cfg.get("chat_script", "")
    if script and not Path(script).exists():
        findings.append({"severity": "warning", "reason": "chat_script_missing", "path": script})
    if not script and shutil.which(cmd) is None:
        findings.append({"severity": "warning", "reason": "openclaw_command_not_found", "command": cmd})
    return {"status": "pass" if not any(f["severity"] == "error" for f in findings) else "fail", "findings": findings, "config": cfg}

def openclaw_health(repo_root: Path, real: bool = False) -> dict:
    cfg = load_openclaw_config(repo_root)
    validation = validate_openclaw_config(repo_root)
    if not real:
        return {"status": "ok", "mode": "dry_run", "validation": validation}
    if not cfg.get("allowed_real_run"):
        return {"status": "blocked", "reason": "allowed_real_run_false", "validation": validation}
    cmd = [cfg.get("command", "openclaw"), "--version"]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return {"status": "ok" if res.returncode == 0 else "fail", "returncode": res.returncode, "stdout": res.stdout[-1000:], "stderr": res.stderr[-1000:], "validation": validation}
    except Exception as exc:
        return {"status": "fail", "error": {"type": type(exc).__name__, "message": str(exc)}, "validation": validation}

def set_openclaw_config(repo_root: Path, **kwargs) -> dict:
    cfg = load_openclaw_config(repo_root)
    for k, v in kwargs.items():
        if v is not None:
            cfg[k] = v
    save_openclaw_config(repo_root, cfg)
    return {"status": "ok", "config_data": cfg, "validation": validate_openclaw_config(repo_root)}

def _build_context(repo_root: Path, task: str, cfg: dict) -> dict:
    mode = cfg.get("context_mode", "budget")
    if mode == "budget":
        ctx = build_budgeted_context(repo_root, task, profile=cfg.get("context_profile"))
        return {"mode": mode, "content": ctx["content"], "meta": {k:v for k,v in ctx.items() if k != "content"}}
    if mode == "smart":
        ctx = smart_context(repo_root, task)
        return {"mode": mode, "content": ctx["content"], "meta": {k:v for k,v in ctx.items() if k != "content"}}
    ctx = build_context_pack(repo_root, task, max_tokens=8000)
    return {"mode": mode, "content": ctx["content"], "meta": {k:v for k,v in ctx.items() if k != "content"}}

def build_openclaw_prompt(repo_root: Path, task: str, agent: str | None = None) -> dict:
    cfg = load_openclaw_config(repo_root)
    agent = agent or cfg.get("default_agent", "leader")
    ctx = _build_context(repo_root, task, cfg)
    prompt = f"""REAL EXECUTION REQUEST FOR OPENCLAW AGENT

Agent: {agent}
Repo: {repo_root}
Task:
{task}

Rules:
- Use only the provided context and inspect repo if you have filesystem access.
- Prefer minimal, safe patches.
- Output a unified diff when code changes are needed.
- Do not claim DONE without test evidence.
- If blocked, report exact missing evidence.

Context:
{ctx['content']}
"""
    if len(prompt) > int(cfg.get("max_prompt_chars", 120000)):
        return {"status": "blocked", "reason": "prompt_too_large", "prompt_chars": len(prompt), "max_prompt_chars": cfg.get("max_prompt_chars")}
    out = openclaw_dir(repo_root) / "latest_openclaw_prompt.md"
    out.write_text(prompt, encoding="utf-8")
    return {"status": "ok", "agent": agent, "prompt_file": str(out), "prompt_chars": len(prompt), "context_mode": ctx["mode"], "context_meta": ctx["meta"], "prompt": prompt}

def _append_history(repo_root: Path, row: dict) -> None:
    row = dict(row)
    row.setdefault("ts", utcnow())
    with history_path(repo_root).open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def read_openclaw_history(repo_root: Path, limit: int = 50) -> list[dict]:
    p = history_path(repo_root)
    if not p.exists():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows[-limit:]

def run_openclaw(repo_root: Path, task: str, agent: str | None = None, real: bool = False) -> dict:
    cfg = load_openclaw_config(repo_root)
    run_id = new_run_id()
    prompt = build_openclaw_prompt(repo_root, task, agent=agent)
    record = {"id": run_id, "task": task, "agent": agent or cfg.get("default_agent"), "real": real, "prompt": {k:v for k,v in prompt.items() if k != "prompt"}, "created_at": utcnow()}
    if prompt["status"] != "ok":
        record["status"] = "blocked"
        record["reason"] = prompt.get("reason")
        _append_history(repo_root, record)
        return record
    if not real or cfg.get("mode") == "dry_run":
        record["status"] = "dry_run"
        record["instruction"] = "Copy prompt_file content into OpenClaw manually or run with --real after enabling allowed_real_run."
        _append_history(repo_root, record)
        return record
    if not cfg.get("allowed_real_run"):
        record["status"] = "blocked"
        record["reason"] = "allowed_real_run_false"
        _append_history(repo_root, record)
        return record

    out_file = repo_root / cfg.get("output_file", "agent_response.md")
    timeout = int(cfg.get("timeout_sec", 300))
    script = cfg.get("chat_script", "")
    try:
        if script:
            cmd = [script, agent or cfg.get("default_agent", "leader"), prompt["prompt"]]
        else:
            cmd = [cfg.get("command", "openclaw"), "chat", agent or cfg.get("default_agent", "leader"), prompt["prompt"]]
        res = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True, timeout=timeout)
        output = (res.stdout or "") + ("\nSTDERR:\n" + res.stderr if res.stderr else "")
        out_file.write_text(output, encoding="utf-8")
        record.update({"status": "ok" if res.returncode == 0 else "failed", "returncode": res.returncode, "output_file": str(out_file), "stdout_tail": res.stdout[-2000:], "stderr_tail": res.stderr[-2000:]})
    except Exception as exc:
        record.update({"status": "error", "error": {"type": type(exc).__name__, "message": str(exc)}})
    _append_history(repo_root, record)
    return record

def openclaw_summary(repo_root: Path) -> dict:
    rows = read_openclaw_history(repo_root, limit=10000)
    by_status = {}
    for r in rows:
        st = r.get("status", "unknown")
        by_status[st] = by_status.get(st, 0) + 1
    return {"status": "ok", "runs": len(rows), "by_status": by_status, "recent": rows[-20:]}
