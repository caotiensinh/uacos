from __future__ import annotations

from pathlib import Path
import ast
import hashlib

def _name(node) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    if isinstance(node, ast.Call):
        return _name(node.func)
    if isinstance(node, ast.Subscript):
        return _name(node.value)
    if isinstance(node, ast.Constant):
        return str(node.value)
    return ""

class PythonAstVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self.async_functions = []
        self.classes = []
        self.methods = []
        self.imports = []
        self.calls = []
        self.symbol_locations = []
        self.current_class = None
        self.current_function = None

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        mod = node.module or ""
        for alias in node.names:
            self.imports.append(f"{mod}.{alias.name}" if mod else alias.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        prev_class = self.current_class
        self.current_class = node.name
        bases = [_name(b) for b in node.bases if _name(b)]
        self.classes.append({"name": node.name, "lineno": node.lineno, "bases": bases})
        self.symbol_locations.append({"symbol": node.name, "kind": "class", "lineno": node.lineno})
        self.generic_visit(node)
        self.current_class = prev_class

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._visit_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._visit_function(node, is_async=True)

    def _visit_function(self, node, is_async: bool):
        prev_function = self.current_function
        qname = f"{self.current_class}.{node.name}" if self.current_class else node.name
        self.current_function = qname
        args = [a.arg for a in node.args.args]
        item = {"name": node.name, "qname": qname, "lineno": node.lineno, "args": args}
        if self.current_class:
            self.methods.append(item)
        elif is_async:
            self.async_functions.append(item)
        else:
            self.functions.append(item)
        self.symbol_locations.append({"symbol": qname, "kind": "function", "lineno": node.lineno})
        self.generic_visit(node)
        self.current_function = prev_function

    def visit_Call(self, node: ast.Call):
        called = _name(node.func)
        if called:
            self.calls.append({
                "caller": self.current_function or "<module>",
                "callee": called,
                "lineno": getattr(node, "lineno", None),
            })
        self.generic_visit(node)

def parse_python_file(path: Path, repo_root: Path | None = None) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    rel = str(path.relative_to(repo_root)).replace("\\", "/") if repo_root else str(path)
    digest = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
    result = {
        "path": rel,
        "language": "python",
        "sha256": digest,
        "line_count": text.count("\n") + 1 if text else 0,
        "functions": [],
        "async_functions": [],
        "classes": [],
        "methods": [],
        "imports": [],
        "calls": [],
        "symbol_locations": [],
        "parse_error": None,
    }
    try:
        tree = ast.parse(text)
        visitor = PythonAstVisitor()
        visitor.visit(tree)
        result.update({
            "functions": visitor.functions,
            "async_functions": visitor.async_functions,
            "classes": visitor.classes,
            "methods": visitor.methods,
            "imports": sorted(set(visitor.imports)),
            "calls": visitor.calls,
            "symbol_locations": visitor.symbol_locations,
        })
    except SyntaxError as exc:
        result["parse_error"] = {"type": "SyntaxError", "message": str(exc), "lineno": exc.lineno}
    except Exception as exc:
        result["parse_error"] = {"type": type(exc).__name__, "message": str(exc)}
    return result

def parse_repo_python(repo_root: Path, include_tests: bool = True) -> list[dict]:
    docs = []
    for path in sorted(repo_root.rglob("*.py")):
        if ".uacos" in path.parts or "__pycache__" in path.parts or ".venv" in path.parts:
            continue
        if not include_tests and (path.name.startswith("test_") or "/tests/" in str(path).replace("\\", "/")):
            continue
        docs.append(parse_python_file(path, repo_root=repo_root))
    return docs
