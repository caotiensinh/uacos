from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import subprocess
import uuid
import shlex
import sys
import os

from uacos.config import uacos_dir
from uacos.skill.store import get_skill, suggest_skills, mark_skill_used

SAFE_COMMAND_PREFIXES = [
    "python -S -c",
    "python -c",
    "py -3.12 -c",
    "py -3.12 -S -c",
    "python -m pytest",
    "pytest",
    "uacos ",
    "git status",
    "git diff",
    "git log",
    "pip --version",
    "python --version",
    "py --version",
]

BLOCKED_TOKENS = [
    " rm ",
    "del ",
    "Remove-Item",
    "format ",
    "shutdown",
    "restart",
    "curl ",
    "wget ",
    "Invoke-WebRequest",
    ">",
    ">>",
    "|",
    "&&",
]

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def new_execution_id() -> str:
    return "SKEXEC-" + uuid.uuid4().hex[:12]

def skill_exec_dir(repo_root: Path) -> Path:
    p = uacos_dir(repo_root) / "skill_executions"
    p.mkdir(parents=True, exist_ok=True)
    return p

def skill_exec_history_path(repo_root: Path) -> Path:
    p = uacos_dir(repo_root)
    p.mkdir(parents=True, exist_ok=True)
    return p / "skill_execution_history.jsonl"

def _append_history(repo_root: Path, record: dict) -> None:
    with skill_exec_history_path(repo_root).open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def read_skill_execution_history(repo_root: Path) -> list[dict]:
    path = skill_exec_history_path(repo_root)
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows

def is_command_safe(command: str, extra_allowed_prefixes: list[str] | None = None) -> dict:
    c = " " + command.strip() + " "
    for bad in BLOCKED_TOKENS:
        if bad in c:
            return {"safe": False, "reason": f"blocked_token:{bad.strip()}"}
    prefixes = list(SAFE_COMMAND_PREFIXES)
    if extra_allowed_prefixes:
        prefixes.extend(extra_allowed_prefixes)
    stripped = command.strip()
    if any(stripped.startswith(prefix) for prefix in prefixes):
        return {"safe": True, "reason": "allowed_prefix"}
    return {"safe": False, "reason": "prefix_not_allowed"}

def skill_execution_plan(repo_root: Path, skill_id: str, task: str = "", dry_run: bool = True, extra_allowed_prefixes: list[str] | None = None) -> dict:
    skill = get_skill(repo_root, skill_id)
    if not skill:
        raise KeyError(f"skill_not_found:{skill_id}")
    commands = skill.get("commands", []) or []
    steps = []
    for idx, command in enumerate(commands, 1):
        safety = is_command_safe(command, extra_allowed_prefixes=extra_allowed_prefixes)
        steps.append({
            "step": idx,
            "command": command,
            "safe": safety["safe"],
            "safety_reason": safety["reason"],
            "would_run": bool(safety["safe"] and not dry_run),
        })
    return {
        "status": "ok",
        "skill_id": skill_id,
        "title": skill.get("title"),
        "skill_status": skill.get("status"),
        "task": task,
        "dry_run": dry_run,
        "step_count": len(steps),
        "blocked_count": len([s for s in steps if not s["safe"]]),
        "steps": steps,
        "created_at": utcnow(),
    }

def run_command(repo_root: Path, command: str, timeout_sec: int = 120) -> dict:
    res = subprocess.run(command, cwd=repo_root, shell=True, capture_output=True, text=True, timeout=timeout_sec)
    return {
        "command": command,
        "returncode": res.returncode,
        "stdout": res.stdout[-4000:],
        "stderr": res.stderr[-4000:],
        "ok": res.returncode == 0,
    }

def execute_skill(repo_root: Path, skill_id: str, task: str = "", dry_run: bool = True, timeout_sec: int = 120, extra_allowed_prefixes: list[str] | None = None) -> dict:
    skill = get_skill(repo_root, skill_id)
    if not skill:
        raise KeyError(f"skill_not_found:{skill_id}")
    if skill.get("status") != "approved":
        return {"status": "blocked", "reason": "skill_not_approved", "skill_id": skill_id, "skill_status": skill.get("status")}

    plan = skill_execution_plan(repo_root, skill_id, task=task, dry_run=dry_run, extra_allowed_prefixes=extra_allowed_prefixes)
    execution = {
        "id": new_execution_id(),
        "status": "dry_run" if dry_run else "running",
        "skill_id": skill_id,
        "title": skill.get("title"),
        "task": task,
        "dry_run": dry_run,
        "plan": plan,
        "results": [],
        "created_at": utcnow(),
    }

    if plan["blocked_count"] > 0:
        execution["status"] = "blocked"
        execution["reason"] = "unsafe_command_in_plan"
    elif dry_run:
        execution["status"] = "dry_run"
    else:
        all_ok = True
        for step in plan["steps"]:
            result = run_command(repo_root, step["command"], timeout_sec=timeout_sec)
            execution["results"].append(result)
            if not result["ok"]:
                all_ok = False
                break
        execution["status"] = "done" if all_ok else "failed"
        if all_ok:
            mark_skill_used(repo_root, skill_id, task=task)

    out = skill_exec_dir(repo_root) / f"{execution['id']}.json"
    out.write_text(json.dumps(execution, ensure_ascii=False, indent=2), encoding="utf-8")
    execution["execution_file"] = str(out)
    _append_history(repo_root, {
        "id": execution["id"],
        "skill_id": skill_id,
        "title": skill.get("title"),
        "task": task,
        "status": execution["status"],
        "dry_run": dry_run,
        "created_at": execution["created_at"],
        "execution_file": str(out),
    })
    return execution

def execute_best_skill(repo_root: Path, task: str, dry_run: bool = True, min_score: float = 1.0, timeout_sec: int = 120) -> dict:
    suggestions = suggest_skills(repo_root, task, limit=5, min_score=min_score)
    approved = [s for s in suggestions if s.get("status") == "approved"]
    if not approved:
        return {"status": "no_skill", "task": task, "suggestions": suggestions}
    skill = approved[0]
    result = execute_skill(repo_root, skill["id"], task=task, dry_run=dry_run, timeout_sec=timeout_sec)
    result["selected_score"] = skill.get("_score")
    return result

def skill_execution_summary(repo_root: Path) -> dict:
    rows = read_skill_execution_history(repo_root)
    by_status = {}
    for row in rows:
        by_status[row.get("status", "unknown")] = by_status.get(row.get("status", "unknown"), 0) + 1
    return {"status": "ok", "count": len(rows), "by_status": by_status, "recent": rows[-20:]}
