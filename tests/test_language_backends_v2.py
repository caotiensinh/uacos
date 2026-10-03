from pathlib import Path

from uacos.ast_engine.language_backends import available_backends, parse_repo_languages
from uacos.graph.builder import build_graph, load_graph
from uacos.graph.query import query_symbol


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_backend_registry_exposes_python_and_js_ts():
    backends = {row["name"]: row for row in available_backends()}
    assert backends["python_ast"]["semantic_level"] == "native_ast"
    assert set(backends["javascript_typescript"]["languages"]) == {"javascript", "typescript"}
    assert backends["javascript_typescript"]["semantic_level"] == "tree_sitter_ast"
    assert backends["javascript_typescript"]["parser_engine"] == "tree_sitter"
    assert backends["javascript_typescript"]["available"] is True


def test_parse_repo_languages_combines_python_and_typescript(tmp_path: Path):
    _write(tmp_path, "pkg/a.py", "def py_helper():\n    return 1\n")
    _write(tmp_path, "src/b.ts", "export function tsHelper() { return 2 }\n")

    parsed = parse_repo_languages(tmp_path)
    by_path = {row["path"]: row for row in parsed}

    assert by_path["pkg/a.py"]["backend"] == "python_ast"
    assert by_path["pkg/a.py"]["semantic_level"] == "native_ast"
    assert by_path["src/b.ts"]["backend"] == "javascript_typescript"
    assert by_path["src/b.ts"]["semantic_level"] == "tree_sitter_ast"
    assert by_path["src/b.ts"]["parser_engine"] == "tree_sitter"


def test_semantic_graph_resolves_typescript_relative_import(tmp_path: Path):
    _write(tmp_path, "src/b.ts", "export function helper() { return 1 }\n")
    _write(
        tmp_path,
        "src/a.ts",
        "import { helper } from './b'\n"
        "export function useHelper() { return helper() }\n",
    )

    result = build_graph(tmp_path)
    assert result["status"] == "ok"
    graph = load_graph(tmp_path, auto_build=False)

    assert graph["stats"]["language_counts"]["typescript"] == 2
    assert graph["stats"]["backend_counts"]["javascript_typescript"] == 2

    ids = {row["id"] for row in graph["symbols"]}
    assert "src.a:useHelper" in ids
    assert "src.b:helper" in ids

    imports = [
        edge for edge in graph["file_edges"]
        if edge["source"] == "src/a.ts" and edge["target"] == "src/b.ts"
    ]
    assert len(imports) == 1
    assert imports[0]["language"] == "typescript"

    helper = query_symbol(tmp_path, "src.b:helper")
    assert helper["ambiguous"] is False
    assert helper["matches"][0]["symbol_id"] == "src.b:helper"

    calls = [
        edge for edge in graph["call_edges"]
        if edge["source_file"] == "src/a.ts" and edge["callee"] == "helper"
    ]
    assert calls
    assert calls[0]["target_symbol_id"] == "src.b:helper"
    assert calls[0]["target_file"] == "src/b.ts"
