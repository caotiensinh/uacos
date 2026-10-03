from pathlib import Path

from uacos.ast_engine.language_backends import available_backends, parse_repo_languages
from uacos.ast_engine.tree_sitter_rust_go import (
    parse_go_file_tree_sitter,
    parse_rust_file_tree_sitter,
    tree_sitter_go_available,
    tree_sitter_rust_available,
)
from uacos.graph.builder import build_graph, load_graph


def test_rust_tree_sitter_symbols_methods_calls_and_mod_import(tmp_path: Path):
    repo = tmp_path / "repo"
    src = repo / "src"
    src.mkdir(parents=True)
    source = src / "lib.rs"
    source.write_text(
        "mod helper;\n"
        "pub struct Worker {}\n"
        "impl Worker {\n"
        "    pub fn run(&self) { helper::ping(); }\n"
        "}\n",
        encoding="utf-8",
    )

    assert tree_sitter_rust_available() is True
    doc = parse_rust_file_tree_sitter(source, repo)

    assert doc["language"] == "rust"
    assert doc["parser_engine"] == "tree_sitter"
    assert any(row["qname"] == "Worker" for row in doc["classes"])
    assert any(row["qname"] == "Worker.run" for row in doc["methods"])
    assert any(row["caller"] == "Worker.run" and "helper::ping" in row["callee"] for row in doc["calls"])
    assert any(row["module"] == "helper" for row in doc["import_records"])


def test_go_tree_sitter_symbols_receiver_calls_and_import(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    source = repo / "main.go"
    source.write_text(
        "package main\n\n"
        "import \"example.com/demo/pkg\"\n\n"
        "type Worker struct{}\n\n"
        "func (w *Worker) Run() { pkg.Ping() }\n"
        "func main() { w := &Worker{}; w.Run() }\n",
        encoding="utf-8",
    )

    assert tree_sitter_go_available() is True
    doc = parse_go_file_tree_sitter(source, repo)

    assert doc["language"] == "go"
    assert any(row["qname"] == "Worker" for row in doc["classes"])
    assert any(row["qname"] == "Worker.Run" for row in doc["methods"])
    assert any(row["qname"] == "main" for row in doc["functions"])
    assert any(row["module"] == "example.com/demo/pkg" for row in doc["import_records"])
    assert any(row["caller"] == "Worker.Run" and "pkg.Ping" in row["callee"] for row in doc["calls"])


def test_rust_and_go_backends_are_registered_and_graph_rust_mod_edge_resolves(tmp_path: Path):
    repo = tmp_path / "repo"
    src = repo / "src"
    src.mkdir(parents=True)
    (src / "lib.rs").write_text("mod helper;\npub fn boot() { helper::ping(); }\n", encoding="utf-8")
    (src / "helper.rs").write_text("pub fn ping() {}\n", encoding="utf-8")
    (repo / "main.go").write_text("package main\nfunc main() {}\n", encoding="utf-8")

    rows = {row["name"]: row for row in available_backends()}
    assert rows["rust"]["available"] is True
    assert rows["go"]["available"] is True

    parsed = parse_repo_languages(repo)
    assert {doc["language"] for doc in parsed} >= {"rust", "go"}

    build_graph(repo)
    graph = load_graph(repo, auto_build=False)
    assert graph["stats"]["language_counts"]["rust"] == 2
    assert graph["stats"]["language_counts"]["go"] == 1
    assert any(
        edge["source"] == "src/lib.rs" and edge["target"] == "src/helper.rs"
        for edge in graph["file_edges"]
    )
    assert "src.lib:boot" in {row["id"] for row in graph["symbols"]}
    assert "src.helper:ping" in {row["id"] for row in graph["symbols"]}
