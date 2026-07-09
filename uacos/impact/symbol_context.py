from __future__ import annotations

from pathlib import Path
import re

from uacos.graph.builder import load_graph

GENERIC_TERMS = {"fix", "add", "update", "change", "code", "file", "test", "docs", "api", "app", "module"}


def _task_terms(task: str | None) -> list[str]:
    terms = []
    for term in re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", task or ""):
        low = term.lower()
        if low not in GENERIC_TERMS:
            terms.append(low)
    return sorted(set(terms))[:40]


def _selected_paths(selected_files: list[dict] | None) -> set[str]:
    return {item.get("file") or item.get("path") for item in selected_files or [] if item.get("file") or item.get("path")}


def _symbol_matches(graph: dict, terms: list[str]) -> list[dict]:
    rows = []
    seen = set()
    for symbol, file in graph.get("symbol_to_file", {}).items():
        low = symbol.lower()
        matched = [term for term in terms if term in low]
        if not matched:
            continue
        key = (symbol, file)
        if key in seen:
            continue
        seen.add(key)
        rows.append({"symbol": symbol, "file": file, "matched_task_terms": matched})
    rows.sort(key=lambda row: (row["file"], row["symbol"]))
    return rows[:100]


def _call_edges_for_files(graph: dict, files: set[str], max_edges: int = 100) -> tuple[list[dict], list[dict]]:
    outgoing = []
    incoming = []
    for edge in graph.get("call_edges", []):
        src = edge.get("source_file")
        dst = edge.get("target_file")
        row = {
            "source_file": src,
            "target_file": dst,
            "caller": edge.get("caller"),
            "callee": edge.get("callee"),
            "line": edge.get("lineno"),
        }
        if src in files:
            outgoing.append(row)
        if dst in files:
            incoming.append(row)
    return outgoing[:max_edges], incoming[:max_edges]


def _import_edges_for_files(graph: dict, files: set[str], max_edges: int = 100) -> tuple[list[dict], list[dict]]:
    outgoing = []
    incoming = []
    for edge in graph.get("file_edges", []):
        row = {
            "source": edge.get("source"),
            "target": edge.get("target"),
            "kind": edge.get("kind"),
            "import": edge.get("import"),
        }
        if edge.get("source") in files:
            outgoing.append(row)
        if edge.get("target") in files:
            incoming.append(row)
    return outgoing[:max_edges], incoming[:max_edges]


def build_symbol_context(repo_root: Path, task: str | None = None, selected_files: list[dict] | None = None, max_symbols_per_file: int = 80) -> dict:
    """Explain selected files through existing symbol/import/call graph data.

    This does not replace the graph builder. It is a review layer that makes the
    existing Python symbol index visible inside assist output.
    """

    graph = load_graph(repo_root)
    selected = _selected_paths(selected_files)
    terms = _task_terms(task)
    matches = _symbol_matches(graph, terms)
    if not selected:
        selected = {row["file"] for row in matches[:10]}

    file_symbols = graph.get("file_symbols", {})
    selected_symbol_rows = []
    for file in sorted(selected):
        symbols = file_symbols.get(file, [])[:max_symbols_per_file]
        selected_symbol_rows.append({
            "file": file,
            "symbol_count": len(file_symbols.get(file, [])),
            "symbols": symbols,
            "matched_symbols": [symbol for symbol in symbols if any(term in symbol.lower() for term in terms)],
        })

    outgoing_calls, incoming_calls = _call_edges_for_files(graph, selected)
    outgoing_imports, incoming_imports = _import_edges_for_files(graph, selected)
    return {
        "status": "ok",
        "task": task,
        "task_terms": terms,
        "selected_file_count": len(selected),
        "selected_file_symbols": selected_symbol_rows,
        "task_symbol_matches": matches,
        "outgoing_calls_from_selected": outgoing_calls,
        "incoming_calls_to_selected": incoming_calls,
        "outgoing_imports_from_selected": outgoing_imports,
        "incoming_imports_to_selected": incoming_imports,
        "graph_stats": graph.get("stats", {}),
        "claim": "Symbol context is based on the current static Python graph. It improves reviewability but does not prove runtime behavior or complete cross-language coverage.",
    }
