from __future__ import annotations

from pathlib import Path
from collections import deque
from uacos.graph.builder import load_graph

def query_symbol(repo_root: Path, symbol: str) -> dict:
    graph = load_graph(repo_root)
    matches = []
    for sym, file in graph.get("symbol_to_file", {}).items():
        if symbol == sym or symbol.lower() in sym.lower():
            matches.append({"symbol": sym, "file": file})
    calls_from = []
    calls_to = []
    for edge in graph.get("call_edges", []):
        if symbol in str(edge.get("caller", "")):
            calls_from.append(edge)
        if symbol in str(edge.get("callee", "")):
            calls_to.append(edge)
    return {"status": "ok", "query": symbol, "matches": matches, "calls_from": calls_from, "calls_to": calls_to}

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
