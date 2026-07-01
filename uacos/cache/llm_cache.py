from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import sqlite3
import threading

from uacos.config import uacos_dir
from uacos.cache.similarity import semantic_similarity, jaccard


DEFAULT_TTL_SECONDS = int(os.environ.get("UACOS_LLM_CACHE_TTL_SECONDS", "86400"))
_DB_LOCK = threading.RLock()


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def _age_seconds(value: str | None) -> float | None:
    created = _parse_ts(value)
    if not created:
        return None
    return (datetime.now(timezone.utc) - created).total_seconds()


def _is_expired(item: dict, ttl_seconds: int | None = None) -> bool:
    ttl = DEFAULT_TTL_SECONDS if ttl_seconds is None else int(ttl_seconds)
    if ttl <= 0:
        return False
    age = _age_seconds(item.get("created_at"))
    return age is None or age > ttl


def cache_dir(repo_root: Path) -> Path:
    p = uacos_dir(repo_root) / "llm_cache"
    if not (uacos_dir(repo_root) / "llm_cache_migrated").exists():
        p.mkdir(parents=True, exist_ok=True)
    return p


def db_path(repo_root: Path) -> Path:
    p = uacos_dir(repo_root)
    p.mkdir(parents=True, exist_ok=True)
    return p / "llm_cache.db"


def _connect(repo_root: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path(repo_root), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=3000")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS cache_entries(
            key TEXT PRIMARY KEY,
            task TEXT,
            prompt_hash TEXT,
            result TEXT,
            created_at TEXT,
            ttl_seconds INTEGER
        )
        """
    )
    conn.commit()
    _migrate_json_cache(repo_root, conn)
    return conn


def _migrate_json_cache(repo_root: Path, conn: sqlite3.Connection) -> None:
    old_dir = uacos_dir(repo_root) / "llm_cache"
    migrated_dir = uacos_dir(repo_root) / "llm_cache_migrated"
    if not old_dir.exists() or migrated_dir.exists():
        return
    json_files = [p for p in old_dir.glob("*.json") if p.name != "index.json"]
    if not json_files:
        return
    for path in json_files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        key = str(data.get("key") or path.stem)
        task = str(data.get("task") or "")
        prompt_hash = str(data.get("prompt_hash") or "")
        created_at = str(data.get("created_at") or utcnow())
        ttl_seconds = int(data.get("ttl_seconds") or DEFAULT_TTL_SECONDS)
        result = data.get("result", data)
        conn.execute(
            """
            INSERT OR REPLACE INTO cache_entries(key, task, prompt_hash, result, created_at, ttl_seconds)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (key, task, prompt_hash, json.dumps(result, ensure_ascii=False), created_at, ttl_seconds),
        )
    conn.commit()
    target = migrated_dir
    if target.exists():
        shutil.rmtree(target)
    old_dir.rename(target)


def _row_to_cache(row: sqlite3.Row, hit_type: str = "exact") -> dict:
    try:
        result = json.loads(row["result"] or "{}")
    except Exception:
        result = {"status": "error", "raw": row["result"]}
    return {
        "key": row["key"],
        "task": row["task"],
        "prompt_hash": row["prompt_hash"],
        "result": result,
        "created_at": row["created_at"],
        "ttl_seconds": row["ttl_seconds"],
        "hit_type": hit_type,
    }


