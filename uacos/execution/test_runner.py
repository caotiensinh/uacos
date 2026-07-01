from pathlib import Path
import subprocess
from datetime import datetime, timezone
import json
from uacos.security.command_policy import check_command
from uacos.agent.task import load_task
from uacos.config import uacos_dir

def utcnow():
    return datetime.now(timezone.utc).isoformat()

def results_dir(repo_root: Path) -> Path:
    p = uacos_dir(repo_root) / "test_results"
    p.mkdir(parents=True, exist_ok=True)
    return p

def run_allowed_command(repo_root: Path, command: str, timeout: int = 120) -> dict:
    check = check_command(command)
    if not check["allowed"]:
        return {
            "command": command,
            "allowed": False,
            "status": "blocked",
            "reason": check["reason"],
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "started_at": utcnow(),
            "finished_at": utcnow(),
        }

    started = utcnow()
    try:
        proc = subprocess.run(command, shell=True, cwd=repo_root, capture_output=True, text=True, timeout=timeout)
        return {
            "command": command,
            "allowed": True,
            "status": "pass" if proc.returncode == 0 else "fail",
            "reason": "completed",
            "returncode": proc.returncode,
            "stdout": proc.stdout[-6000:],
            "stderr": proc.stderr[-6000:],
            "started_at": started,
            "finished_at": utcnow(),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "allowed": True,
            "status": "timeout",
            "reason": f"timeout:{timeout}",
            "returncode": None,
            "stdout": (exc.stdout or "")[-6000:] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[-6000:] if isinstance(exc.stderr, str) else "",
            "started_at": started,
            "finished_at": utcnow(),
        }
    except Exception as exc:
        return {
            "command": command,
            "allowed": True,
            "status": "error",
            "reason": f"{type(exc).__name__}:{exc}",
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "started_at": started,
            "finished_at": utcnow(),
        }

def run_task_tests(repo_root: Path, task_file: Path, timeout: int = 120) -> dict:
    task = load_task(task_file)
    commands = list(task.get("tests", [])) + list(task.get("commands", []))
    results = [run_allowed_command(repo_root, cmd, timeout=timeout) for cmd in commands]
    status = "pass"
    if any(r["status"] in {"blocked", "fail", "timeout", "error"} for r in results):
        status = "fail"
    out = {
        "task_id": task["id"],
        "status": status,
        "results": results,
        "created_at": utcnow(),
    }
    path = results_dir(repo_root) / f"{task['id']}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    out["result_file"] = str(path)
    return out
