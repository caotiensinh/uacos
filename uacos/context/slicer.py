from __future__ import annotations

from pathlib import Path

from uacos.graph.builder import load_graph


def _norm_path(value: str) -> str:
    return str(value).replace("\\", "/")


def _symbol_map(graph: dict) -> dict[str, dict]:
    return {
        str(row.get("id")): row
        for row in graph.get("symbols", [])
        if row.get("id") and row.get("file") and row.get("lineno")
    }


def _infer_end_line(symbol: dict, graph: dict, total_lines: int, max_lines: int) -> int:
    explicit = symbol.get("end_lineno")
    if isinstance(explicit, int) and explicit >= int(symbol["lineno"]):
        return min(explicit, total_lines)

    file_path = _norm_path(symbol["file"])
    start = int(symbol["lineno"])
    next_starts = sorted(
        int(row["lineno"])
        for row in graph.get("symbols", [])
        if _norm_path(str(row.get("file") or "")) == file_path
        and isinstance(row.get("lineno"), int)
        and int(row["lineno"]) > start
    )
    if next_starts:
        return min(next_starts[0] - 1, total_lines, start + max_lines - 1)
    return min(total_lines, start + max_lines - 1)


def slice_symbol(
    repo_root: Path,
    symbol_id: str,
    *,
    padding: int = 2,
    max_lines: int = 160,
    graph: dict | None = None,
) -> dict:
    """Extract a bounded source slice for one canonical semantic symbol.

    Exact graph symbol IDs are required. This intentionally avoids fuzzy symbol
    resolution so context generation cannot silently select the wrong symbol.
    """
    graph = graph or load_graph(repo_root)
    symbols = _symbol_map(graph)
    symbol = symbols.get(symbol_id)
    if symbol is None:
        return {"status": "not_found", "symbol_id": symbol_id}

    rel = _norm_path(symbol["file"])
    path = repo_root / rel
    if not path.exists() or not path.is_file():
        return {"status": "missing_file", "symbol_id": symbol_id, "file": rel}

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    total_lines = len(lines)
    if total_lines == 0:
        return {
            "status": "ok",
            "symbol_id": symbol_id,
            "file": rel,
            "kind": symbol.get("kind"),
            "start_line": 1,
            "end_line": 0,
            "symbol_start_line": int(symbol["lineno"]),
            "symbol_end_line": int(symbol["lineno"]),
            "content": "",
        }

    symbol_start = max(1, int(symbol["lineno"]))
    symbol_end = _infer_end_line(symbol, graph, total_lines, max_lines)
    start = max(1, symbol_start - max(0, padding))
    end = min(total_lines, symbol_end + max(0, padding))
    if end - start + 1 > max_lines + (2 * max(0, padding)):
        end = min(total_lines, start + max_lines + (2 * max(0, padding)) - 1)

    content = "\n".join(lines[start - 1 : end])
    return {
        "status": "ok",
        "symbol_id": symbol_id,
        "file": rel,
        "kind": symbol.get("kind"),
        "qname": symbol.get("qname"),
        "language": symbol.get("language"),
        "start_line": start,
        "end_line": end,
        "symbol_start_line": symbol_start,
        "symbol_end_line": symbol_end,
        "content": content,
        "line_count": max(0, end - start + 1),
    }


def slice_symbols(
    repo_root: Path,
    symbol_ids: list[str] | tuple[str, ...],
    *,
    max_symbols: int = 8,
    max_chars: int = 12000,
    padding: int = 2,
    max_lines_per_symbol: int = 160,
) -> dict:
    """Extract deterministic, de-duplicated symbol slices under a char budget."""
    graph = load_graph(repo_root)
    slices = []
    seen_ranges: set[tuple[str, int, int]] = set()
    chars = 0

    for symbol_id in list(dict.fromkeys(str(x) for x in symbol_ids if str(x).strip())):
        if len(slices) >= max_symbols:
            break
        row = slice_symbol(
            repo_root,
            symbol_id,
            padding=padding,
            max_lines=max_lines_per_symbol,
            graph=graph,
        )
        if row.get("status") != "ok":
            continue
        key = (str(row["file"]), int(row["start_line"]), int(row["end_line"]))
        if key in seen_ranges:
            continue
        projected = chars + len(str(row.get("content") or ""))
        if slices and projected > max_chars:
            break
        if not slices and projected > max_chars:
            row = dict(row)
            row["content"] = str(row.get("content") or "")[:max_chars]
            row["truncated_by_char_budget"] = True
            projected = len(row["content"])
        slices.append(row)
        seen_ranges.add(key)
        chars = projected

    return {
        "status": "ok",
        "requested_symbol_ids": list(dict.fromkeys(str(x) for x in symbol_ids if str(x).strip())),
        "slice_count": len(slices),
        "char_count": chars,
        "slices": slices,
    }
