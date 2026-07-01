from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import re
from uacos.config import uacos_dir
from uacos.skill.extract import extract_skill_from_text, extract_skill_from_file, extract_problem_signatures, extract_commands
from uacos.skill.store import search_skills, read_skills
from uacos.memory.store import add_memory, search_memories, read_memories

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def learning_events_path(repo_root: Path) -> Path:
    p = uacos_dir(repo_root)
    p.mkdir(parents=True, exist_ok=True)
    return p / "learning_events.jsonl"

def _append_event(repo_root: Path, event: dict) -> dict:
    event = dict(event)
    event.setdefault("ts", utcnow())
    with learning_events_path(repo_root).open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event

def read_learning_events(repo_root: Path) -> list[dict]:
    path = learning_events_path(repo_root)
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows

def _clip(text: str, limit: int = 1200) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[:limit] + "..."

def _classify_text(text: str) -> dict:
    low = text.lower()
    kind = "note"
    severity = "low"
    if "traceback" in low or "error" in low or "failed" in low or "exception" in low:
        kind = "failure"
        severity = "high"
    elif "rollback" in low or "rolled_back" in low:
        kind = "failure"
        severity = "high"
    elif "root cause" in low or "fix:" in low or "solution" in low:
        kind = "lesson"
        severity = "medium"
    return {"kind": kind, "severity": severity}

def _duplicate_skill_candidates(repo_root: Path, title: str, text: str, limit: int = 5) -> list[dict]:
    query = title + " " + " ".join(extract_problem_signatures(text)[:5])
    if not query.strip():
        query = text[:500]
    rows = search_skills(repo_root, query, include_inactive=False, limit=limit)
    # Keep only plausible duplicate matches.
    return [r for r in rows if r.get("_score", 0) >= 2.0]

def _memory_key_from_title(title: str) -> str:
    key = re.sub(r"[^A-Za-z0-9_]+", "_", title.strip().lower()).strip("_")
    return key[:80] or "learning_note"

def learn_from_text(
    repo_root: Path,
    text: str,
    title: str,
    source: str = "manual",
    category: str = "auto_learning",
    auto_approve: bool = False,
    create_memory: bool = True,
) -> dict:
    classification = _classify_text(text)
    duplicates = _duplicate_skill_candidates(repo_root, title, text)
    skill = extract_skill_from_text(
        repo_root,
        text,
        title=title,
        category=category,
        source=source,
        auto_approve=auto_approve,
    )
    memory = None
    if create_memory:
        mem_kind = "failure" if classification["kind"] == "failure" else "note"
        memory = add_memory(
            repo_root,
            kind=mem_kind,
            key=_memory_key_from_title(title),
            value=_clip(text),
            source=source,
            confidence=0.75 if classification["kind"] == "failure" else 0.65,
            tags=["auto_learning", classification["kind"], classification["severity"]],
            applies_to=[],
        )
    event = _append_event(repo_root, {
        "event": "learn_from_text",
        "title": title,
        "source": source,
        "classification": classification,
        "skill_id": skill["id"],
        "skill_status": skill["status"],
        "memory_id": memory["id"] if memory else None,
        "duplicate_skill_candidates": [{"id": d["id"], "title": d["title"], "score": d.get("_score")} for d in duplicates],
    })
    return {
        "status": "ok",
        "classification": classification,
        "skill": skill,
        "memory": memory,
        "duplicates": duplicates,
        "event": event,
    }

def learn_from_file(
    repo_root: Path,
    source_file: Path,
    title: str,
    category: str = "auto_learning",
    auto_approve: bool = False,
    create_memory: bool = True,
) -> dict:
    text = source_file.read_text(encoding="utf-8", errors="replace")
    return learn_from_text(
        repo_root,
        text,
        title=title,
        source=str(source_file),
        category=category,
        auto_approve=auto_approve,
        create_memory=create_memory,
    )

def _manifest_text(manifest: dict) -> str:
    parts = [
        "Manifest learning source",
        f"status: {manifest.get('status')}",
        f"task_id: {manifest.get('task_id')}",
        f"rolled_back: {manifest.get('rolled_back')}",
    ]
    if manifest.get("error"):
        parts.append("error: " + json.dumps(manifest.get("error"), ensure_ascii=False))
    if manifest.get("test_result"):
        parts.append("test_result: " + json.dumps(manifest.get("test_result"), ensure_ascii=False)[:4000])
    if manifest.get("patch_check"):
        parts.append("patch_check: " + json.dumps(manifest.get("patch_check"), ensure_ascii=False)[:4000])
    return "\n".join(parts)

def learn_from_manifest(repo_root: Path, manifest_file: Path, auto_approve: bool = False) -> dict:
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    title = f"Learn from manifest {manifest.get('id', manifest_file.stem)}"
    text = _manifest_text(manifest)
    result = learn_from_text(
        repo_root,
        text,
        title=title,
        source=str(manifest_file),
        category="manifest_learning",
        auto_approve=auto_approve,
        create_memory=True,
    )
    result["manifest"] = manifest
    return result

def learn_review(repo_root: Path) -> dict:
    candidate_skills = [s for s in read_skills(repo_root, include_inactive=True) if s.get("status") == "candidate"]
    auto_memories = [m for m in read_memories(repo_root, include_invalid=False) if "auto_learning" in m.get("tags", [])]
    events = read_learning_events(repo_root)
    return {
        "status": "ok",
        "candidate_skill_count": len(candidate_skills),
        "candidate_skills": candidate_skills,
        "auto_memory_count": len(auto_memories),
        "auto_memories": auto_memories,
        "learning_event_count": len(events),
        "recent_events": events[-20:],
    }

def learn_summary(repo_root: Path) -> dict:
    skills = read_skills(repo_root, include_inactive=True)
    events = read_learning_events(repo_root)
    memories = read_memories(repo_root, include_invalid=False)
    by_status = {}
    for s in skills:
        by_status[s.get("status", "unknown")] = by_status.get(s.get("status", "unknown"), 0) + 1
    auto_mem = [m for m in memories if "auto_learning" in m.get("tags", [])]
    return {
        "status": "ok",
        "skills_total": len(skills),
        "skills_by_status": by_status,
        "auto_learning_memories": len(auto_mem),
        "learning_events": len(events),
        "last_event": events[-1] if events else None,
    }
