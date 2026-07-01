from __future__ import annotations

from pathlib import Path
import hashlib
import re

IMPORT_RE = re.compile(r"""(?m)^\s*(?:import\s+(?:.+?\s+from\s+)?['"]([^'"]+)['"]|const\s+\w+\s*=\s*require\(['"]([^'"]+)['"]\))""")
FUNCTION_RE = re.compile(r"""(?m)^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(""")
ARROW_RE = re.compile(r"""(?m)^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>""")
CLASS_RE = re.compile(r"""(?m)^\s*(?:export\s+)?class\s+([A-Za-z_$][\w$]*)""")
METHOD_RE = re.compile(r"""(?m)^\s*(?:async\s+)?([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*\{""")
FETCH_RE = re.compile(r"""(?:fetch|axios\.(?:get|post|put|delete|patch))\s*\(\s*([`'"])(.*?)\1""")
URL_LITERAL_RE = re.compile(r"""[`'"]((?:/api/|https?://)[^`'"]+)[`'"]""")
ROUTE_LIKE_RE = re.compile(r"""(?m)(?:router|app)\.(?:get|post|put|delete|patch)\s*\(\s*([`'"])(.*?)\1""")
EXPORT_RE = re.compile(r"""(?m)^\s*export\s+(?:default\s+)?(?:function|class|const|let|var)?\s*([A-Za-z_$][\w$]*)?""")

def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()

def _norm_endpoint(url: str) -> str:
    url = url.strip()
    url = re.sub(r"\$\{[^}]+\}", "{var}", url)
    url = re.sub(r"https?://[^/]+", "", url)
    url = url.split("?")[0]
    return url

def parse_js_ts_file(path: Path, repo_root: Path | None = None) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    rel = str(path.relative_to(repo_root)).replace("\\", "/") if repo_root else str(path)
    imports = []
    for m in IMPORT_RE.finditer(text):
        imports.append(m.group(1) or m.group(2))
    functions = [{"name": m.group(1), "lineno": text[:m.start()].count("\n") + 1, "kind": "function"} for m in FUNCTION_RE.finditer(text)]
    functions += [{"name": m.group(1), "lineno": text[:m.start()].count("\n") + 1, "kind": "arrow"} for m in ARROW_RE.finditer(text)]
    classes = [{"name": m.group(1), "lineno": text[:m.start()].count("\n") + 1} for m in CLASS_RE.finditer(text)]
    calls = []
    for m in re.finditer(r"""([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)?)\s*\(""", text):
        name = m.group(1)
        if name not in {"if", "for", "while", "switch", "catch", "function"}:
            calls.append({"callee": name, "lineno": text[:m.start()].count("\n") + 1})
    api_calls = []
    for m in FETCH_RE.finditer(text):
        api_calls.append({"endpoint": _norm_endpoint(m.group(2)), "lineno": text[:m.start()].count("\n") + 1, "kind": "fetch_or_axios"})
    for m in URL_LITERAL_RE.finditer(text):
        ep = _norm_endpoint(m.group(1))
        if not any(x["endpoint"] == ep for x in api_calls):
            api_calls.append({"endpoint": ep, "lineno": text[:m.start()].count("\n") + 1, "kind": "url_literal"})
    routes = [{"endpoint": _norm_endpoint(m.group(2)), "lineno": text[:m.start()].count("\n") + 1} for m in ROUTE_LIKE_RE.finditer(text)]
    return {
        "path": rel,
        "language": "javascript" if path.suffix.lower() in {".js", ".jsx"} else "typescript",
        "sha256": _sha_text(text),
        "line_count": text.count("\n") + 1 if text else 0,
        "imports": sorted(set(imports)),
        "functions": functions[:300],
        "classes": classes[:120],
        "calls": calls[:500],
        "api_calls": api_calls[:200],
        "routes": routes[:200],
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
