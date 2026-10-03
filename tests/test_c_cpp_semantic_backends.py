from pathlib import Path

from uacos.ast_engine.language_backends import available_backends, parse_repo_languages
from uacos.ast_engine.tree_sitter_c_cpp import parse_c_file_tree_sitter, parse_cpp_file_tree_sitter, tree_sitter_c_available, tree_sitter_cpp_available
from uacos.graph.builder import build_graph, load_graph

def test_c_tree_sitter_functions_calls_and_include(tmp_path: Path):
    repo = tmp_path / "repo"; src = repo / "src"; src.mkdir(parents=True)
    (src / "helper.h").write_text("void helper(void);\n", encoding="utf-8")
    source = src / "main.c"; source.write_text('#include "helper.h"\nvoid helper(void) {}\nint add(int left, int right) { return left + right; }\nint main(void) { helper(); return add(1, 2); }\n', encoding="utf-8")
    assert tree_sitter_c_available() is True
    doc = parse_c_file_tree_sitter(source, repo); assert doc["language"] == "c"; qnames = {row["qname"] for row in doc["functions"]}
    assert {"helper", "add", "main"} <= qnames; assert "left" not in qnames; assert "right" not in qnames
    assert any(row["module"] == "helper" for row in doc["import_records"])
    assert any(row["caller"] == "main" and row["callee"] == "helper" for row in doc["calls"])
    assert any(row["caller"] == "main" and row["callee"] == "add" for row in doc["calls"])

def test_cpp_tree_sitter_class_method_and_call(tmp_path: Path):
    repo = tmp_path / "repo"; repo.mkdir(); source = repo / "worker.cpp"
    source.write_text("class Worker { public: void ping() {} void run(int count) { ping(); } };\n", encoding="utf-8")
    assert tree_sitter_cpp_available() is True
    doc = parse_cpp_file_tree_sitter(source, repo); assert doc["language"] == "cpp"
    assert any(row["qname"] == "Worker" for row in doc["classes"]); assert any(row["qname"] == "Worker.run" for row in doc["methods"]); assert not any(row["qname"] == "Worker.count" for row in doc["methods"]); assert any(row["caller"] == "Worker.run" and row["callee"] == "ping" for row in doc["calls"])

def test_c_cpp_backends_registered_and_include_graph_resolves(tmp_path: Path):
    repo = tmp_path / "repo"; src = repo / "src"; src.mkdir(parents=True)
    (src / "helper.h").write_text("void helper(void);\n", encoding="utf-8"); (src / "main.c").write_text('#include "helper.h"\nint main(void) { return 0; }\n', encoding="utf-8"); (repo / "demo.cpp").write_text("int boot() { return 0; }\n", encoding="utf-8")
    rows = {row["name"]: row for row in available_backends()}; assert rows["c"]["available"] is True; assert rows["cpp"]["available"] is True
    parsed = parse_repo_languages(repo); assert {row["language"] for row in parsed} >= {"c", "cpp"}
    build_graph(repo); graph = load_graph(repo, auto_build=False); assert graph["stats"]["language_counts"]["c"] == 2; assert graph["stats"]["language_counts"]["cpp"] == 1
    assert any(edge["source"] == "src/main.c" and edge["target"] == "src/helper.h" for edge in graph["file_edges"])
