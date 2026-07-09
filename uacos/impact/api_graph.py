from __future__ import annotations

from pathlib import Path
import re

SKIP_DIRS = {".git", ".uacos", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build", "reports"}
CODE_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx"}
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}

PY_ROUTE_RE = re.compile(r"@(?P<obj>app|router|bp)\.(?P<method>get|post|put|patch|delete|options|head|route)\((?P<args>[^\n)]*)", re.IGNORECASE)
PY_FUNCTION_RE = re.compile(r"^\s*(?:async\s+def|def)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\(", re.MULTILINE)
JS_ROUTE_RE = re.compile(r"(?P<obj>app|router)\.(?P<method>get|post|put|patch|delete|options|head)\s*\(\s*[`'\"](?P<path>[^`'\"]+)[`'\"]", re.IGNORECASE)
JS_FETCH_RE = re.compile(r"(?P<kind>fetch|axios\.(?:get|post|put|patch|delete)|api\.(?:get|post|put|patch|delete))\s*\(\s*[`'\"](?P<path>[^`'\"]+)[`'\"]", re.IGNORECASE)
STRING_RE = re.compile(r"[`'\"](?P<value>/[^`'\"]*)[`'\"]")


def _safe_rel(path: Path, repo_root: Path) -> str:
    return str(path.relative_to(repo_root)).replace("\\", "/")


def _should_scan(path: Path, repo_root: Path) -> bool:
    if not path.is_file() or path.suffix.lower() not in CODE_EXTS:
        return False
    rel = path.relative_to(repo_root)
    return not any(part in SKIP_DIRS for part in rel.parts)


def _task_terms(task: str | None) -> list[str]:
    return sorted({term.lower() for term in re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}|/[A-Za-z0-9_/{}/.-]+", task or "")})[:40]


def _first_string(args: str) -> str | None:
    match = STRING_RE.search(args or "")
    return match.group("value") if match else None


def _method_from_py(method: str, args: str) -> str:
    if method.lower() != "route":
        return method.upper()
    methods = re.findall(r"['\"]([A-Z]+)['\"]", args or "")
    for method_name in methods:
        if method_name.lower() in HTTP_METHODS:
            return method_name.upper()
    return "ANY"


def _nearest_function_after(text: str, pos: int) -> str | None:
    match = PY_FUNCTION_RE.search(text, pos)
    return match.group("name") if match else None


def _matches_task(row: dict, terms: list[str]) -> list[str]:
    haystack = " ".join(str(row.get(key, "")) for key in ["path", "file", "handler", "kind", "method"]).lower()
    return [term for term in terms if term in haystack]


def scan_python_routes(text: str, rel: str, terms: list[str]) -> list[dict]:
    rows = []
    for match in PY_ROUTE_RE.finditer(text):
        args = match.group("args") or ""
        path = _first_string(args)
        if not path:
            continue
        row = {
            "kind": "server_route",
            "language": "python",
            "file": rel,
            "method": _method_from_py(match.group("method"), args),
            "path": path,
            "handler": _nearest_function_after(text, match.end()),
            "line": text.count("\n", 0, match.start()) + 1,
            "framework_hint": match.group("obj"),
        }
        row["matched_task_terms"] = _matches_task(row, terms)
        rows.append(row)
    return rows


def scan_js_routes_and_calls(text: str, rel: str, terms: list[str]) -> tuple[list[dict], list[dict]]:
    routes = []
    calls = []
    for match in JS_ROUTE_RE.finditer(text):
        row = {
            "kind": "server_route",
            "language": "js_ts",
            "file": rel,
            "method": match.group("method").upper(),
            "path": match.group("path"),
            "handler": None,
            "line": text.count("\n", 0, match.start()) + 1,
            "framework_hint": match.group("obj"),
        }
        row["matched_task_terms"] = _matches_task(row, terms)
        routes.append(row)
    for match in JS_FETCH_RE.finditer(text):
        kind = match.group("kind")
        method = "GET"
        if "." in kind:
            method = kind.rsplit(".", 1)[-1].upper()
        row = {
            "kind": "client_api_call",
            "language": "js_ts",
            "file": rel,
            "method": method,
            "path": match.group("path"),
            "line": text.count("\n", 0, match.start()) + 1,
            "caller_hint": kind,
        }
        row["matched_task_terms"] = _matches_task(row, terms)
        calls.append(row)
    return routes, calls


def build_api_graph(repo_root: Path, task: str | None = None, selected_files: list[dict] | None = None, max_entries: int = 200) -> dict:
    """Build a lightweight route/API graph for reviewable context intelligence.

    This is a static heuristic scanner. It does not execute the app and does not
    guarantee complete framework coverage. It is intended to make backend/frontend
    route and API relationships visible before an AI agent edits code.
    """

    terms = _task_terms(task)
    selected = {item.get("file") or item.get("path") for item in selected_files or [] if item.get("file") or item.get("path")}
    routes: list[dict] = []
    calls: list[dict] = []
    scanned_files = 0
    for path in sorted(repo_root.rglob("*")):
        if not _should_scan(path, repo_root):
            continue
        rel = _safe_rel(path, repo_root)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")[:500000]
        except OSError:
            continue
        scanned_files += 1
        if path.suffix.lower() == ".py":
            routes.extend(scan_python_routes(text, rel, terms))
        else:
            js_routes, js_calls = scan_js_routes_and_calls(text, rel, terms)
            routes.extend(js_routes)
            calls.extend(js_calls)

    for row in routes + calls:
        row["in_selected_context"] = row.get("file") in selected

    relevant_routes = [row for row in routes if row.get("matched_task_terms") or row.get("in_selected_context")]
    relevant_calls = [row for row in calls if row.get("matched_task_terms") or row.get("in_selected_context")]
    return {
        "status": "ok",
        "task": task,
        "scanned_files": scanned_files,
        "route_count": len(routes),
        "client_api_call_count": len(calls),
        "routes": routes[:max_entries],
        "client_api_calls": calls[:max_entries],
        "relevant_routes": relevant_routes[:max_entries],
        "relevant_client_api_calls": relevant_calls[:max_entries],
        "selected_context_files_with_api_items": sorted({row.get("file") for row in routes + calls if row.get("in_selected_context")}),
        "claim": "Route/API graph is a static heuristic map. It helps context selection review but does not prove runtime routing behavior.",
    }
