from __future__ import annotations

from pathlib import Path
import hashlib
import re

IMPORT_RE = re.compile(r'''(?m)^\s*(?:import\s+(?:.+?\s+from\s+)?['"]([^'"]+)['"]|const\s+\w+\s*=\s*require\(['"]([^'"]+)['"]\))''')
FUNCTION_RE = re.compile(r'''(?m)^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(''')
ARROW_RE = re.compile(r'''(?m)^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>''')
CLASS_RE = re.compile(r'''(?m)^\s*(?:export\s+)?class\s+([A-Za-z_$][\w$]*)''')
FETCH_RE = re.compile(r'''(?:fetch|axios\.(?:get|post|put|delete|patch))\s*\(\s*([`'"])(.*?)\1''')
URL_LITERAL_RE = re.compile(r'''[`'"]((?:/api/|https?://)[^`'"]+)[`'"]''')
ROUTE_LIKE_RE = re.compile(r'''(?m)(?:router|app)\.(?:get|post|put|delete|patch)\s*\(\s*([`'"])(.*?)\1''')
CALL_RE = re.compile(r'''([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)?)\s*\(''')


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def _line(text: str, pos: int) -> int:
    return text[:pos].count("\n") + 1


def _norm_endpoint(url: str) -> str:
    url = url.strip()
    url = re.sub(r"\$\{[^}]+\}", "{var}", url)
    url = re.sub(r"https?://[^/]+", "", url)
    return url.split("?")[0]


def parse_js_ts_file(path: Path, repo_root: Path | None = None) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    rel = str(path.relative_to(repo_root)).replace("\\", "/") if repo_root else str(path)
    imports = []
    import_records = []
    for m in IMPORT_RE.finditer(text):
        module = m.group(1) or m.group(2)
        imports.append(module)
        import_records.append({
            "kind": "import",
            "module": module,
            "name": None,
            "alias": None,
            "level": 0,
            "lineno": _line(text, m.start()),
        })

    functions = [
        {"name": m.group(1), "qname": m.group(1), "lineno": _line(text, m.start()), "kind": "function"}
        for m in FUNCTION_RE.finditer(text)
    ]
    functions += [
        {"name": m.group(1), "qname": m.group(1), "lineno": _line(text, m.start()), "kind": "arrow"}
        for m in ARROW_RE.finditer(text)
    ]
    classes = [
        {"name": m.group(1), "qname": m.group(1), "lineno": _line(text, m.start())}
        for m in CLASS_RE.finditer(text)
    ]

    calls = []
    for m in CALL_RE.finditer(text):
        name = m.group(1)
        if name not in {"if", "for", "while", "switch", "catch", "function"}:
            calls.append({"caller": "<module>", "callee": name, "lineno": _line(text, m.start())})

    api_calls = []
    for m in FETCH_RE.finditer(text):
        api_calls.append({"endpoint": _norm_endpoint(m.group(2)), "lineno": _line(text, m.start()), "kind": "fetch_or_axios"})
    for m in URL_LITERAL_RE.finditer(text):
        ep = _norm_endpoint(m.group(1))
        if not any(x["endpoint"] == ep for x in api_calls):
            api_calls.append({"endpoint": ep, "lineno": _line(text, m.start()), "kind": "url_literal"})
    routes = [{"endpoint": _norm_endpoint(m.group(2)), "lineno": _line(text, m.start())} for m in ROUTE_LIKE_RE.finditer(text)]

    return {
        "path": rel,
        "language": "javascript" if path.suffix.lower() in {".js", ".jsx"} else "typescript",
        "sha256": _sha_text(text),
        "line_count": text.count("\n") + 1 if text else 0,
        "imports": sorted(set(imports)),
        "import_records": import_records,
        "functions": functions[:300],
        "async_functions": [],
        "classes": classes[:120],
        "methods": [],
        "calls": calls[:500],
        "api_calls": api_calls[:200],
        "routes": routes[:200],
        "symbol_locations": [
            {"symbol": row["qname"], "kind": row.get("kind", "function"), "lineno": row["lineno"]}
            for row in functions
        ] + [
            {"symbol": row["qname"], "kind": "class", "lineno": row["lineno"]}
            for row in classes
        ],
        "parse_error": None,
    }


def parse_repo_js_ts(repo_root: Path) -> list[dict]:
    docs = []
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".js", ".jsx", ".ts", ".tsx"}:
            continue
        if any(part in {".uacos", "node_modules", "dist", "build", ".git", "__pycache__", ".venv"} for part in path.parts):
            continue
        docs.append(parse_js_ts_file(path, repo_root=repo_root))
    return docs
