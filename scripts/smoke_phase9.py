from pathlib import Path
import tempfile
import threading
import urllib.request
import json
from http.server import ThreadingHTTPServer
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.memory.store import add_memory
from uacos.dashboard.server import DashboardHandler
from uacos.dashboard.ops_summary import ops_summary

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"; repo.mkdir()
        (repo / "main.py").write_text("def open_gate():\n    return True\n", encoding="utf-8")
        init_storage(repo); scan_repo(repo)
        add_memory(repo, "project_truth", "barrier_safety", "Lower barrier must obey ROI", tags=["barrier"])
        summary = ops_summary(repo)
        assert summary["active_memory_count"] >= 1

        handler_cls = type("SmokeDashboardHandler", (DashboardHandler,), {"repo_root": repo})
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
        port = server.server_address[1]
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/summary", timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            assert data["repo"] == str(repo)
        finally:
            server.shutdown(); server.server_close()

        print("PHASE9_SMOKE_OK")
        print("repo=", summary["repo"])
        print("memory_count=", summary["memory_count"])

if __name__ == "__main__":
    main()
