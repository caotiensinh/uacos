from pathlib import Path
import threading
import time
import urllib.request
import json
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.memory.store import add_memory
from uacos.dashboard.ops_summary import ops_summary
from uacos.dashboard.server import dashboard_html, DashboardHandler
from http.server import ThreadingHTTPServer

def test_phase9_ops_summary_and_html(tmp_path: Path):
    repo = tmp_path / "repo"; repo.mkdir()
    (repo / "app.py").write_text("def open_gate():\n    return True\n", encoding="utf-8")
    init_storage(repo); scan_repo(repo)
    add_memory(repo, "project_truth", "barrier", "Barrier lower obeys safe ROI", tags=["barrier"])
    summary = ops_summary(repo)
    assert summary["repo"] == str(repo)
    assert summary["memory_count"] >= 1
    html = dashboard_html(repo, "vi")
    assert "UACOS" in html
    assert "Bảng điều khiển" in html

def test_phase9_http_api(tmp_path: Path):
    repo = tmp_path / "repo"; repo.mkdir()
    (repo / "app.py").write_text("def open_gate():\n    return True\n", encoding="utf-8")
    init_storage(repo); scan_repo(repo)
    handler_cls = type("TestDashboardHandler", (DashboardHandler,), {"repo_root": repo})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
    port = server.server_address[1]
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/summary", timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        assert data["repo"] == str(repo)
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/search?q=open_gate", timeout=5) as resp:
            search = json.loads(resp.read().decode("utf-8"))
        assert search["results"]
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5) as resp:
            page = resp.read().decode("utf-8")
        assert "UACOS Operations Dashboard" in page
    finally:
        server.shutdown()
        server.server_close()
