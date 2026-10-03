from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import re


def tree_sitter_rust_available() -> bool:
    try:
        import tree_sitter  # noqa: F401
        import tree_sitter_rust  # noqa: F401
    except Exception:
        return False
    return True


def tree_sitter_go_available() -> bool:
    try:
        import tree_sitter  # noqa: F401
        import tree_sitter_go  # noqa: F401
    except Exception:
        return False
    return True


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def _node_text(node: Any, source: bytes) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def _line(node: Any) -> int:
    return int(node.start_point.row) + 1


def _end_line(node: Any) -> int:
    return int(node.end_point.row) + 1


def _identifier(node: Any, source: bytes) -> str:
    return _node_text(node, source).strip() if node is not None else ""


def _make_parser(language):
    from tree_sitter import Parser

    try:
        return Parser(language)
    except TypeError:
        parser = Parser()
        try:
            parser.language = language
        except AttributeError:
            parser.set_language(language)
        return parser


def _language(kind: str):
    from tree_sitter import Language

    if kind == "rust":
        import tree_sitter_rust as grammar
    else:
        import tree_sitter_go as grammar
    return Language(grammar.language())


def _rust_use_module(text: str) -> str | None:
    match = re.search(r"\buse\s+([^;]+)", text)
    if not match:
        return None
    expr = match.group(1).strip()
    expr = expr.split("{", 1)[0].rstrip(":").strip()
    return expr or None


def _rust_mod_module(text: str) -> str | None:
    match = re.match(r"\s*(?:pub\s+)?mod\s+([A-Za-z_][A-Za-z0-9_]*)\s*;", text)
    return match.group(1) if match else None


def _go_import_module(text: str) -> str | None:
    quoted = re.findall(r'"([^"]+)"', text)
    return quoted[-1] if quoted else None


def _go_receiver_name(text: str) -> str | None:
    match = re.search(r"\(\s*\w+\s+\*?([A-Za-z_][A-Za-z0-9_]*)\s*\)", text)
    return match.group(1) if match else None


def _base_doc(path: Path, repo_root: Path, language: str, text: str) -> dict:
    rel = str(path.relative_to(repo_root)).replace("\\", "/")
    return {
        "path": rel,
        "language": language,
        "sha256": _sha_text(text),
        "line_count": text.count("\n") + 1 if text else 0,
        "imports": [],
        "import_records": [],
        "functions": [],
        "async_functions": [],
        "classes": [],
        "methods": [],
        "calls": [],
        "api_calls": [],
        "routes": [],
        "symbol_locations": [],
        "parse_error": None,
        "parser_engine": "tree_sitter",
    }


def parse_rust_file_tree_sitter(path: Path, repo_root: Path) -> dict:
    if not tree_sitter_rust_available():
        raise RuntimeError("Tree-sitter Rust dependency is not installed")

    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    doc = _base_doc(path, repo_root, "rust", text)
    tree = _make_parser(_language("rust")).parse(raw)

    def add_symbol(name: str, node: Any, kind: str, current_type: str | None = None) -> str:
        qname = f"{current_type}.{name}" if current_type else name
        row = {
            "name": name,
            "qname": qname,
            "lineno": _line(node),
            "end_lineno": _end_line(node),
            "kind": kind,
        }
        target = doc["methods"] if current_type else doc["functions"]
        target.append(row)
        doc["symbol_locations"].append({
            "symbol": qname,
            "kind": "method" if current_type else "function",
            "lineno": row["lineno"],
            "end_lineno": row["end_lineno"],
        })
        return qname

    def walk(node: Any, current_type: str | None = None, current_function: str | None = None) -> None:
        node_type = node.type
        next_type = current_type
        next_function = current_function

        if node_type in {"struct_item", "enum_item", "trait_item"}:
            name = _identifier(node.child_by_field_name("name"), raw)
            if name:
                doc["classes"].append({
                    "name": name,
                    "qname": name,
                    "lineno": _line(node),
                    "end_lineno": _end_line(node),
                    "bases": [],
                })
                doc["symbol_locations"].append({
                    "symbol": name,
                    "kind": "class",
                    "lineno": _line(node),
                    "end_lineno": _end_line(node),
                })

        if node_type == "impl_item":
            target = _identifier(node.child_by_field_name("type"), raw)
            if target:
                next_type = target

        if node_type == "function_item":
            name = _identifier(node.child_by_field_name("name"), raw)
            if name:
                next_function = add_symbol(name, node, "method" if current_type else "function", current_type)

        if node_type == "use_declaration":
            module = _rust_use_module(_node_text(node, raw))
            if module:
                doc["imports"].append(module)
                doc["import_records"].append({
                    "kind": "import",
                    "module": module,
                    "name": None,
                    "alias": None,
                    "level": 0,
                    "lineno": _line(node),
                })

        if node_type == "mod_item":
            module = _rust_mod_module(_node_text(node, raw))
            if module:
                doc["imports"].append(module)
                doc["import_records"].append({
                    "kind": "import",
                    "module": module,
                    "name": None,
                    "alias": None,
                    "level": 0,
                    "lineno": _line(node),
                })

        if node_type == "call_expression":
            function = node.child_by_field_name("function")
            callee = _identifier(function, raw)
            if callee:
                doc["calls"].append({
                    "caller": current_function or "<module>",
                    "callee": callee,
                    "lineno": _line(node),
                })

        for child in node.children:
            walk(child, next_type, next_function)

    walk(tree.root_node)
    doc["imports"] = sorted(set(doc["imports"]))
    doc["functions"] = doc["functions"][:300]
    doc["classes"] = doc["classes"][:120]
    doc["methods"] = doc["methods"][:300]
    doc["calls"] = doc["calls"][:1000]
    doc["symbol_locations"] = doc["symbol_locations"][:1000]
    if tree.root_node.has_error:
        doc["parse_error"] = {"type": "TreeSitterSyntaxError", "message": "parse tree contains syntax errors"}
    return doc


