from __future__ import annotations

from pathlib import Path
import json, uuid
from datetime import datetime, timezone
from uacos.config import uacos_dir

VALID_KINDS = {"project_truth", "decision", "error", "failure", "deprecated", "regression_rule", "note"}

def utcnow():
    return datetime.now(timezone.utc).isoformat()

def new_id(prefix="MEM"):
    return prefix + "-" + uuid.uuid4().hex[:12]

def memory_path(repo_root: Path) -> Path:
    p = uacos_dir(repo_root)
    p.mkdir(parents=True, exist_ok=True)
    return p / "memory.jsonl"

def _append(repo_root: Path, record: dict):
    with memory_path(repo_root).open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def add_memory(repo_root: Path, kind: str, key: str, value: str, source: str = "user", confidence: float = 1.0, tags: list[str] | None = None, applies_to: list[str] | None = None) -> dict:
    if kind not in VALID_KINDS:
        raise ValueError(f"invalid_memory_kind:{kind}")
    rec = {
        "id": new_id("MEM"),
        "kind": kind,
        "key": key,
        "value": value,
        "source": source,
        "confidence": float(confidence),
        "tags": tags or [],
        "applies_to": applies_to or [],
        "valid_at": utcnow(),
        "invalid_at": None,
        "invalid_reason": None,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    _append(repo_root, rec)
    return rec

def read_memories(repo_root: Path, include_invalid: bool = False) -> list[dict]:
    path = memory_path(repo_root)
    if not path.exists():
        return []
    rows = []
    invalidated = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("event") == "invalidate":
            invalidated[rec["memory_id"]] = rec
        else:
            rows.append(rec)
    out = []
    for rec in rows:
        inv = invalidated.get(rec["id"])
        if inv:
            rec = dict(rec)
            rec["invalid_at"] = inv["invalid_at"]
            rec["invalid_reason"] = inv["reason"]
        if include_invalid or not rec.get("invalid_at"):
            out.append(rec)
    return out

def invalidate_memory(repo_root: Path, memory_id: str, reason: str) -> dict:
    rec = {
        "event": "invalidate",
        "memory_id": memory_id,
        "reason": reason,
        "invalid_at": utcnow(),
    }
    _append(repo_root, rec)
    return rec

def search_memories(repo_root: Path, query: str, include_invalid: bool = False, limit: int = 20) -> list[dict]:
    terms = [t.lower() for t in query.split() if t.strip()]
    rows = read_memories(repo_root, include_invalid=include_invalid)
    scored = []
    for rec in rows:
        hay = " ".join([
            rec.get("kind", ""), rec.get("key", ""), rec.get("value", ""),
            " ".join(rec.get("tags", [])), " ".join(rec.get("applies_to", []))
        ]).lower()
        score = sum(1 for t in terms if t in hay)
        if score > 0 or not terms:
            r = dict(rec)
            r["_score"] = score
            scored.append(r)
    scored.sort(key=lambda x: (x["_score"], x.get("confidence", 0)), reverse=True)
    return scored[:limit]

def memory_summary_for_task(repo_root: Path, task: str, limit: int = 12) -> str:
    rows = search_memories(repo_root, task, include_invalid=False, limit=limit)
    if not rows:
        return "No active project memories matched this task."
    lines = ["# Relevant Project Memory", ""]
    for r in rows:
        lines.append(f"- [{r['kind']}] {r['key']}: {r['value']} (id={r['id']}, confidence={r.get('confidence')})")
    return "\n".join(lines) + "\n"
