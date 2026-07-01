import subprocess
import sys

from uacos.cache.similarity import semantic_similarity, jaccard
from uacos.cache.llm_cache import prune_expired, invalidate_cache, find_similar


def test_similarity_backward_compatibility():
    assert semantic_similarity("fix login bug", "fix authentication error") >= 0.6
    assert jaccard("fix login bug", "fix authentication error") >= 0.6


def test_cache_public_imports_are_callable():
    assert callable(prune_expired)
    assert callable(invalidate_cache)
    assert callable(find_similar)


def test_cache_status_cli_does_not_crash():
    result = subprocess.run(
        [sys.executable, "-m", "uacos.cli", "cache-status"],
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
