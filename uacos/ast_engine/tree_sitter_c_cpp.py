from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import re


C_EXTENSIONS = {".c", ".h"}
CPP_EXTENSIONS = {".cc", ".cpp", ".cxx", ".hh", ".hpp", ".hxx"}


def tree_sitter_c_available() -> bool:
    try:
        import tree_sitter  # noqa: F401
        import tree_sitter_c  # noqa: F401
    except Exception:
        return False
    return True


def tree_sitter_cpp_available() -> bool:
    try:
        import tree_sitter  # noqa: F401
        import tree_sitter_cpp  # noqa: F401
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
    if kind == "c":
        import tree_sitter_c as grammar
    else:
        import tree_sitter_cpp as grammar
    return Language(grammar.language())


def _declarator_name(node: Any, source: bytes) -> str:
    """Resolve a declared symbol without descending into parameter names."""
    if node is None:
        return ""
    if node.type in {"identifier", "field_identifier", "operator_name", "destructor_name", "type_identifier"}:
        return _node_text(node, source).strip()
    for field in ("name", "declarator"):
        child = node.child_by_field_name(field)
        if child is not None and child is not node:
            name = _declarator_name(child, source)
            if name:
                return name
    ignored = {
        "parameter_list",
        "argument_list",
        "template_parameter_list",
        "template_argument_list",
        "requires_clause",
    }
    for child in node.children:
        if child.type in ignored:
            continue
        name = _declarator_name(child, source)
        if name:
            return name
    return ""


def _include_module(text: str) -> str | None:
    match = re.search(r"#\s*include\s*[<\"]([^>\"]+)[>\"]", text)
    if not match:
        return None
    value = match.group(1).strip().replace("\\", "/")
    suffix = Path(value).suffix.lower()
    if suffix in C_EXTENSIONS | CPP_EXTENSIONS:
        value = value[: -len(suffix)]
    return value.replace("/", ".") or None


def _clean_cpp_type(value: str) -> str:
    value = re.sub(r"\b(public|protected|private|virtual)\b", " ", value)
    value = re.sub(r"<[^<>]*>", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value.replace("::", ".")


def _cpp_base_records(node: Any, source: bytes) -> list[dict]:
    header = _node_text(node, source).split("{", 1)[0]
    if ":" not in header:
        return []
    value = header.split(":", 1)[1]
    rows = []
    for part in value.split(","):
        name = _clean_cpp_type(part)
        if name:
            rows.append({"name": name, "relation": "inherits"})
    return rows


def _base_doc(path: Path, repo_root: Path, language: str, text: str) -> dict:
    return {
        "path": str(path.relative_to(repo_root)).replace("\\", "/"),
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


def _parse_file(path: Path, repo_root: Path, language: str) -> dict:
    available = tree_sitter_c_available if language == "c" else tree_sitter_cpp_available
    if not available():
        raise RuntimeError(f"Tree-sitter {language.upper()} dependency is not installed")
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    doc = _base_doc(path, repo_root, language, text)
    tree = _make_parser(_language(language)).parse(raw)

    def walk(node: Any, current_type: str | None = None, current_function: str | None = None) -> None:
        node_type = node.type
        next_type = current_type
        next_function = current_function

        if node_type in {"class_specifier", "struct_specifier", "union_specifier"}:
            name_node = node.child_by_field_name("name")
            name = _node_text(name_node, raw).strip() if name_node is not None else ""
            if name:
                next_type = name
                base_records = _cpp_base_records(node, raw) if language == "cpp" else []
                row = {
                    "name": name,
                    "qname": name,
                    "lineno": _line(node),
                    "end_lineno": _end_line(node),
                    "bases": [record["name"] for record in base_records],
                    "base_records": base_records,
                    "type_kind": node_type.removesuffix("_specifier"),
                }
                doc["classes"].append(row)
                doc["symbol_locations"].append({"symbol": name, "kind": "class", "lineno": row["lineno"], "end_lineno": row["end_lineno"]})

        if node_type == "function_definition":
            name = _declarator_name(node.child_by_field_name("declarator"), raw)
            if name:
                qname = f"{current_type}.{name}" if current_type else name
                row = {
                    "name": name,
                    "qname": qname,
                    "lineno": _line(node),
                    "end_lineno": _end_line(node),
                    "kind": "method" if current_type else "function",
                }
                (doc["methods"] if current_type else doc["functions"]).append(row)
                doc["symbol_locations"].append({"symbol": qname, "kind": row["kind"], "lineno": row["lineno"], "end_lineno": row["end_lineno"]})
                next_function = qname

        if node_type == "preproc_include":
            module = _include_module(_node_text(node, raw))
            if module:
                doc["imports"].append(module)
                doc["import_records"].append({"kind": "include", "module": module, "name": None, "alias": None, "level": 0, "lineno": _line(node)})

        if node_type == "call_expression":
            function = node.child_by_field_name("function")
            callee = _node_text(function, raw).strip() if function is not None else ""
            if callee:
                doc["calls"].append({"caller": current_function or "<module>", "callee": callee, "lineno": _line(node)})

        for child in node.children:
            walk(child, next_type, next_function)

    walk(tree.root_node)
    doc["imports"] = sorted(set(doc["imports"]))
    doc["functions"] = doc["functions"][:500]
    doc["classes"] = doc["classes"][:250]
    doc["methods"] = doc["methods"][:700]
    doc["calls"] = doc["calls"][:2000]
    doc["symbol_locations"] = doc["symbol_locations"][:2000]
    if tree.root_node.has_error:
        doc["parse_error"] = {"type": "TreeSitterSyntaxError", "message": "parse tree contains syntax errors"}
    return doc


def parse_c_file_tree_sitter(path: Path, repo_root: Path) -> dict:
    return _parse_file(path, repo_root, "c")


def parse_cpp_file_tree_sitter(path: Path, repo_root: Path) -> dict:
    return _parse_file(path, repo_root, "cpp")


def _skip_path(path: Path) -> bool:
    return any(part in {".uacos", "build", "out", "vendor", ".git", "__pycache__", ".venv"} for part in path.parts)


def parse_repo_c_tree_sitter(repo_root: Path) -> list[dict]:
    docs = []
    for ext in sorted(C_EXTENSIONS):
        for path in sorted(repo_root.rglob(f"*{ext}")):
            if path.is_file() and not _skip_path(path):
                docs.append(parse_c_file_tree_sitter(path, repo_root))
    return sorted(docs, key=lambda row: row["path"])


def parse_repo_cpp_tree_sitter(repo_root: Path) -> list[dict]:
    docs = []
    for ext in sorted(CPP_EXTENSIONS):
        for path in sorted(repo_root.rglob(f"*{ext}")):
            if path.is_file() and not _skip_path(path):
                docs.append(parse_cpp_file_tree_sitter(path, repo_root))
    return sorted(docs, key=lambda row: row["path"])
