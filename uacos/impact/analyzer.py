from __future__ import annotations

from pathlib import Path
import re

from uacos.context.planner import build_context_plan
from uacos.graph.builder import load_graph
from uacos.graph.query import related_files, query_symbol
from uacos.search import search_repo
from uacos.security.diff_parser import parse_unified_diff

GENERIC_TASK_TOKENS = {"uacos", "module", "modules", "add", "fix", "update", "write", "handle", "type", "hints", "hint", "test", "docs", "class", "bug", "query", "endpoint"}

# Scores are evidence weights, not probabilities. They are deliberately additive
# so a file supported by several independent signals outranks a one-off match.
EVIDENCE_WEIGHTS = {
    "symbol_exact": 1.50,
    "symbol_fuzzy": 1.10,
    "graph_distance_0": 1.00,
    "graph_distance_1": 0.70,
    "graph_distance_2": 0.45,
    "caller": 0.65,
    "callee": 0.75,
    "keyword": 0.55,
}


def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text) if len(t) >= 2]


def _task_symbol_candidates(text: str) -> list[str]:
    """Extract likely symbol references while preserving qualified names."""
    qualified = re.findall(
        r"[A-Za-z_][A-Za-z0-9_]*(?:(?::|\.)[A-Za-z_][A-Za-z0-9_]*)+",
        text,
    )
    bare = _tokens(text)
    ordered = []
    seen = set()
    for token in qualified + bare:
        if token.lower() in GENERIC_TASK_TOKENS or token in seen:
            continue
        seen.add(token)
        ordered.append(token)
    return ordered


def _graph_weight(distance: int) -> float:
    if distance <= 0:
        return EVIDENCE_WEIGHTS["graph_distance_0"]
    if distance == 1:
        return EVIDENCE_WEIGHTS["graph_distance_1"]
    if distance == 2:
        return EVIDENCE_WEIGHTS["graph_distance_2"]
    return max(0.10, 0.30 - ((distance - 3) * 0.05))


def impact_by_symbol(repo_root: Path, symbol: str, depth: int = 2) -> dict:
    graph = load_graph(repo_root)
    q = query_symbol(repo_root, symbol)
    files = {}
    for m in q["matches"]:
        files[m["file"]] = max(files.get(m["file"], 0), 1.0)
        rel = related_files(repo_root, m["file"], depth=depth)
        for r in rel["related"]:
            score = max(0.1, 1.0 - (r["distance"] * 0.25))
            files[r["file"]] = max(files.get(r["file"], 0), score)
    for edge in q["calls_to"]:
        if edge.get("source_file"):
            files[edge["source_file"]] = max(files.get(edge["source_file"], 0), 0.75)
        if edge.get("target_file"):
            files[edge["target_file"]] = max(files.get(edge["target_file"], 0), 0.85)
    for edge in q["calls_from"]:
        if edge.get("target_file"):
            files[edge["target_file"]] = max(files.get(edge["target_file"], 0), 0.75)
    ranked = [{"file": f, "score": round(s, 4)} for f, s in files.items()]
    ranked.sort(key=lambda x: (-x["score"], x["file"]))
    return {"status": "ok", "symbol": symbol, "impacted_files": ranked, "symbol_query": q}


def impact_by_task(repo_root: Path, task: str, limit: int = 10, depth: int = 2) -> dict:
    load_graph(repo_root)
    scores: dict[str, float] = {}
    reasons: dict[str, list[str]] = {}
    evidence: dict[str, list[dict]] = {}
    symbol_hits = []
    candidates = _task_symbol_candidates(task)

    def add(file: str | None, weight: float, reason: str, payload: dict | None = None) -> None:
        if not file:
            return
        rel = str(file).replace("\\", "/")
        scores[rel] = scores.get(rel, 0.0) + float(weight)
        reasons.setdefault(rel, []).append(reason)
        item = {"kind": reason, "weight": round(float(weight), 4)}
        if payload:
            item.update(payload)
        evidence.setdefault(rel, []).append(item)

    matched_symbol_ids = set()
    for token in candidates:
        q = query_symbol(repo_root, token)
        matches = q.get("matches", [])
        if not matches:
            continue

        match_rows = []
        for match in matches:
            symbol_id = match.get("symbol_id")
            if symbol_id:
                matched_symbol_ids.add(symbol_id)
            match_kind = str(match.get("match") or "fuzzy")
            weight = EVIDENCE_WEIGHTS["symbol_exact"] if match_kind == "exact" else EVIDENCE_WEIGHTS["symbol_fuzzy"]
            add(
                match.get("file"),
                weight,
                f"symbol:{token}",
                {"symbol_id": symbol_id, "match": match_kind},
            )
            match_rows.append(
                {
                    "query": token,
                    "symbol_id": symbol_id,
                    "file": match.get("file"),
                    "match": match_kind,
                    "ambiguous": bool(q.get("ambiguous")),
                }
            )

            if match.get("file"):
                rel = related_files(repo_root, match["file"], depth=depth)
                for related in rel.get("related", []):
                    distance = int(related.get("distance") or 0)
                    add(
                        related.get("file"),
                        _graph_weight(distance),
                        f"graph:{token}:d{distance}",
                        {"source_file": match.get("file"), "distance": distance},
                    )

        symbol_hits.extend(match_rows)

        for edge in q.get("calls_to", []):
            add(
                edge.get("source_file"),
                EVIDENCE_WEIGHTS["caller"],
                f"caller_of:{token}",
                {"source_symbol_id": edge.get("source_symbol_id")},
            )
            add(
                edge.get("target_file"),
                EVIDENCE_WEIGHTS["callee"],
                f"callee:{token}",
                {"target_symbol_id": edge.get("target_symbol_id")},
            )
        for edge in q.get("calls_from", []):
            add(
                edge.get("target_file"),
                EVIDENCE_WEIGHTS["callee"],
                f"called_by:{token}",
                {"target_symbol_id": edge.get("target_symbol_id")},
            )

    try:
        hits = search_repo(repo_root, task, limit=max(limit * 2, limit))
    except Exception:
        hits = []
    for i, hit in enumerate(hits):
        rel = hit.get("path") or hit.get("file_path")
        if not rel:
            continue
        weight = max(0.10, EVIDENCE_WEIGHTS["keyword"] - i * 0.03)
        add(rel, weight, "keyword_search", {"rank": i + 1})

    ranked = []
    for file, score in scores.items():
        unique_reasons = list(dict.fromkeys(reasons.get(file, [])))
        ranked.append(
            {
                "file": file,
                "score": round(score, 4),
                "reasons": unique_reasons,
                "evidence_count": len(evidence.get(file, [])),
                "evidence": evidence.get(file, []),
            }
        )
    ranked.sort(key=lambda x: (-x["score"], -x["evidence_count"], x["file"]))

    return {
        "status": "ok",
        "task": task,
        "impacted_files": ranked[:limit],
        "token_count": len(_tokens(task)),
        "symbol_candidates": candidates,
        "symbol_hits": symbol_hits,
        "matched_symbol_ids": sorted(matched_symbol_ids),
        "ranking_model": "evidence_weighted_v2",
        "evidence_weights": dict(EVIDENCE_WEIGHTS),
    }


