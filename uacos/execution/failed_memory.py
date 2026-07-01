from __future__ import annotations

from pathlib import Path
import json
from datetime import datetime, timezone
from uacos.config import uacos_dir

def utcnow():
    return datetime.now(timezone.utc).isoformat()

def failed_memory_path(repo_root: Path) -> Path:
    p = uacos_dir(repo_root)
    p.mkdir(parents=True, exist_ok=True)
    return p / "failed_tasks.jsonl"

def record_failure(repo_root: Path, task_id: str, reason: str, detail: dict | None = None) -> dict:
    record = {"ts": utcnow(), "task_id": task_id, "reason": reason, "detail": detail or {}}
    with failed_memory_path(repo_root).open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record

def read_failures(repo_root: Path) -> list:
    path = failed_memory_path(repo_root)
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows
