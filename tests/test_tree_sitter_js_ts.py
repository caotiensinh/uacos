from pathlib import Path

from uacos.ast_engine.language_backends import available_backends, parse_repo_languages
from uacos.ast_engine.tree_sitter_js_ts import (
    parse_js_ts_file_tree_sitter,
    tree_sitter_available,
)


def _write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_tree_sitter_dependencies_available_in_test_environment():
    assert tree_sitter_available() is True
    rows = {row["name"]: row for row in available_backends()}
    assert rows["javascript_typescript"]["available"] is True
    assert rows["javascript_typescript"]["semantic_level"] == "tree_sitter_ast"
    assert rows["javascript_typescript"]["parser_engine"] == "tree_sitter"


def test_tree_sitter_typescript_extracts_symbols_imports_and_callers(tmp_path: Path):
    _write(tmp_path, "src/helper.ts", "export function helper(): number { return 1; }\n")
    app = _write(
        tmp_path,
        "src/app.ts",
        "import { helper } from './helper';\n"
        "export class Runner {\n"
        "  run(): number { return helper(); }\n"
        "}\n"
        "export const boot = () => helper();\n",
    )

    doc = parse_js_ts_file_tree_sitter(app, repo_root=tmp_path)
    assert doc["parser_engine"] == "tree_sitter"
    assert doc["parse_error"] is None
    assert "./helper" in doc["imports"]

    class_names = {row["name"] for row in doc["classes"]}
    method_names = {row["qname"] for row in doc["methods"]}
    function_names = {row["qname"] for row in doc["functions"]}
    assert "Runner" in class_names
    assert "Runner.run" in method_names
    assert "boot" in function_names

    helper_calls = [row for row in doc["calls"] if row["callee"] == "helper"]
    assert {row["caller"] for row in helper_calls} == {"Runner.run", "boot"}


def test_tree_sitter_backend_is_authoritative_when_installed(tmp_path: Path):
    _write(tmp_path, "src/b.ts", "export function helper() { return 1; }\n")
    _write(
        tmp_path,
        "src/a.ts",
        "import { helper } from './b';\n"
        "export function useHelper() { return helper(); }\n",
    )
    docs = parse_repo_languages(tmp_path)
    ts_docs = [row for row in docs if row["language"] == "typescript"]
    assert len(ts_docs) == 2
    assert {row["backend"] for row in ts_docs} == {"javascript_typescript"}
    assert {row["semantic_level"] for row in ts_docs} == {"tree_sitter_ast"}
    assert {row["parser_engine"] for row in ts_docs} == {"tree_sitter"}


def test_tree_sitter_handles_jsx_and_tsx(tmp_path: Path):
    jsx = _write(
        tmp_path,
        "ui/view.jsx",
        "export function View() { return <div>Hello</div>; }\n",
    )
    tsx = _write(
        tmp_path,
        "ui/widget.tsx",
        "export const Widget = () => <span>World</span>;\n",
    )
    jsx_doc = parse_js_ts_file_tree_sitter(jsx, repo_root=tmp_path)
    tsx_doc = parse_js_ts_file_tree_sitter(tsx, repo_root=tmp_path)
    assert jsx_doc["parse_error"] is None
    assert tsx_doc["parse_error"] is None
    assert {row["name"] for row in jsx_doc["functions"]} == {"View"}
    assert {row["name"] for row in tsx_doc["functions"]} == {"Widget"}