def smart_context(repo_root: Path, task: str, max_files: int = 8, max_chars: int = 18000) -> dict:
    impact = impact_by_task(repo_root, task, limit=max_files * 2)
    lines = ["# UACOS Smart Context", "", f"Task: {task}", "", "## Impact Ranking"]
    for row in impact["impacted_files"][:max_files]:
        lines.append(f"- {row['file']} score={row['score']} reasons={','.join(row.get('reasons', []))}")

    base_chars = sum(len(x) for x in lines)
    plan_budget = max(1000, max_chars - base_chars - 600)
    plan = build_context_plan(
        repo_root,
        impact,
        max_chars=plan_budget,
        max_files=max_files,
        max_symbols_per_file=2,
    )

    included = []
    included_files = set()
    lines.extend(["", "## Planned Semantic Context"])
    for entry in plan.get("entries", []):
        role = str(entry.get("role") or "support")
        title = entry.get("symbol_id") or entry.get("file")
        chunk = (
            f"### {title}\n"
            f"- file: {entry['file']}\n"
            f"- role: {role}\n"
            f"- mode: {entry.get('mode')}\n"
            f"- lines: {entry.get('start_line')}-{entry.get('end_line')}\n"
            f"- allocated_chars: {entry.get('allocated_chars')}\n"
            f"- reasons: {', '.join(entry.get('reasons', []))}\n"
            f"```text\n{entry.get('content', '')}\n```\n"
        )
        if sum(len(x) for x in lines) + len(chunk) > max_chars:
            continue
        lines.append(chunk)
        included_files.add(entry["file"])
        included.append(
            {
                "file": entry["file"],
                "symbol_id": entry.get("symbol_id"),
                "role": role,
                "mode": entry.get("mode"),
                "start_line": entry.get("start_line"),
                "end_line": entry.get("end_line"),
                "allocated_chars": entry.get("allocated_chars"),
                "truncated_by_budget": bool(entry.get("truncated_by_budget")),
            }
        )

    content = "\n".join(lines)
    out_dir = repo_root / ".uacos" / "smart_context"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "latest_smart_context.md"
    out.write_text(content, encoding="utf-8")
    return {
        "status": "ok",
        "task": task,
        "included_files": sorted(included_files),
        "included_context": included,
        "symbol_slice_count": len([x for x in included if x.get("mode") == "symbol_slice"]),
        "role_counts": dict(plan.get("role_counts") or {}),
        "budget_utilization": plan.get("utilization"),
        "impact": impact,
        "context_plan": {
            key: value
            for key, value in plan.items()
            if key != "entries"
        },
        "context_file": str(out),
        "content": content,
        "char_count": len(content),
        "context_model": "dynamic_semantic_budget_v1",
    }


def impact_alignment_check(repo_root: Path, task: str, patch_file: Path, min_score: float = 0.15, limit: int = 50) -> dict:
    """Compare a patch's changed files against this task's dependency-graph impact ranking.

    This is a heuristic signal, not a hard safety boundary (unlike patch_gate's
    scope allowlist): impact ranking can miss legitimate files (new files,
    config, docs, tests) that a correct fix still needs to touch. Findings are
    informational — callers decide whether to warn or block.
    """
    text = patch_file.read_text(encoding="utf-8", errors="replace")
    changed = [p.path for p in parse_unified_diff(text)]
    impact = impact_by_task(repo_root, task, limit=limit)
    ranked = {row["file"]: row["score"] for row in impact["impacted_files"]}
    aligned = [f for f in changed if ranked.get(f, 0) >= min_score]
    unranked = [f for f in changed if ranked.get(f, 0) < min_score]
    status = "warn" if unranked else "pass"
    return {
        "status": status,
        "task": task,
        "changed_files": changed,
        "aligned_files": aligned,
        "unranked_files": unranked,
        "impacted_files": impact["impacted_files"],
    }