def parse_go_file_tree_sitter(path: Path, repo_root: Path) -> dict:
    if not tree_sitter_go_available():
        raise RuntimeError("Tree-sitter Go dependency is not installed")

    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    doc = _base_doc(path, repo_root, "go", text)
    tree = _make_parser(_language("go")).parse(raw)

    def add_function(name: str, node: Any, receiver: str | None = None) -> str:
        qname = f"{receiver}.{name}" if receiver else name
        row = {
            "name": name,
            "qname": qname,
            "lineno": _line(node),
            "end_lineno": _end_line(node),
            "kind": "method" if receiver else "function",
        }
        (doc["methods"] if receiver else doc["functions"]).append(row)
        doc["symbol_locations"].append({
            "symbol": qname,
            "kind": "method" if receiver else "function",
            "lineno": row["lineno"],
            "end_lineno": row["end_lineno"],
        })
        return qname

    def walk(node: Any, current_function: str | None = None) -> None:
        node_type = node.type
        next_function = current_function

        if node_type == "type_spec":
            name = _identifier(node.child_by_field_name("name"), raw)
            type_node = node.child_by_field_name("type")
            if name and type_node is not None and type_node.type in {"struct_type", "interface_type"}:
                doc["classes"].append({
                    "name": name,
                    "qname": name,
                    "lineno": _line(node),
                    "end_lineno": _end_line(node),
                    "bases": [],
                })
                doc["symbol_locations"].append({
                    "symbol": name,
                    "kind": "class",
                    "lineno": _line(node),
                    "end_lineno": _end_line(node),
                })

        if node_type == "function_declaration":
            name = _identifier(node.child_by_field_name("name"), raw)
            if name:
                next_function = add_function(name, node)

        if node_type == "method_declaration":
            name = _identifier(node.child_by_field_name("name"), raw)
            receiver = _go_receiver_name(_node_text(node, raw))
            if name:
                next_function = add_function(name, node, receiver)

        if node_type == "import_spec":
            module = _go_import_module(_node_text(node, raw))
            if module:
                doc["imports"].append(module)
                doc["import_records"].append({
                    "kind": "import",
                    "module": module,
                    "name": None,
                    "alias": None,
                    "level": 0,
                    "lineno": _line(node),
                })

        if node_type == "call_expression":
            function = node.child_by_field_name("function")
            callee = _identifier(function, raw)
            if callee:
                doc["calls"].append({
                    "caller": current_function or "<module>",
                    "callee": callee,
                    "lineno": _line(node),
                })

        for child in node.children:
            walk(child, next_function)

    walk(tree.root_node)
    doc["imports"] = sorted(set(doc["imports"]))
    doc["functions"] = doc["functions"][:300]
    doc["classes"] = doc["classes"][:120]
    doc["methods"] = doc["methods"][:300]
    doc["calls"] = doc["calls"][:1000]
    doc["symbol_locations"] = doc["symbol_locations"][:1000]
    if tree.root_node.has_error:
        doc["parse_error"] = {"type": "TreeSitterSyntaxError", "message": "parse tree contains syntax errors"}
    return doc


def _skip_path(path: Path) -> bool:
    return any(part in {".uacos", "target", "vendor", ".git", "__pycache__", ".venv"} for part in path.parts)


def parse_repo_rust_tree_sitter(repo_root: Path) -> list[dict]:
    docs = []
    for path in sorted(repo_root.rglob("*.rs")):
        if path.is_file() and not _skip_path(path):
            docs.append(parse_rust_file_tree_sitter(path, repo_root))
    return docs


def parse_repo_go_tree_sitter(repo_root: Path) -> list[dict]:
    docs = []
    for path in sorted(repo_root.rglob("*.go")):
        if path.is_file() and not _skip_path(path):
            docs.append(parse_go_file_tree_sitter(path, repo_root))
    return docs
