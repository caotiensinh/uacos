from __future__ import annotations

from pathlib import Path

from uacos.cache.llm_cache import get_cache, put_cache
from uacos.ops.packaging import bootstrap


def test_file_change_invalidates_related_llm_cache(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = repo / "app.py"
    app.write_text("def value():\n    return 1\n", encoding="utf-8")

    first = bootstrap(repo)
    assert "app.py" in first["scan_result"]["changed_files"]

    put_cache(
        repo,
        "cache-for-app.py",
        "fix app.py",
        "Context includes app.py",
        {"status": "ok", "file": "app.py"},
    )
    assert get_cache(repo, "cache-for-app.py") is not None

    app.write_text("def value():\n    return 2\n", encoding="utf-8")
    second = bootstrap(repo)

    assert "app.py" in second["scan_result"]["changed_files"]
    assert second["cache_invalidation"]["removed"] >= 1
    assert get_cache(repo, "cache-for-app.py") is None
