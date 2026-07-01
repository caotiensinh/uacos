from pathlib import Path
from uacos.storage import init_storage
from uacos.memory.store import add_memory, search_memories, read_memories, invalidate_memory, memory_summary_for_task
from uacos.memory.regression import add_regression_rule, regression_check_patch
from uacos.retrieval.context_pack import build_context_pack
from uacos.scanner.file_scanner import scan_repo

def test_phase8_memory_add_search_invalidate(tmp_path: Path):
    repo = tmp_path / "repo"; repo.mkdir(); init_storage(repo)
    mem = add_memory(repo, "project_truth", "barrier_rule", "Barrier lower must obey safe ROI", tags=["barrier", "safety"], applies_to=["backend/barrier.py"])
    assert mem["id"].startswith("MEM-")
    results = search_memories(repo, "barrier ROI")
    assert results
    assert results[0]["key"] == "barrier_rule"
    invalidate_memory(repo, mem["id"], "replaced by v2")
    active = read_memories(repo)
    assert not any(x["id"] == mem["id"] for x in active)
    all_rows = read_memories(repo, include_invalid=True)
    assert any(x["id"] == mem["id"] and x["invalid_at"] for x in all_rows)

def test_phase8_context_pack_injects_memory(tmp_path: Path):
    repo = tmp_path / "repo"; repo.mkdir()
    (repo / "barrier.py").write_text("def open_gate():\n    return True\n", encoding="utf-8")
    init_storage(repo); scan_repo(repo)
    add_memory(repo, "decision", "barrier_priority", "AI box LPR event has priority to open barrier", tags=["barrier"])
    pack = build_context_pack(repo, "fix barrier open", max_tokens=3000)
    assert "Relevant Memory" in pack["content"]
    assert "AI box LPR event has priority" in pack["content"]

def test_phase8_regression_rule_check(tmp_path: Path):
    repo = tmp_path / "repo"; repo.mkdir(); init_storage(repo)
    add_regression_rule(repo, "Do not touch video pipeline", "backend/video_pipeline.py", severity="high", reason="fragile smooth video")
    patch = repo / "change.diff"
    patch.write_text(
        "diff --git a/backend/video_pipeline.py b/backend/video_pipeline.py\n"
        "--- a/backend/video_pipeline.py\n"
        "+++ b/backend/video_pipeline.py\n"
        "@@ -1 +1 @@\n"
        "-x = 1\n"
        "+x = 2\n",
        encoding="utf-8",
    )
    result = regression_check_patch(repo, patch)
    assert result["status"] == "fail"
    assert result["findings"]
    assert result["findings"][0]["type"] == "regression_rule_match"
