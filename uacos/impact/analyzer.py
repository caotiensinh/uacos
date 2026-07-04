from __future__ import annotations

from pathlib import Path
import re
from uacos.graph.builder import load_graph
from uacos.graph.query import related_files, query_symbol
from uacos.search import search_repo
from uacos.security.diff_parser import parse_unified_diff

GENERIC_TASK_TOKENS = {"uacos", "module", "modules", "add", "fix", "update", "write", "handle", "type", "hints", "hint", "test", "docs", "class", "bug", "query", "endpoint"}

def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text) if len(t) >= 2]

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
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return {"status": "ok", "symbol": symbol, "impacted_files": ranked, "symbol_query": q}

def impact_by_task(repo_root: Path, task: str, limit: int = 10, depth: int = 2) -> dict:
    graph = load_graph(repo_root)
    scores = {}
    reasons = {}
    toks = _tokens(task)
    for tok in toks:
        if tok.lower() in GENERIC_TASK_TOKENS:
            continue
        q = query_symbol(repo_root, tok)
        if q["matches"]:
            sym_impact = impact_by_symbol(repo_root, tok, depth=depth)
            for row in sym_impact["impacted_files"]:
                scores[row["file"]] = max(scores.get(row["file"], 0), row["score"] + 0.5)
                reasons.setdefault(row["file"], []).append(f"symbol:{tok}")

    try:
        hits = search_repo(repo_root, task, limit=limit)
    except Exception:
        hits = []
    for i, hit in enumerate(hits):
        rel = hit.get("path") or hit.get("file_path")
        if not rel:
            continue
        score = max(0.1, 0.8 - i * 0.05)
        scores[rel] = max(scores.get(rel, 0), score)
        reasons.setdefault(rel, []).append("keyword_search")

    ranked = [{"file": f, "score": round(s, 4), "reasons": reasons.get(f, [])} for f, s in scores.items()]
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return {"status": "ok", "task": task, "impacted_files": ranked[:limit], "token_count": len(toks)}

def smart_context(repo_root: Path, task: str, max_files: int = 8, max_chars: int = 18000) -> dict:
    impact = impact_by_task(repo_root, task, limit=max_files)
    lines = ["# UACOS Smart Context", "", f"Task: {task}", "", "## Impact Ranking"]
    for row in impact["impacted_files"]:
        lines.append(f"- {row['file']} score={row['score']} reasons={','.join(row.get('reasons', []))}")
    lines.append("")
    included = []
    for row in impact["impacted_files"][:max_files]:
        path = repo_root / row["file"]
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        chunk = f"## File: {row['file']}\n\n```text\n{text[:3500]}\n```\n"
        if sum(len(x) for x in lines) + len(chunk) > max_chars:
            break
        lines.append(chunk)
        included.append(row["file"])
    content = "\n".join(lines)
    out_dir = repo_root / ".uacos" / "smart_context"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "latest_smart_context.md"
    out.write_text(content, encoding="utf-8")
    return {"status": "ok", "task": task, "included_files": included, "impact": impact, "context_file": str(out), "content": content, "char_count": len(content)}

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
