from pathlib import Path
import tempfile
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.search import search_repo, search_symbols, stats
from uacos.codeintel.repo_map import get_repo_map
from uacos.retrieval.context_pack import build_context_pack

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "sample_repo"
        repo.mkdir()
        (repo / "main.py").write_text(
            "class BarrierService:\n"
            "    def open_gate(self):\n"
            "        return 'GATE=UP OK'\n\n"
            "def health():\n"
            "    return 'ok'\n",
            encoding="utf-8",
        )
        (repo / "dashboard.html").write_text("<button id='openGateBtn' class='danger action'>開門</button>\n", encoding="utf-8")
        init_storage(repo)
        scan = scan_repo(repo)
        hits = search_repo(repo, "open gate")
        syms = search_symbols(repo, "open_gate")
        repomap = get_repo_map(repo, "open gate")
        pack = build_context_pack(repo, "Fix open gate button")
        assert scan["files_indexed"] == 2
        assert scan["symbols_indexed"] >= 2
        assert hits
        assert syms
        assert "BarrierService" in repomap or "open_gate" in repomap
        assert pack["id"]
        print("PHASE2_SMOKE_OK")
        print("scan=", scan)
        print("stats=", stats(repo))
        print("context_id=", pack["id"])

if __name__ == "__main__":
    main()
