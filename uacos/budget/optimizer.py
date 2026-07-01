from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re

from uacos.config import uacos_dir
from uacos.llm.hardened import estimate_tokens
from uacos.impact.analyzer import impact_by_task
from uacos.semantic.search import semantic_search, build_semantic_index
from uacos.skill.store import suggest_skills
from uacos.memory.store import search_memories
from uacos.scanner.file_scanner import scan_repo

BUDGET_PROFILES = {
    "tiny": {"max_tokens": 2500, "max_files": 3, "per_file_tokens": 650, "memory_tokens": 350, "skill_tokens": 350},
    "small": {"max_tokens": 4500, "max_files": 5, "per_file_tokens": 850, "memory_tokens": 500, "skill_tokens": 500},
    "medium": {"max_tokens": 8000, "max_files": 8, "per_file_tokens": 1000, "memory_tokens": 800, "skill_tokens": 800},
    "large": {"max_tokens": 12000, "max_files": 12, "per_file_tokens": 1100, "memory_tokens": 1200, "skill_tokens": 1200},
    "architecture": {"max_tokens": 10000, "max_files": 6, "per_file_tokens": 650, "memory_tokens": 1800, "skill_tokens": 1200},
}

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def budget_dir(repo_root: Path) -> Path:
    p = uacos_dir(repo_root) / "budget"
    p.mkdir(parents=True, exist_ok=True)
    return p

def summary_cache_path(repo_root: Path) -> Path:
    return budget_dir(repo_root) / "file_summary_cache.json"

def report_path(repo_root: Path) -> Path:
    return budget_dir(repo_root) / "latest_context_budget_report.json"

def classify_task(task: str) -> dict:
    low = task.lower()
    score = 0
    if any(k in low for k in ["architecture", "design", "roadmap", "spec", "tổng thể", "kiến trúc"]):
        return {"size": "architecture", "reason": "architecture_keyword"}
    if any(k in low for k in ["refactor", "cross-file", "workflow", "pipeline", "integration", "multi-file"]):
        score += 3
    if any(k in low for k in ["fix", "bug", "error", "traceback", "lỗi"]):
        score += 1
    if any(k in low for k in ["small", "minor", "typo"]):
        score -= 1
    wc = len(task.split())
    if wc > 80: score += 2
    elif wc > 35: score += 1
    if score <= 0:
        size = "tiny"
    elif score == 1:
        size = "small"
    elif score <= 3:
        size = "medium"
    else:
        size = "large"
    return {"size": size, "reason": f"heuristic_score:{score}", "word_count": wc}

def load_summary_cache(repo_root: Path) -> dict:
    p = summary_cache_path(repo_root)
    if not p.exists():
        return {"version": 1, "files": {}, "updated_at": None}
    return json.loads(p.read_text(encoding="utf-8"))

def save_summary_cache(repo_root: Path, cache: dict) -> dict:
    cache["updated_at"] = utcnow()
    p = summary_cache_path(repo_root)
    p.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "ok", "cache_file": str(p)}

def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def summarize_file(repo_root: Path, rel: str, max_chars: int = 2600) -> dict:
    path = repo_root / rel
    text = path.read_text(encoding="utf-8", errors="replace")
    funcs = re.findall(r"(?m)^\s*(?:async\s+def|def)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", text)
    classes = re.findall(r"(?m)^\s*class\s+([A-Za-z_][A-Za-z0-9_]*)", text)
    imports = re.findall(r"(?m)^\s*(?:from\s+\S+\s+import\s+.+|import\s+.+)$", text)
    head = "\n".join([l for l in text.splitlines()[:80]])[:max_chars]
    return {
        "path": rel,
        "sha256": _sha(path),
        "line_count": text.count("\n") + 1 if text else 0,
        "tokens_est": estimate_tokens(text),
        "functions": funcs[:80],
        "classes": classes[:40],
        "imports": imports[:50],
        "summary_text": head,
        "summarized_at": utcnow(),
    }

def update_summary_cache(repo_root: Path, files: list[str] | None = None) -> dict:
    cache = load_summary_cache(repo_root)
    entries = cache.setdefault("files", {})
    if files is None:
        files = [str(p.relative_to(repo_root)).replace("\\", "/") for p in repo_root.rglob("*") if p.is_file() and p.suffix.lower() in {".py", ".js", ".ts", ".md"} and ".uacos" not in p.parts and "__pycache__" not in p.parts]
    updated = 0
    skipped = 0
    for rel in files:
        path = repo_root / rel
        if not path.exists() or not path.is_file():
            continue
        sha = _sha(path)
        if entries.get(rel, {}).get("sha256") == sha:
            skipped += 1
            continue
        entries[rel] = summarize_file(repo_root, rel)
        updated += 1
    save_summary_cache(repo_root, cache)
    return {"status": "ok", "updated": updated, "skipped": skipped, "file_count": len(entries), "cache_file": str(summary_cache_path(repo_root))}

