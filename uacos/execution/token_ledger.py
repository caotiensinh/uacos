from __future__ import annotations

from pathlib import Path
import json
from datetime import datetime, timezone
from uacos.config import uacos_dir

def utcnow():
    return datetime.now(timezone.utc).isoformat()

def ledger_path(repo_root: Path) -> Path:
    p = uacos_dir(repo_root)
    p.mkdir(parents=True, exist_ok=True)
    return p / "token_ledger.jsonl"

def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    low = model.lower()
    if "local" in low or "ollama" in low:
        return 0.0
    return round((input_tokens * 0.50 + output_tokens * 1.50) / 1_000_000, 6)

def log_token_usage(repo_root: Path, task_id: str, agent: str, model: str, input_tokens: int, output_tokens: int, context_id: str | None = None) -> dict:
    record = {
        "ts": utcnow(),
        "task_id": task_id,
        "agent": agent,
        "model": model,
        "input_tokens": int(input_tokens),
        "output_tokens": int(output_tokens),
        "estimated_cost_usd": estimate_cost_usd(model, int(input_tokens), int(output_tokens)),
        "context_id": context_id,
    }
    with ledger_path(repo_root).open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record

def read_ledger(repo_root: Path) -> list:
    path = ledger_path(repo_root)
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows

def _group_sum(rows: list, key: str) -> dict:
    out = {}
    for r in rows:
        k = r.get(key) or "unknown"
        item = out.setdefault(k, {"calls": 0, "input_tokens": 0, "output_tokens": 0, "estimated_cost_usd": 0.0})
        item["calls"] += 1
        item["input_tokens"] += r.get("input_tokens", 0)
        item["output_tokens"] += r.get("output_tokens", 0)
        item["estimated_cost_usd"] = round(item["estimated_cost_usd"] + r.get("estimated_cost_usd", 0.0), 6)
    return out

def ledger_summary(repo_root: Path) -> dict:
    rows = read_ledger(repo_root)
    return {
        "records": len(rows),
        "input_tokens": sum(r.get("input_tokens", 0) for r in rows),
        "output_tokens": sum(r.get("output_tokens", 0) for r in rows),
        "estimated_cost_usd": round(sum(r.get("estimated_cost_usd", 0.0) for r in rows), 6),
        "by_agent": _group_sum(rows, "agent"),
        "by_model": _group_sum(rows, "model"),
    }
