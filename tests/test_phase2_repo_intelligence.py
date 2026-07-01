from pathlib import Path
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.search import search_symbols
from uacos.codeintel.snippet import extract_snippet
from uacos.codeintel.repo_map import get_repo_map
from uacos.retrieval.context_pack import build_context_pack

def test_phase2_symbols_snippets_repomap_context(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "gate.py").write_text(
        "class GateTcpClient:\n"
        "    def send_command(self, command: str):\n"
        "        return f'GATE={command} OK'\n\n"
        "def open_gate():\n"
        "    client = GateTcpClient()\n"
        "    return client.send_command('UP')\n",
        encoding="utf-8",
    )
    (repo / "frontend.js").write_text(
        "export function manualOpen() {\n"
        "  return fetch('/api/barrier/open');\n"
        "}\n\n"
        "const liveMonitor = () => {\n"
        "  return 'LIVE MONITOR';\n"
        "};\n",
        encoding="utf-8",
    )
    init_storage(repo)
    scan = scan_repo(repo)
    assert scan["files_indexed"] == 2
    assert scan["symbols_indexed"] >= 4
    assert any(s["name"] == "open_gate" for s in search_symbols(repo, "open_gate"))
    assert any(s["name"] == "manualOpen" for s in search_symbols(repo, "manualOpen"))
    snip = extract_snippet(repo, "gate.py", 1, 5, context=0)
    assert "GateTcpClient" in snip["content"]
    assert "send_command" in snip["content"]
    repomap = get_repo_map(repo, query="open gate", max_tokens=1200)
    assert "Repo Map" in repomap
    assert "open_gate" in repomap or "manualOpen" in repomap
    pack = build_context_pack(repo, "Fix open gate button on live monitor", max_tokens=2500)
    assert pack["id"]
    assert "Context Pack" in pack["content"]
    assert "Repo Map" in pack["content"]
    assert "Search Hits" in pack["content"]
