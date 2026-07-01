from pathlib import Path
from uacos.ops.packaging import bootstrap
from uacos.cache.llm_cache import cache_clear, cache_status, cache_list
from uacos.runtime.llm33_runner import llm_run_real


def test_llm_cache_exact_hit_and_benchmark_semantics(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    bootstrap(repo)
    cache_clear(repo)
    first = llm_run_real(repo, "fix app value", size="small", real=False, use_cache=True)
    assert first["status"] == "dry_run", first
    st1 = cache_status(repo)
    assert st1["items"] >= 1
    second = llm_run_real(repo, "fix app value", size="small", real=False, use_cache=True)
    assert second["status"] == "cache_hit", second
    assert second["usage"]["total_tokens"] == 0
    listed = cache_list(repo)
    assert listed["items"]


def test_llm_cache_clear(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    bootstrap(repo)
    llm_run_real(repo, "fix app value", size="small", real=False, use_cache=True)
    assert cache_status(repo)["items"] >= 1
    cleared = cache_clear(repo)
    assert cleared["status"] == "ok"
    assert cache_status(repo)["items"] == 0
