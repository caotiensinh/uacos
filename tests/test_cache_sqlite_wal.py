from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import threading

from uacos.cache.llm_cache import get_cache, put_cache, prune_expired, cache_status


def test_concurrent_writes_sqlite_wal(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    errors = []

    def worker(i: int):
        try:
            put_cache(repo, f"key-{i}", f"task {i}", f"prompt {i}", {"status": "ok", "value": i})
        except Exception as exc:  # pragma: no cover - assertion reports details
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    assert cache_status(repo)["items"] == 5


def test_ttl_expiry_prunes_sqlite_entries(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    put_cache(repo, "expired", "task", "prompt", {"status": "ok"})

    old = (datetime.now(timezone.utc) - timedelta(seconds=3600)).isoformat()
    import sqlite3
    with sqlite3.connect(repo / ".uacos" / "llm_cache.db") as conn:
        conn.execute("UPDATE cache_entries SET created_at=?, ttl_seconds=? WHERE key=?", (old, 1, "expired"))
        conn.commit()

    assert get_cache(repo, "expired") is None
    assert prune_expired(repo)["kept"] == 0


def test_migration_from_old_json_cache(tmp_path: Path):
    repo = tmp_path / "repo"
    old_dir = repo / ".uacos" / "llm_cache"
    old_dir.mkdir(parents=True)
    payload = {
        "key": "old-key",
        "task": "old task",
        "prompt_hash": "abc",
        "result": {"status": "ok", "value": 42},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ttl_seconds": 86400,
    }
    (old_dir / "old-key.json").write_text(json.dumps(payload), encoding="utf-8")

    migrated = get_cache(repo, "old-key")

    assert migrated is not None
    assert migrated["result"]["value"] == 42
    assert (repo / ".uacos" / "llm_cache_migrated").exists()
    assert (repo / ".uacos" / "llm_cache.db").exists()