def _score_files(repo_root: Path, task: str, max_candidates: int = 20) -> dict:
    scores = {}
    reasons = {}
    def add(rel, score, reason):
        if not rel:
            return
        scores[rel] = max(scores.get(rel, 0.0), score)
        reasons.setdefault(rel, []).append(reason)

    try:
        impact = impact_by_task(repo_root, task, limit=max_candidates)
        for row in impact.get("impacted_files", []):
            add(row["file"], 1.3 * float(row.get("score", 0.0)), "impact")
    except Exception as exc:
        impact = {"status": "error", "error": str(exc)}

    try:
        build_semantic_index(repo_root)
        sem = semantic_search(repo_root, task, limit=max_candidates, min_score=0.01)
        for row in sem.get("results", []):
            payload = row.get("payload") or {}
            rel = payload.get("path") or payload.get("key")
            # skill/memory semantic hits are handled in their own sections; file path only if available
            if rel and (repo_root / rel).exists():
                add(rel, 0.8 * float(row.get("score", 0.0)), "semantic")
    except Exception as exc:
        sem = {"status": "error", "error": str(exc)}

    # keyword fallback from filenames/content snippets
    toks = [t.lower() for t in re.findall(r"[A-Za-z_][A-Za-z0-9_]+", task) if len(t) >= 3]
    for p in repo_root.rglob("*"):
        if not p.is_file() or ".uacos" in p.parts or "__pycache__" in p.parts:
            continue
        if p.suffix.lower() not in {".py", ".js", ".ts", ".md", ".go", ".rs", ".java"}:
            continue
        rel = str(p.relative_to(repo_root)).replace("\\", "/")
        name_score = sum(1 for t in toks if t in rel.lower()) * 0.35
        if name_score:
            add(rel, name_score, "filename")
    ranked = [{"file": rel, "score": round(score, 4), "reasons": reasons.get(rel, [])} for rel, score in scores.items()]
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return {"ranked": ranked[:max_candidates], "impact": impact, "semantic": sem}

def build_budgeted_context(repo_root: Path, task: str, profile: str | None = None, max_tokens: int | None = None) -> dict:
    scan_repo(repo_root)
    task_class = classify_task(task)
    profile = profile or task_class["size"]
    budget = dict(BUDGET_PROFILES.get(profile, BUDGET_PROFILES["medium"]))
    if max_tokens:
        budget["max_tokens"] = max_tokens
    update_summary_cache(repo_root)
    cache = load_summary_cache(repo_root)

    ranking = _score_files(repo_root, task, max_candidates=max(20, budget["max_files"] * 2))
    skills = suggest_skills(repo_root, task, limit=5, min_score=1.0)
    try:
        memories = search_memories(repo_root, task, limit=5)
    except Exception:
        memories = []

    lines = ["# UACOS Budgeted Context", "", f"Task: {task}", f"Profile: {profile}", f"Budget: {budget['max_tokens']} tokens", "", "## Relevant Skills"]
    skill_tokens = 0
    for s in skills:
        chunk = f"- {s.get('title')} id={s.get('id')} score={s.get('_score')}\n  solution: {'; '.join(s.get('solution_steps', [])[:3])}\n"
        t = estimate_tokens(chunk)
        if skill_tokens + t <= budget["skill_tokens"]:
            lines.append(chunk.rstrip())
            skill_tokens += t
    lines.append("")
    lines.append("## Relevant Memories")
    mem_tokens = 0
    for m in memories:
        chunk = f"- {m.get('key')} ({m.get('kind')}): {str(m.get('value',''))[:500]}\n"
        t = estimate_tokens(chunk)
        if mem_tokens + t <= budget["memory_tokens"]:
            lines.append(chunk.rstrip())
            mem_tokens += t

    lines.append("")
    lines.append("## Ranked Files")
    selected = []
    used_tokens = estimate_tokens("\n".join(lines))
    per_file = budget["per_file_tokens"]
    for row in ranking["ranked"]:
        if len(selected) >= budget["max_files"]:
            break
        rel = row["file"]
        item = cache.get("files", {}).get(rel)
        if not item:
            continue
        summary = item.get("summary_text", "")
        file_chunk = [
            f"### {rel}",
            f"- score: {row['score']}",
            f"- reasons: {', '.join(row.get('reasons', []))}",
            f"- lines: {item.get('line_count')}",
        ]
        if item.get("classes"):
            file_chunk.append(f"- classes: {', '.join(item['classes'][:20])}")
        if item.get("functions"):
            file_chunk.append(f"- functions: {', '.join(item['functions'][:30])}")
        file_chunk.append("```text\n" + summary[:per_file * 4] + "\n```")
        chunk = "\n".join(file_chunk) + "\n"
        t = estimate_tokens(chunk)
        if used_tokens + t > budget["max_tokens"]:
            continue
        lines.append(chunk)
        used_tokens += t
        selected.append({"file": rel, "score": row["score"], "tokens_est": t, "reasons": row.get("reasons", [])})

    content = "\n".join(lines)
    out = budget_dir(repo_root) / "latest_budgeted_context.md"
    out.write_text(content, encoding="utf-8")
    report = {
        "status": "ok",
        "task": task,
        "profile": profile,
        "task_class": task_class,
        "budget": budget,
        "selected_files": selected,
        "selected_file_count": len(selected),
        "skills_count": len(skills),
        "memories_count": len(memories),
        "tokens_est": estimate_tokens(content),
        "context_file": str(out),
        "content": content,
        "created_at": utcnow(),
    }
    report_path(repo_root).write_text(json.dumps({k:v for k,v in report.items() if k != "content"}, ensure_ascii=False, indent=2), encoding="utf-8")
    return report

def budget_report(repo_root: Path) -> dict:
    p = report_path(repo_root)
    if not p.exists():
        return {"status": "missing", "reason": "no budget report yet"}
    return json.loads(p.read_text(encoding="utf-8"))