def make_cache_key(
    task: str,
    prompt: str,
    size: str | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> str:
    raw = json.dumps(
        {
            "task": task,
            "prompt_head": (prompt or "")[:8000],
            "size": size,
            "provider": provider,
            "model": model,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_cache(repo_root: Path, key: str, ttl_seconds: int | None = None) -> dict | None:
    with _connect(repo_root) as conn:
        row = conn.execute("SELECT * FROM cache_entries WHERE key = ?", (key,)).fetchone()
        if not row:
            return None
        data = _row_to_cache(row)
        effective_ttl = ttl_seconds if ttl_seconds is not None else data.get("ttl_seconds")
        if _is_expired(data, ttl_seconds=effective_ttl):
            conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
            conn.commit()
            return None
        return data


def put_cache(
    repo_root: Path,
    key: str,
    task: str,
    prompt: str,
    result: dict,
    meta: dict | None = None,
) -> dict:
    prompt_hash = hashlib.sha256((prompt or "").encode("utf-8")).hexdigest()
    created_at = utcnow()
    stored_result = dict(result or {})
    if meta:
        stored_result.setdefault("meta", meta)
    if prompt:
        stored_result.setdefault("prompt_head", prompt[:1200])
    with _DB_LOCK:
        with _connect(repo_root) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache_entries(key, task, prompt_hash, result, created_at, ttl_seconds)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (key, task, prompt_hash, json.dumps(stored_result, ensure_ascii=False), created_at, DEFAULT_TTL_SECONDS),
            )
            conn.commit()
    return {
        "key": key,
        "task": task,
        "prompt_hash": prompt_hash,
        "result": stored_result,
        "created_at": created_at,
        "ttl_seconds": DEFAULT_TTL_SECONDS,
    }


def set_cache(
    repo_root: Path,
    key: str,
    task: str = "",
    prompt: str = "",
    result: dict | None = None,
    meta: dict | None = None,
) -> dict:
    return put_cache(repo_root, key, task, prompt, result or {}, meta=meta)


def prune_expired(repo_root: Path, ttl_seconds: int | None = None) -> dict:
    removed = 0
    with _DB_LOCK:
        with _connect(repo_root) as conn:
            rows = conn.execute("SELECT key, created_at, ttl_seconds FROM cache_entries").fetchall()
            for row in rows:
                item = {"key": row["key"], "created_at": row["created_at"], "ttl_seconds": row["ttl_seconds"]}
                effective_ttl = ttl_seconds if ttl_seconds is not None else row["ttl_seconds"]
                if _is_expired(item, ttl_seconds=effective_ttl):
                    conn.execute("DELETE FROM cache_entries WHERE key = ?", (row["key"],))
                    removed += 1
            conn.commit()
            remaining = conn.execute("SELECT COUNT(*) AS c FROM cache_entries").fetchone()["c"]
    return {
        "status": "ok",
        "removed": removed,
        "kept": int(remaining),
        "ttl_seconds": DEFAULT_TTL_SECONDS if ttl_seconds is None else ttl_seconds,
    }


def invalidate_cache(repo_root: Path, keys: list[str] | None = None) -> dict:
    if not keys:
        return cache_clear(repo_root)
    removed = 0
    with _DB_LOCK:
        with _connect(repo_root) as conn:
            rows = conn.execute("SELECT key, task, result FROM cache_entries").fetchall()
            for row in rows:
                haystack = "\n".join([row["key"] or "", row["task"] or "", row["result"] or ""])
                if any(str(key) and str(key) in haystack for key in keys):
                    conn.execute("DELETE FROM cache_entries WHERE key = ?", (row["key"],))
                    removed += 1
            conn.commit()
            remaining = conn.execute("SELECT COUNT(*) AS c FROM cache_entries").fetchone()["c"]
    return {"status": "ok", "removed": removed, "remaining": int(remaining)}


def find_similar(repo_root: Path, task: str, threshold: float = 0.65) -> dict | None:
    prune_expired(repo_root)
    best = None
    best_score = 0.0
    with _connect(repo_root) as conn:
        rows = conn.execute("SELECT * FROM cache_entries").fetchall()
        for row in rows:
            score = semantic_similarity(task, row["task"] or "")
            if score > best_score:
                best_score = score
                best = row
    if best and best_score >= threshold:
        data = _row_to_cache(best, hit_type="similar")
        data["similarity"] = round(best_score, 4)
        return data
    return None


def cache_status(repo_root: Path) -> dict:
    prune = prune_expired(repo_root)
    with _connect(repo_root) as conn:
        rows = conn.execute(
            """
            SELECT key, task, prompt_hash, created_at, ttl_seconds, result
            FROM cache_entries ORDER BY created_at
            """
        ).fetchall()
        items = []
        total_bytes = 0
        for row in rows:
            result_text = row["result"] or ""
            total_bytes += len(result_text.encode("utf-8"))
            status = provider = model = None
            try:
                result = json.loads(result_text)
                status = result.get("status")
                provider = result.get("provider")
                model = result.get("model")
            except Exception:
                pass
            items.append({
                "key": row["key"],
                "task": row["task"],
                "created_at": row["created_at"],
                "prompt_hash": row["prompt_hash"],
                "status": status,
                "provider": provider,
                "model": model,
            })
    return {
        "status": "ok",
        "items": len(items),
        "cache_db": str(db_path(repo_root)),
        "cache_dir": str(uacos_dir(repo_root) / "llm_cache"),
        "bytes": total_bytes,
        "ttl_seconds": DEFAULT_TTL_SECONDS,
        "expired_removed": prune.get("removed", 0),
        "recent": items[-10:],
    }


def cache_list(repo_root: Path, limit: int = 50) -> dict:
    prune_expired(repo_root)
    with _connect(repo_root) as conn:
        rows = conn.execute("SELECT * FROM cache_entries ORDER BY created_at DESC LIMIT ?", (int(limit),)).fetchall()
    return {"status": "ok", "items": [_row_to_cache(row) for row in rows]}


def cache_clear(repo_root: Path) -> dict:
    with _DB_LOCK:
        with _connect(repo_root) as conn:
            before = conn.execute("SELECT COUNT(*) AS c FROM cache_entries").fetchone()["c"]
            conn.execute("DELETE FROM cache_entries")
            conn.commit()
    return {"status": "ok", "removed": int(before), "cache_db": str(db_path(repo_root))}
