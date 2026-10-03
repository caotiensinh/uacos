from __future__ import annotations

from pathlib import Path
import hashlib
import re
from typing import Any


def tree_sitter_available() -> bool:
    try:
        import tree_sitter  # noqa: F401
        import tree_sitter_javascript  # noqa: F401
        import tree_sitter_typescript  # noqa: F401
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
    if node is None:
        return ""
    return _node_text(node, source).strip()


def _module_from_import_text(text: str) -> str | None:
    match = re.search(r"\bfrom\s+['\"]([^'\"]+)['\"]", text)
    if match:
        return match.group(1)
    match = re.search(r"^\s*import\s+['\"]([^'\"]+)['\"]", text)
    if match:
        return match.group(1)
    return None


def _module_from_require_text(text: str) -> str | None:
    match = re.search(r"\brequire\s*\(\s*['\"]([^'\"]+)['\"]\s*\)", text)
    return match.group(1) if match else None


def _language_for_suffix(suffix: str):
    from tree_sitter import Language

    if suffix in {".js", ".jsx"}:
        import tree_sitter_javascript as grammar
        return Language(grammar.language())

    import tree_sitter_typescript as grammar
    if suffix == ".tsx":
        return Language(grammar.language_tsx())
    return Language(grammar.language_typescript())


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


def parse_js_ts_file_tree_sitter(path: Path, repo_root: Path | None = None) -> dict:
    if not tree_sitter_available():
        raise RuntimeError("Tree-sitter JS/TS dependencies are not installed")

    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    rel = str(path.relative_to(repo_root)).replace("\\", "/") if repo_root else str(path)
    suffix = path.suffix.lower()
    language_name = "javascript" if suffix in {".js", ".jsx"} else "typescript"
    parser = _make_parser(_language_for_suffix(suffix))
    tree = parser.parse(raw)

    imports: list[str] = []
    import_records: list[dict] = []
    functions: list[dict] = []
    async_functions: list[dict] = []
    classes: list[dict] = []
    methods: list[dict] = []
    calls: list[dict] = []
    symbol_locations: list[dict] = []

    def add_function(name: str, node: Any, kind: str, current_class: str | None = None) -> str:
        qname = f"{current_class}.{name}" if current_class else name
        row = {
            "name": name,
            "qname": qname,
            "lineno": _line(node),
            "end_lineno": _end_line(node),
            "kind": kind,
            "async": "async" in _node_text(node, raw).split("{", 1)[0],
        }
        if current_class:
            methods.append(row)
        elif row["async"]:
            async_functions.append(row)
        else:
            functions.append(row)
        symbol_locations.append({
            "symbol": qname,
            "kind": "method" if current_class else "function",
            "lineno": row["lineno"],
            "end_lineno": row["end_lineno"],
        })
        return qname

    def walk(node: Any, current_class: str | None = None, current_function: str | None = None) -> None:
        node_type = node.type
        next_class = current_class
        next_function = current_function

        if node_type in {"import_statement", "export_statement"}:
            statement = _node_text(node, raw)
            module = _module_from_import_text(statement)
            if module:
                imports.append(module)
                import_records.append({
                    "kind": "import",
                    "module": module,
                    "name": None,
                    "alias": None,
                    "level": 0,
                    "lineno": _line(node),
                })

        if node_type == "class_declaration":
            name = _identifier(node.child_by_field_name("name"), raw)
            if name:
                classes.append({
                    "name": name,
                    "qname": name,
                    "lineno": _line(node),
                    "end_lineno": _end_line(node),
                    "bases": [],
                })
                symbol_locations.append({
                    "symbol": name,
                    "kind": "class",
                    "lineno": _line(node),
                    "end_lineno": _end_line(node),
                })
                next_class = name

        if node_type in {"function_declaration", "generator_function_declaration"}:
            name = _identifier(node.child_by_field_name("name"), raw)
            if name:
                next_function = add_function(name, node, "function", current_class)

        if node_type == "method_definition":
            name = _identifier(node.child_by_field_name("name"), raw)
            if name:
                next_function = add_function(name, node, "method", current_class)

        if node_type == "variable_declarator":
            value = node.child_by_field_name("value")
            if value is not None and value.type in {"arrow_function", "function_expression", "generator_function"}:
                name = _identifier(node.child_by_field_name("name"), raw)
                if name:
                    next_function = add_function(
                        name,
                        node,
                        "arrow" if value.type == "arrow_function" else "function_expression",
                        current_class,
                    )

        if node_type == "call_expression":
            function = node.child_by_field_name("function")
            callee = _identifier(function, raw)
            if callee:
                calls.append({
                    "caller": current_function or "<module>",
                    "callee": callee,
                    "lineno": _line(node),
                })
                if callee == "require":
                    module = _module_from_require_text(_node_text(node, raw))
                    if module:
                        imports.append(module)
                        import_records.append({
                            "kind": "import",
                            "module": module,
                            "name": None,
                            "alias": None,
                            "level": 0,
                            "lineno": _line(node),
                        })

        for child in node.children:
            walk(child, next_class, next_function)

    walk(tree.root_node)

    seen_imports: set[tuple[str, int]] = set()
    unique_import_records = []
    for row in import_records:
        key = (str(row.get("module") or ""), int(row.get("lineno") or 0))
        if key in seen_imports:
            continue
        seen_imports.add(key)
        unique_import_records.append(row)

    return {
        "path": rel,
        "language": language_name,
        "sha256": _sha_text(text),
        "line_count": text.count("\n") + 1 if text else 0,
        "imports": sorted(set(imports)),
        "import_records": unique_import_records,
        "functions": functions[:300],
        "async_functions": async_functions[:300],
        "classes": classes[:120],
        "methods": methods[:300],
        "calls": calls[:1000],
        "api_calls": [],
        "routes": [],
        "symbol_locations": symbol_locations[:1000],
        "parse_error": (
            {"type": "TreeSitterSyntaxError", "message": "parse tree contains syntax errors"}
            if tree.root_node.has_error
            else None
        ),
        "parser_engine": "tree_sitter",
    }


def parse_repo_js_ts_tree_sitter(repo_root: Path) -> list[dict]:
    docs = []
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".js", ".jsx", ".ts", ".tsx"}:
            continue
        if any(part in {".uacos", "node_modules", "dist", "build", ".git", "__pycache__", ".venv"} for part in path.parts):
            continue
        docs.append(parse_js_ts_file_tree_sitter(path, repo_root=repo_root))
    return docs
