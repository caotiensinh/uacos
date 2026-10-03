from pathlib import Path

from uacos.ast_engine.tree_sitter_c_cpp import parse_cpp_file_tree_sitter
from uacos.ast_engine.tree_sitter_java import parse_java_file_tree_sitter
from uacos.graph.builder import build_graph, load_graph


def _edge(graph: dict, source_suffix: str, base: str) -> dict:
    return next(
        row for row in graph["inheritance_edges"]
        if row["source_symbol_id"].endswith(source_suffix) and row["base"] == base
    )


def test_python_inheritance_uses_import_to_disambiguate_duplicate_base(tmp_path: Path):
    repo = tmp_path / "repo"
    pkg = repo / "pkg"
    pkg.mkdir(parents=True)
    (pkg / "a.py").write_text("class Base:\n    pass\n", encoding="utf-8")
    (pkg / "b.py").write_text("class Base:\n    pass\n", encoding="utf-8")
    (pkg / "child.py").write_text(
        "from .a import Base\n\nclass Child(Base):\n    pass\n",
        encoding="utf-8",
    )

    build_graph(repo)
    graph = load_graph(repo, auto_build=False)
    edge = _edge(graph, "pkg.child:Child", "Base")
    assert edge["relation"] == "inherits"
    assert edge["resolution"] == "import_exact"
    assert edge["target_symbol_id"] == "pkg.a:Base"
    assert edge["target_file"] == "pkg/a.py"


def test_java_extends_and_implements_are_normalized_and_resolved(tmp_path: Path):
    repo = tmp_path / "repo"
    src = repo / "src" / "main" / "java" / "com" / "demo"
    src.mkdir(parents=True)
    (src / "Base.java").write_text(
        "package com.demo;\npublic class Base {}\n",
        encoding="utf-8",
    )
    (src / "Task.java").write_text(
        "package com.demo;\npublic interface Task {}\n",
        encoding="utf-8",
    )
    child = src / "Worker.java"
    child.write_text(
        "package com.demo;\n"
        "import com.demo.Base;\n"
        "import com.demo.Task;\n"
        "public class Worker extends Base implements Task {}\n",
        encoding="utf-8",
    )

    parsed = parse_java_file_tree_sitter(child, repo)
    worker = next(row for row in parsed["classes"] if row["name"] == "Worker")
    assert worker["base_records"] == [
        {"name": "Base", "relation": "extends"},
        {"name": "Task", "relation": "implements"},
    ]

    build_graph(repo)
    graph = load_graph(repo, auto_build=False)
    base_edge = _edge(graph, ":Worker", "Base")
    task_edge = _edge(graph, ":Worker", "Task")
    assert base_edge["relation"] == "extends"
    assert base_edge["target_symbol_id"].endswith(":Base")
    assert base_edge["target_file"].endswith("Base.java")
    assert task_edge["relation"] == "implements"
    assert task_edge["target_symbol_id"].endswith(":Task")
    assert task_edge["target_file"].endswith("Task.java")


def test_cpp_inheritance_is_extracted_and_resolved_through_include(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "base.hpp").write_text("class Base {};\n", encoding="utf-8")
    child = repo / "worker.cpp"
    child.write_text(
        '#include "base.hpp"\nclass Worker : public Base { public: void run() {} };\n',
        encoding="utf-8",
    )

    parsed = parse_cpp_file_tree_sitter(child, repo)
    worker = next(row for row in parsed["classes"] if row["name"] == "Worker")
    assert worker["base_records"] == [{"name": "Base", "relation": "inherits"}]

    build_graph(repo)
    graph = load_graph(repo, auto_build=False)
    edge = _edge(graph, "worker:Worker", "Base")
    assert edge["resolution"] == "import_exact"
    assert edge["target_symbol_id"] == "base:Base"
    assert edge["target_file"] == "base.hpp"


def test_ambiguous_unimported_base_is_fail_safe(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / "a").mkdir(parents=True)
    (repo / "b").mkdir(parents=True)
    (repo / "c").mkdir(parents=True)
    (repo / "a" / "base.py").write_text("class Base:\n    pass\n", encoding="utf-8")
    (repo / "b" / "base.py").write_text("class Base:\n    pass\n", encoding="utf-8")
    (repo / "c" / "child.py").write_text("class Child(Base):\n    pass\n", encoding="utf-8")

    build_graph(repo)
    graph = load_graph(repo, auto_build=False)
    edge = _edge(graph, "c.child:Child", "Base")
    assert edge["resolution"] == "ambiguous"
    assert edge["candidate_count"] == 2
    assert edge["target_symbol_id"] is None
    assert graph["stats"]["ambiguous_inheritance_edge_count"] >= 1
