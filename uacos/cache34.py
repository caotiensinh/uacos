"""
Compatibility facade for old cache34 commands.

Production rule for Phase 42:
- Use official uacos.cache.llm_cache storage path when possible.
- Do not introduce a second incompatible cache format for new LLM flows.
"""

import json
import hashlib
from pathlib import Path


def _official_dir(repo):
    p = Path(repo) / ".uacos" / "llm_cache"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _legacy_dir(repo):
    p = Path(repo) / ".uacos" / "cache34"
    p.mkdir(parents=True, exist_ok=True)
    return p


def key(task):
    return hashlib.sha256(str(task).encode("utf-8")).hexdigest()


def get(repo, task):
    # Legacy compatibility only. Official llm cache is used by llm33_runner.
    legacy_path = _legacy_dir(repo) / key(task)
    if legacy_path.exists():
        return json.loads(legacy_path.read_text(encoding="utf-8"))
    return None


def set(repo, task, res):
    # Keep legacy free-text fallback cache isolated.
    (_legacy_dir(repo) / key(task)).write_text(
        json.dumps(res, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def clear(repo):
    deleted = 0
    for cache_dir in (_official_dir(repo), _legacy_dir(repo)):
        for path in cache_dir.glob("*"):
            if path.is_file():
                path.unlink()
                deleted += 1
    return deleted


def status(repo):
    official_files = [p for p in _official_dir(repo).glob("*") if p.is_file()]
    legacy_files = [p for p in _legacy_dir(repo).glob("*") if p.is_file()]
    total_bytes = sum(p.stat().st_size for p in official_files + legacy_files)

    return {
        "status": "ok",
        "cache_count": len(official_files) + len(legacy_files),
        "official_count": len(official_files),
        "legacy_count": len(legacy_files),
        "path": str(_official_dir(repo)),
        "legacy_path": str(_legacy_dir(repo)),
        "bytes": total_bytes,
        "source": "uacos.cache.llm_cache",
    }
