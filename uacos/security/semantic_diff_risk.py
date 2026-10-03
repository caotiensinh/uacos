from __future__ import annotations

from pathlib import Path
import re

from uacos.graph.builder import load_graph
from uacos.graph.change_map import symbols_for_changed_lines
from uacos.security.diff_parser import parse_unified_diff


HIGH_RISK_SYMBOL_HINTS = (
    "auth", "login", "session", "jwt", "token", "oauth", "password",
    "permission", "rbac", "encrypt", "decrypt", "secret", "credential",
)
CRITICAL_PATH_HINTS = (
    ".github/workflows/", "security/", "auth/", "migrations/", "schema/",
    "pyproject.toml", "requirements", "package.json", "dockerfile",
)
STRUCTURAL_ADDED_PATTERNS = (
    re.compile(r"^\s*(?:async\s+)?def\s+", re.I),
    re.compile(r"^\s*class\s+", re.I),
    re.compile(r"^\s*(?:public\s+|private\s+|protected\s+)?(?:class|interface|record|enum)\s+", re.I),
    re.compile(r"^\s*(?:fn|struct|trait|enum|impl)\s+", re.I),
    re.compile(r"^\s*(?:func|type)\s+", re.I),
)


def _to_ranges(lines: list[int]) -> list[tuple[int, int]]:
    values = sorted({int(line) for line in lines if isinstance(line, int) and line > 0})
    if not values:
        return []
    ranges: list[tuple[int, int]] = []
    start = previous = values[0]
    for value in values[1:]:
        if value == previous + 1:
            previous = value
            continue
        ranges.append((start, previous))
        start = previous = value
    ranges.append((start, previous))
    return ranges


def _symbol_risk(symbol_id: str, kind: str) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    lowered = symbol_id.lower()
    if any(hint in lowered for hint in HIGH_RISK_SYMBOL_HINTS):
        score += 3
        reasons.append("security_sensitive_symbol")
    if kind in {"class", "async_function", "function", "method"}:
        score += 1
        reasons.append("executable_symbol_changed")
    return score, reasons


def assess_semantic_diff_risk(repo_root: Path, patch_text: str) -> dict:
    """Assess patch risk from diff hunks and existing semantic graph evidence.

    Changed old-side lines are mapped to existing symbols. Unknown hunks remain
    explicit uncertainty; the analyzer never invents a target symbol.
    """
    root = Path(repo_root).resolve()
    graph = load_graph(root, auto_build=True)
    patches = parse_unified_diff(patch_text)

    old_changes: dict[str, list[tuple[int, int]]] = {}
    for fp in patches:
        path = fp.old_path or fp.new_path or ""
        if path and fp.old_changed_lines:
            old_changes[path] = _to_ranges(fp.old_changed_lines)

    affected_symbols = symbols_for_changed_lines(graph, old_changes)
    symbol_findings: list[dict] = []
    score = 0
    categories: set[str] = set()

    for symbol in affected_symbols:
        symbol_score, reasons = _symbol_risk(str(symbol.get("symbol_id") or ""), str(symbol.get("kind") or ""))
        score += symbol_score
        categories.update(reasons)
        symbol_findings.append({
            "symbol_id": symbol.get("symbol_id"),
            "file": symbol.get("file"),
            "kind": symbol.get("kind"),
            "changed_ranges": symbol.get("changed_ranges", []),
            "score": symbol_score,
            "reasons": reasons,
        })

    structural_additions = 0
    deleted_files = 0
    new_files = 0
    critical_paths: list[str] = []
    unmapped_old_hunks: list[dict] = []
    mapped_files = {str(row.get("file") or "") for row in affected_symbols}

    for fp in patches:
        path = fp.path
        normalized = path.replace("\\", "/").lower()
        if fp.old_path is None:
            new_files += 1
            score += 1
            categories.add("new_file")
        if fp.new_path is None:
            deleted_files += 1
            score += 4
            categories.add("file_deleted")
        if any(hint in normalized for hint in CRITICAL_PATH_HINTS):
            critical_paths.append(path)
            # Critical control-plane/configuration paths deserve enough weight
            # that a structural change in the same patch crosses the high-risk
            # review threshold. This keeps semantic review aligned with the
            # existing patch-review policy without making path evidence alone
            # an automatic block.
            score += 4
            categories.add("critical_path")
        added_structures = sum(1 for line in fp.added_lines if any(pattern.search(line) for pattern in STRUCTURAL_ADDED_PATTERNS))
        if added_structures:
            structural_additions += added_structures
            score += min(3, added_structures)
            categories.add("structural_addition")
        old_path = fp.old_path or fp.new_path or ""
        if fp.old_changed_lines and old_path not in mapped_files:
            unmapped_old_hunks.append({"path": old_path, "ranges": _to_ranges(fp.old_changed_lines)})

    if unmapped_old_hunks:
        categories.add("unmapped_changed_hunk")

    if score >= 8:
        risk_level = "critical"
    elif score >= 5:
        risk_level = "high"
    elif score >= 2:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "risk_level": risk_level,
        "risk_score": score,
        "categories": sorted(categories),
        "affected_symbols": symbol_findings,
        "critical_paths": sorted(set(critical_paths)),
        "structural_additions": structural_additions,
        "new_files": new_files,
        "deleted_files": deleted_files,
        "unmapped_old_hunks": unmapped_old_hunks,
        "evidence_model": "existing_symbol_locations_plus_unified_diff_hunks_v1",
        "requires_human_review": risk_level in {"high", "critical"},
    }
