from __future__ import annotations

from pathlib import Path
import re

from uacos.context.slicer import slice_symbol
from uacos.graph.builder import load_graph


ROLE_WEIGHTS = {
    "target": 5.0,
    "contract": 3.0,
    "neighbor": 2.0,
    "test_support": 2.5,
    "support": 1.0,
}


def _norm_path(value: str) -> str:
    return str(value).replace("\\", "/")


def _is_test_file(path: str) -> bool:
    rel = f"/{_norm_path(path).lower()}/"
    name = Path(path).name.lower()
    return (
        "/test/" in rel
        or "/tests/" in rel
        or name.startswith("test_")
        or name.endswith(("_test.py", ".test.js", ".test.jsx", ".test.ts", ".test.tsx", ".spec.js", ".spec.ts", ".spec.tsx"))
    )


def _focused_excerpt(path: Path, task: str, max_chars: int) -> tuple[str, int, int]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if not lines:
        return "", 1, 0
    tokens = [
        token.lower()
        for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", task)
        if len(token) >= 3
    ]
    center = 0
    for idx, line in enumerate(lines):
        lower = line.lower()
        if any(token in lower for token in tokens):
            center = idx
            break
    radius = 12
    start = max(0, center - radius)
    end = min(len(lines), center + radius + 1)
    excerpt = "\n".join(lines[start:end])
    if len(excerpt) > max_chars:
        excerpt = excerpt[:max_chars]
    return excerpt, start + 1, end


def _containing_contract(symbol: dict, symbols: dict[str, dict]) -> str | None:
    if symbol.get("kind") != "method":
        return None
    qname = str(symbol.get("qname") or "")
    if "." not in qname:
        return None
    owner = qname.rsplit(".", 1)[0]
    module = str(symbol.get("module") or "")
    candidate = f"{module}:{owner}" if module else owner
    row = symbols.get(candidate)
    if row and row.get("kind") == "class":
        return candidate
    return None


