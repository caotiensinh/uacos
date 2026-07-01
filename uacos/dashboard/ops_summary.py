from pathlib import Path
from uacos.search import stats
from uacos.memory.store import read_memories
from uacos.execution.token_ledger import ledger_summary
from uacos.execution.failed_memory import read_failures
from uacos.apply.patch_apply import list_manifests
from uacos.config import uacos_dir

def _safe(fn, fallback):
    try:
        return fn()
    except Exception as exc:
        return {"error": f"{type(exc).__name__}:{exc}", "fallback": fallback}

def ops_summary(repo_root: Path) -> dict:
    memories = _safe(lambda: read_memories(repo_root, include_invalid=True), [])
    failures = _safe(lambda: read_failures(repo_root), [])
    manifests = _safe(lambda: list_manifests(repo_root), {"count": 0, "manifests": []})
    tokens = _safe(lambda: ledger_summary(repo_root), {})
    repo_stats = _safe(lambda: stats(repo_root), {})
    return {
        "repo": str(repo_root),
        "uacos_dir": str(uacos_dir(repo_root)),
        "stats": repo_stats,
        "memory_count": len(memories) if isinstance(memories, list) else 0,
        "active_memory_count": len([m for m in memories if not m.get("invalid_at")]) if isinstance(memories, list) else 0,
        "failure_count": len(failures) if isinstance(failures, list) else 0,
        "manifest_count": manifests.get("count", 0) if isinstance(manifests, dict) else 0,
        "token_summary": tokens,
    }
