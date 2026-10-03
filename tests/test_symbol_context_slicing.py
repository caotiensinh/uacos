from pathlib import Path

from uacos.context.slicer import slice_symbol, slice_symbols
from uacos.graph.builder import build_graph
from uacos.impact.analyzer import smart_context


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_slice_symbol_extracts_target_body_not_whole_file(tmp_path: Path):
    _write(
        tmp_path,
        "pkg/service.py",
        "def unrelated_before():\n"
        "    return 'before'\n\n"
        "def target(value):\n"
        "    checked = value + 1\n"
        "    return checked\n\n"
        "def unrelated_after():\n"
        "    return 'after'\n",
    )
    build_graph(tmp_path)

    row = slice_symbol(tmp_path, "pkg.service:target", padding=0)

    assert row["status"] == "ok"
    assert row["symbol_start_line"] == 4
    assert "def target(value):" in row["content"]
    assert "return checked" in row["content"]
    assert "unrelated_before" not in row["content"]
    assert "unrelated_after" not in row["content"]


def test_slice_symbol_uses_next_symbol_when_end_line_missing(tmp_path: Path):
    _write(
        tmp_path,
        "pkg/mod.py",
        "def first():\n"
        "    return 1\n\n"
        "def second():\n"
        "    return 2\n",
    )
    build_graph(tmp_path)
    graph_path = tmp_path / ".uacos" / "graph" / "dependency_graph.json"
    import json

    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    for symbol in graph["symbols"]:
        if symbol["id"] == "pkg.mod:first":
            symbol["end_lineno"] = None
    graph_path.write_text(json.dumps(graph), encoding="utf-8")

    row = slice_symbol(tmp_path, "pkg.mod:first", padding=0)

    assert row["status"] == "ok"
    assert row["end_line"] == 3
    assert "def second" not in row["content"]


def test_slice_symbols_deduplicates_same_source_range(tmp_path: Path):
    _write(
        tmp_path,
        "pkg/service.py",
        "class Worker:\n"
        "    def run(self):\n"
        "        return 1\n",
    )
    build_graph(tmp_path)

    result = slice_symbols(
        tmp_path,
        ["pkg.service:Worker", "pkg.service:Worker.run", "pkg.service:Worker.run"],
        padding=0,
    )

    assert result["status"] == "ok"
    assert result["slice_count"] >= 1
    assert len({(x["file"], x["start_line"], x["end_line"]) for x in result["slices"]}) == result["slice_count"]


def test_smart_context_prefers_symbol_slice_over_large_file_head(tmp_path: Path):
    filler = "\n".join(f"FILLER_{i} = {i}" for i in range(220))
    _write(
        tmp_path,
        "pkg/service.py",
        filler
        + "\n\ndef critical_handler(value):\n"
        + "    result = value * 2\n"
        + "    return result\n",
    )
    build_graph(tmp_path)

    result = smart_context(tmp_path, "fix pkg.service:critical_handler", max_files=2, max_chars=7000)

    assert result["status"] == "ok"
    assert result["context_model"] == "semantic_symbol_slices_v1"
    assert result["symbol_slice_count"] >= 1
    assert "critical_handler" in result["content"]
    assert "FILLER_0" not in result["content"]
    assert any(
        row.get("symbol_id") == "pkg.service:critical_handler" and row.get("mode") == "symbol_slice"
        for row in result["included_context"]
    )
