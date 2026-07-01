from pathlib import Path
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.search import search_repo, stats

def test_phase1_smoke(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "main.py").write_text("def open_gate():\n    return 'GATE=UP OK'\n", encoding="utf-8")
    (repo / ".env").write_text("SECRET=abc", encoding="utf-8")
    init_storage(repo)
    result = scan_repo(repo)
    assert result["files_indexed"] >= 1
    hits = search_repo(repo, "open_gate")
    assert hits
    assert hits[0]["path"] == "main.py"
    s = stats(repo)
    assert s["file_count"] >= 1
    assert s["symbol_count"] >= 1
