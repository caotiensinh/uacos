from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import re


def tree_sitter_java_available() -> bool:
    try:
        import tree_sitter  # noqa: F401
        import tree_sitter_java  # noqa: F401
    except Exception:
        return False
    return True


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def _node_text(node: Any, source: bytes) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def _identifier(node: Any, source: bytes) -> str:
    return _node_text(node, source).strip() if node is not None else ""


def _line(node: Any) -> int:
    return int(node.start_point.row) + 1


def _end_line(node: Any) -> int:
    return int(node.end_point.row) + 1


def _language():
    from tree_sitter import Language
    import tree_sitter_java
    return Language(tree_sitter_java.language())


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


def _import_name(text: str) -> str | None:
    match = re.match(r"\s*import\s+(?:static\s+)?([A-Za-z0-9_.$*]+)\s*;", text)
    return match.group(1).rstrip(".*") if match else None


def _clean_java_type(value: str) -> str:
    value = re.sub(r"<[^<>]*>", "", value.strip())
    value = value.replace("$", ".")
    return value.strip()


def _split_java_types(value: str) -> list[str]:
    return [cleaned for part in value.split(",") if (cleaned := _clean_java_type(part))]


def _base_records(node: Any, source: bytes) -> list[dict]:
    """Return normalized extends/implements relations from a Java type declaration."""
    text = _node_text(node, source).split("{", 1)[0]
    rows: list[dict] = []

    extends_match = re.search(r"\bextends\s+(.+?)(?=\bimplements\b|$)", text, re.DOTALL)
    if extends_match:
        for name in _split_java_types(extends_match.group(1)):
            rows.append({"name": name, "relation": "extends"})

    implements_match = re.search(r"\bimplements\s+(.+)$", text, re.DOTALL)
    if implements_match:
        for name in _split_java_types(implements_match.group(1)):
            rows.append({"name": name, "relation": "implements"})
    return rows


def parse_java_file_tree_sitter(path: Path, repo_root: Path) -> dict:
    if not tree_sitter_java_available():
        raise RuntimeError("Tree-sitter Java dependency is not installed")
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    rel = str(path.relative_to(repo_root)).replace("\\", "/")
    doc = {
        "path": rel,
        "language": "java",
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
    tree = _make_parser(_language()).parse(raw)

    def walk(node: Any, current_type: str | None = None, current_method: str | None = None) -> None:
        node_type = node.type
        next_type = current_type
        next_method = current_method
        if node_type in {"class_declaration", "interface_declaration", "enum_declaration", "record_declaration"}:
            name = _identifier(node.child_by_field_name("name"), raw)
            if name:
                next_type = name
                base_records = _base_records(node, raw)
                row = {
                    "name": name,
                    "qname": name,
                    "lineno": _line(node),
                    "end_lineno": _end_line(node),
                    "bases": [record["name"] for record in base_records],
                    "base_records": base_records,
                    "type_kind": node_type.removesuffix("_declaration"),
                }
                doc["classes"].append(row)
                doc["symbol_locations"].append({"symbol": name, "kind": "class", "lineno": row["lineno"], "end_lineno": row["end_lineno"]})
        if node_type in {"method_declaration", "constructor_declaration"}:
            name = _identifier(node.child_by_field_name("name"), raw)
            if name:
                qname = f"{current_type}.{name}" if current_type else name
                row = {"name": name, "qname": qname, "lineno": _line(node), "end_lineno": _end_line(node), "kind": "method"}
                doc["methods"].append(row)
                doc["symbol_locations"].append({"symbol": qname, "kind": "method", "lineno": row["lineno"], "end_lineno": row["end_lineno"]})
                next_method = qname
        if node_type == "import_declaration":
            module = _import_name(_node_text(node, raw))
            if module:
                doc["imports"].append(module)
                doc["import_records"].append({"kind": "import", "module": module, "name": None, "alias": None, "level": 0, "lineno": _line(node)})
        if node_type in {"method_invocation", "object_creation_expression"}:
            name = node.child_by_field_name("name") or node.child_by_field_name("type")
            callee = _identifier(name, raw)
            if callee:
                doc["calls"].append({"caller": current_method or "<module>", "callee": callee, "lineno": _line(node)})
        for child in node.children:
            walk(child, next_type, next_method)

    walk(tree.root_node)
    doc["imports"] = sorted(set(doc["imports"]))
    doc["classes"] = doc["classes"][:200]
    doc["methods"] = doc["methods"][:600]
    doc["calls"] = doc["calls"][:1500]
    doc["symbol_locations"] = doc["symbol_locations"][:1500]
    if tree.root_node.has_error:
        doc["parse_error"] = {"type": "TreeSitterSyntaxError", "message": "parse tree contains syntax errors"}
    return doc


def _skip_path(path: Path) -> bool:
    return any(part in {".uacos", "target", "build", "vendor", ".git", "__pycache__", ".venv"} for part in path.parts)


def parse_repo_java_tree_sitter(repo_root: Path) -> list[dict]:
    docs = []
    for path in sorted(repo_root.rglob("*.java")):
        if path.is_file() and not _skip_path(path):
            docs.append(parse_java_file_tree_sitter(path, repo_root))
    return docs
