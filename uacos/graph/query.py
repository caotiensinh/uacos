from __future__ import annotations

from pathlib import Path
from collections import deque
from uacos.graph.builder import load_graph


def _legacy_query(graph: dict, symbol: str) -> list[dict]:
    matches = []
    for sym, file in graph.get("symbol_to_file", {}).items():
        if symbol == sym or symbol.lower() in sym.lower():
            matches.append({"symbol": sym, "file": file})
    return matches


def query_symbol(repo_root: Path, symbol: str) -> dict:
    graph = load_graph(repo_root)
    records = graph.get("symbols") or []
    matches = []

    if records:
        needle = symbol.lower()
        exact = []
        fuzzy = []
        for row in records:
            aliases = {
                str(row.get("id") or ""),
                str(row.get("name") or ""),
                str(row.get("qname") or ""),
                f"{row.get('module')}.{row.get('qname')}" if row.get("module") and row.get("qname") else "",
            }
            aliases.discard("")
            if symbol in aliases:
                exact.append(row)
            elif any(needle in alias.lower() for alias in aliases):
                fuzzy.append(row)
        chosen = exact if exact else fuzzy
        matches = [
            {
                "symbol": row.get("qname") or row.get("name"),
                "symbol_id": row.get("id"),
                "file": row.get("file"),
                "kind": row.get("kind"),
                "lineno": row.get("lineno"),
                "end_lineno": row.get("end_lineno"),
                "match": "exact" if exact else "fuzzy",
            }
            for row in chosen
        ]
    else:
        matches = _legacy_query(graph, symbol)

    matched_ids = {m.get("symbol_id") for m in matches if m.get("symbol_id")}
    matched_names = {m.get("symbol") for m in matches if m.get("symbol")}

    calls_from = []
    calls_to = []
    for edge in graph.get("call_edges", []):
        if (
            edge.get("source_symbol_id") in matched_ids
            or edge.get("caller") in matched_names
            or symbol in str(edge.get("caller", ""))
        ):
            calls_from.append(edge)
        if (
            edge.get("target_symbol_id") in matched_ids
            or edge.get("callee") in matched_names
            or symbol in str(edge.get("callee", ""))
        ):
            calls_to.append(edge)

    return {
        "status": "ok",
        "query": symbol,
        "matches": matches,
        "match_count": len(matches),
        "ambiguous": len(matches) > 1,
        "calls_from": calls_from,
        "calls_to": calls_to,
    }


def related_files(repo_root: Path, start_file: str, depth: int = 2) -> dict:
    graph = load_graph(repo_root)
    adj = {}
    for edge in graph.get("file_edges", []):
        adj.setdefault(edge["source"], set()).add(edge["target"])
        adj.setdefault(edge["target"], set()).add(edge["source"])
    for edge in graph.get("call_edges", []):
        src = edge.get("source_file")
        dst = edge.get("target_file")
        if src and dst and src != dst:
            adj.setdefault(src, set()).add(dst)
            adj.setdefault(dst, set()).add(src)
    seen = {start_file}
    q = deque([(start_file, 0)])
    rows = []
    while q:
        node, dist = q.popleft()
        rows.append({"file": node, "distance": dist})
        if dist >= depth:
            continue
        for nxt in sorted(adj.get(node, [])):
            if nxt not in seen:
                seen.add(nxt)
                q.append((nxt, dist + 1))
    return {"status": "ok", "start_file": start_file, "depth": depth, "related": rows}
