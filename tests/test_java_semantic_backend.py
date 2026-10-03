from pathlib import Path

from uacos.ast_engine.language_backends import available_backends, parse_repo_languages
from uacos.ast_engine.tree_sitter_java import parse_java_file_tree_sitter, tree_sitter_java_available
from uacos.graph.builder import build_graph, load_graph


def test_java_tree_sitter_symbols_calls_and_imports(tmp_path: Path):
    repo = tmp_path / "repo"
    src = repo / "src" / "main" / "java" / "com" / "demo"
    src.mkdir(parents=True)
    helper = src / "Helper.java"
    helper.write_text(
        "package com.demo;\npublic class Helper { public static void ping() {} }\n",
        encoding="utf-8",
    )
    app = src / "App.java"
    app.write_text(
        "package com.demo;\n"
        "import com.demo.Helper;\n"
        "public class App {\n"
        "  public void run() { Helper.ping(); }\n"
        "}\n",
        encoding="utf-8",
    )

    assert tree_sitter_java_available() is True
    doc = parse_java_file_tree_sitter(app, repo)
    assert doc["language"] == "java"
    assert any(row["qname"] == "App" for row in doc["classes"])
    assert any(row["qname"] == "App.run" for row in doc["methods"])
    assert any(row["module"] == "com.demo.Helper" for row in doc["import_records"])
    assert any(row["caller"] == "App.run" and row["callee"] == "ping" for row in doc["calls"])

    rows = {row["name"]: row for row in available_backends()}
    assert rows["java"]["available"] is True
    parsed = parse_repo_languages(repo)
    assert any(row["language"] == "java" for row in parsed)

    build_graph(repo)
    graph = load_graph(repo, auto_build=False)
    assert graph["stats"]["language_counts"]["java"] == 2
    assert any(
        edge["source"].endswith("App.java") and edge["target"].endswith("Helper.java")
        for edge in graph["file_edges"]
    )
    symbol_ids = {row["id"] for row in graph["symbols"]}
    assert any(symbol.endswith(":App.run") for symbol in symbol_ids)
    assert any(symbol.endswith(":Helper.ping") for symbol in symbol_ids)