def build_context_plan(
    repo_root: Path,
    impact: dict,
    *,
    max_chars: int = 18000,
    max_files: int = 8,
    max_symbols_per_file: int = 2,
) -> dict:
    """Plan diverse semantic context under one explicit character budget.

    Direct task symbols receive the most budget, containing classes/contracts are
    next, caller/callee neighbors follow, then tests and weak supporting files.
    The planner limits repeated slices from one file so a single large module does
    not consume the entire context window.
    """
    graph = load_graph(repo_root)
    symbols = {
        str(row.get("id")): row
        for row in graph.get("symbols", [])
        if row.get("id") and row.get("file")
    }
    direct_ids = [str(x) for x in impact.get("matched_symbol_ids", []) if str(x) in symbols]
    candidates: dict[str, dict] = {}

    def add_symbol(symbol_id: str | None, role: str, priority: float, reason: str) -> None:
        if not symbol_id or symbol_id not in symbols:
            return
        row = symbols[symbol_id]
        existing = candidates.get(symbol_id)
        payload = {
            "symbol_id": symbol_id,
            "file": _norm_path(row["file"]),
            "kind": row.get("kind"),
            "role": role,
            "priority": float(priority),
            "reasons": [reason],
        }
        if existing:
            existing["priority"] = max(float(existing["priority"]), float(priority))
            existing["reasons"] = list(dict.fromkeys(existing["reasons"] + [reason]))
            role_order = {"target": 4, "contract": 3, "neighbor": 2}
            if role_order.get(role, 0) > role_order.get(str(existing.get("role")), 0):
                existing["role"] = role
            return
        candidates[symbol_id] = payload

    for symbol_id in direct_ids:
        add_symbol(symbol_id, "target", 100.0, "direct_task_symbol")
        contract = _containing_contract(symbols[symbol_id], symbols)
        add_symbol(contract, "contract", 85.0, f"contract_for:{symbol_id}")

    for file_row in impact.get("impacted_files", []):
        file_score = float(file_row.get("score") or 0.0)
        for evidence in file_row.get("evidence", []):
            for key in ("symbol_id", "source_symbol_id", "target_symbol_id"):
                symbol_id = evidence.get(key)
                if symbol_id and str(symbol_id) not in direct_ids:
                    add_symbol(str(symbol_id), "neighbor", 60.0 + min(file_score, 20.0), str(evidence.get("kind") or key))

    ordered = sorted(
        candidates.values(),
        key=lambda row: (-float(row["priority"]), -ROLE_WEIGHTS.get(str(row["role"]), 1.0), str(row["symbol_id"])),
    )
    selected_symbols = []
    per_file: dict[str, int] = {}
    target_files = {symbols[sid]["file"] for sid in direct_ids if sid in symbols}
    for row in ordered:
        rel = row["file"]
        cap = max_symbols_per_file + (1 if rel in target_files else 0)
        if per_file.get(rel, 0) >= cap:
            continue
        selected_symbols.append(row)
        per_file[rel] = per_file.get(rel, 0) + 1

    impacted = impact.get("impacted_files", [])[: max_files * 2]
    support_rows = []
    symbol_files = {row["file"] for row in selected_symbols}
    for row in impacted:
        rel = _norm_path(str(row.get("file") or ""))
        if not rel or rel in symbol_files:
            continue
        role = "test_support" if _is_test_file(rel) else "support"
        support_rows.append(
            {
                "file": rel,
                "role": role,
                "priority": float(row.get("score") or 0.0) + (10.0 if role == "test_support" else 0.0),
                "reasons": list(row.get("reasons") or []),
            }
        )
    support_rows.sort(key=lambda row: (-float(row["priority"]), row["file"]))
    support_rows = support_rows[:max_files]

    all_weight = sum(ROLE_WEIGHTS.get(str(row["role"]), 1.0) for row in selected_symbols + support_rows) or 1.0
    usable = max(1000, int(max_chars * 0.88))
    entries = []
    used_chars = 0
    seen_ranges: set[tuple[str, int, int]] = set()

    for row in selected_symbols:
        weight = ROLE_WEIGHTS.get(str(row["role"]), 1.0)
        budget = max(700, int(usable * weight / all_weight))
        sliced = slice_symbol(repo_root, row["symbol_id"], padding=2, max_lines=180, graph=graph)
        if sliced.get("status") != "ok":
            continue
        key = (str(sliced["file"]), int(sliced["start_line"]), int(sliced["end_line"]))
        if key in seen_ranges:
            continue
        content = str(sliced.get("content") or "")
        truncated = len(content) > budget
        if truncated:
            content = content[:budget]
        if used_chars + len(content) > usable and entries:
            continue
        entry = dict(row)
        entry.update(
            {
                "mode": "symbol_slice",
                "start_line": sliced["start_line"],
                "end_line": sliced["end_line"],
                "allocated_chars": budget,
                "content": content,
                "truncated_by_budget": truncated,
            }
        )
        entries.append(entry)
        used_chars += len(content)
        seen_ranges.add(key)

    task = str(impact.get("task") or "")
    selected_files = {str(entry["file"]) for entry in entries}
    for row in support_rows:
        if len({str(x["file"]) for x in entries}) >= max_files and row["file"] not in selected_files:
            break
        path = repo_root / row["file"]
        if not path.exists() or not path.is_file():
            continue
        weight = ROLE_WEIGHTS.get(str(row["role"]), 1.0)
        budget = max(500, min(1800, int(usable * weight / all_weight)))
        excerpt, start_line, end_line = _focused_excerpt(path, task, budget)
        if not excerpt or used_chars + len(excerpt) > usable:
            continue
        entries.append(
            {
                **row,
                "mode": "focused_support_excerpt",
                "start_line": start_line,
                "end_line": end_line,
                "allocated_chars": budget,
                "content": excerpt,
                "truncated_by_budget": len(excerpt) >= budget,
            }
        )
        used_chars += len(excerpt)
        selected_files.add(row["file"])

    role_counts: dict[str, int] = {}
    for entry in entries:
        role = str(entry.get("role") or "support")
        role_counts[role] = role_counts.get(role, 0) + 1

    return {
        "status": "ok",
        "planner": "dynamic_semantic_budget_v1",
        "max_chars": max_chars,
        "usable_chars": usable,
        "used_chars": used_chars,
        "utilization": round(used_chars / usable, 4) if usable else 0.0,
        "role_weights": dict(ROLE_WEIGHTS),
        "role_counts": role_counts,
        "selected_file_count": len({str(row.get("file")) for row in entries}),
        "entry_count": len(entries),
        "entries": entries,
    }
