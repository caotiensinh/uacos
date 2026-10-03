from __future__ import annotations


def symbols_for_changed_lines(graph: dict, changes: dict[str, list[tuple[int, int]]]) -> list[dict]:
    """Return symbols intersecting changed line ranges.

    `changes` maps repo-relative file paths to inclusive (start, end) ranges.
    Symbols without usable locations are ignored instead of guessed.
    """
    rows: list[dict] = []
    for symbol in graph.get("symbols", []) or []:
        file_path = str(symbol.get("file") or "")
        ranges = changes.get(file_path) or []
        if not ranges:
            continue
        start = symbol.get("lineno")
        end = symbol.get("end_lineno") or start
        if not isinstance(start, int) or not isinstance(end, int):
            continue
        matched = []
        for changed_start, changed_end in ranges:
            if changed_start <= end and changed_end >= start:
                matched.append((changed_start, changed_end))
        if not matched:
            continue
        rows.append({
            "symbol_id": symbol.get("id"),
            "file": file_path,
            "kind": symbol.get("kind"),
            "lineno": start,
            "end_lineno": end,
            "changed_ranges": matched,
        })
    rows.sort(key=lambda row: (str(row.get("file") or ""), int(row.get("lineno") or 0), str(row.get("symbol_id") or "")))
    return rows
