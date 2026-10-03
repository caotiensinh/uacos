from pathlib import Path

from uacos.graph.builder import build_graph, load_graph
from uacos.graph.query import query_symbol


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_semantic_graph_preserves_duplicate_symbol_identity(tmp_path: Path):
    _write(tmp_path, "pkg/__init__.py", "")
    _write(
        tmp_path,
        "pkg/a.py",
        "from .b import helper\n\n"
        "class Worker:\n"
        "    def run(self):\n"
        "        return helper()\n",
    )
    _write(
        tmp_path,
        "pkg/b.py",
        "def helper():\n"
        "    return 1\n\n"
        "class Worker:\n"
        "    def run(self):\n"
        "        return 2\n",
    )

    result = build_graph(tmp_path)
    assert result["status"] == "ok"

    graph = load_graph(tmp_path, auto_build=False)
    assert graph["version"] == 2

    ids = {row["id"] for row in graph["symbols"]}
    assert "pkg.a:Worker.run" in ids
    assert "pkg.b:Worker.run" in ids
    assert "pkg.b:helper" in ids

    duplicate = query_symbol(tmp_path, "Worker.run")
    assert duplicate["ambiguous"] is True
    assert {m["symbol_id"] for m in duplicate["matches"]} == {
        "pkg.a:Worker.run",
        "pkg.b:Worker.run",
    }

    exact = query_symbol(tmp_path, "pkg.a:Worker.run")
    assert exact["ambiguous"] is False
    assert [m["symbol_id"] for m in exact["matches"]] == ["pkg.a:Worker.run"]


def test_semantic_graph_resolves_relative_import_and_unambiguous_call(tmp_path: Path):
    _write(tmp_path, "pkg/__init__.py", "")
    _write(tmp_path, "pkg/b.py", "def helper():\n    return 1\n")
    _write(
        tmp_path,
        "pkg/a.py",
        "from .b import helper\n\n"
        "def use_helper():\n"
        "    return helper()\n",
    )

    build_graph(tmp_path)
    graph = load_graph(tmp_path, auto_build=False)

    import_edges = [
        edge
        for edge in graph["file_edges"]
        if edge["source"] == "pkg/a.py" and edge["target"] == "pkg/b.py"
    ]
    assert import_edges
    assert import_edges[0]["import"] == "pkg.b.helper"
    assert import_edges[0]["level"] == 1

    helper_calls = [
        edge
        for edge in graph["call_edges"]
        if edge["source_file"] == "pkg/a.py" and edge["callee"] == "helper"
    ]
    assert len(helper_calls) == 1
    assert helper_calls[0]["target_symbol_id"] == "pkg.b:helper"
    assert helper_calls[0]["target_file"] == "pkg/b.py"
    assert helper_calls[0]["resolution"] == "exact_or_unambiguous_alias"
