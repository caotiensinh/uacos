from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json, uuid, re
from uacos.config import uacos_dir

VALID_STATUS = {"candidate", "approved", "rejected", "deprecated"}

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def new_skill_id() -> str:
    return "SKILL-" + uuid.uuid4().hex[:12]

def skills_path(repo_root: Path) -> Path:
    p = uacos_dir(repo_root)
    p.mkdir(parents=True, exist_ok=True)
    return p / "skills.jsonl"

def _append(repo_root: Path, record: dict) -> None:
    with skills_path(repo_root).open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in re.findall(r"[A-Za-z0-9_\-\.\|]+", text or "") if len(t) >= 2]

def _normalize_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x) for x in v if str(x).strip()]
    return [str(v)]

def add_skill(repo_root: Path, title: str, problem_signatures=None, root_cause: str = "", solution_steps=None, commands=None, verification=None, applies_to=None, category: str = "general", source: str = "user", confidence: float = 0.8, status: str = "candidate", tags=None) -> dict:
    if status not in VALID_STATUS:
        raise ValueError(f"invalid_skill_status:{status}")
    skill = {
        "id": new_skill_id(), "title": title.strip(), "category": category,
        "problem_signatures": _normalize_list(problem_signatures),
        "root_cause": root_cause.strip(),
        "solution_steps": _normalize_list(solution_steps),
        "commands": _normalize_list(commands),
        "verification": _normalize_list(verification),
        "applies_to": _normalize_list(applies_to),
        "source": source, "confidence": float(confidence), "status": status,
        "tags": _normalize_list(tags), "times_used": 0, "last_used_at": None,
        "created_at": utcnow(), "updated_at": utcnow(),
        "deprecated_reason": None, "reject_reason": None,
    }
    _append(repo_root, skill)
    return skill

def read_skills(repo_root: Path, include_inactive: bool = False) -> list[dict]:
    path = skills_path(repo_root)
    if not path.exists():
        return []
    records, events = {}, []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("event"):
            events.append(rec)
        else:
            records[rec["id"]] = rec
    for ev in events:
        sid = ev.get("skill_id")
        if sid not in records:
            continue
        rec = dict(records[sid])
        if ev["event"] == "status":
            rec["status"] = ev["status"]
            rec["updated_at"] = ev["ts"]
            if ev.get("reason"):
                if ev["status"] == "rejected":
                    rec["reject_reason"] = ev["reason"]
                if ev["status"] == "deprecated":
                    rec["deprecated_reason"] = ev["reason"]
        elif ev["event"] == "use":
            rec["times_used"] = int(rec.get("times_used", 0)) + 1
            rec["last_used_at"] = ev["ts"]
            rec["updated_at"] = ev["ts"]
        records[sid] = rec
    out = list(records.values())
    if not include_inactive:
        out = [s for s in out if s.get("status") in {"candidate", "approved"}]
    return sorted(out, key=lambda s: (s.get("status") != "approved", -float(s.get("confidence", 0)), s.get("created_at", "")))

def get_skill(repo_root: Path, skill_id: str) -> dict | None:
    for s in read_skills(repo_root, include_inactive=True):
        if s["id"] == skill_id:
            return s
    return None

def set_skill_status(repo_root: Path, skill_id: str, status: str, reason: str = "") -> dict:
    if status not in VALID_STATUS:
        raise ValueError(f"invalid_skill_status:{status}")
    if get_skill(repo_root, skill_id) is None:
        raise KeyError(f"skill_not_found:{skill_id}")
    event = {"event": "status", "skill_id": skill_id, "status": status, "reason": reason, "ts": utcnow()}
    _append(repo_root, event)
    return event

def approve_skill(repo_root: Path, skill_id: str) -> dict:
    return set_skill_status(repo_root, skill_id, "approved", "")

def reject_skill(repo_root: Path, skill_id: str, reason: str) -> dict:
    return set_skill_status(repo_root, skill_id, "rejected", reason)

def deprecate_skill(repo_root: Path, skill_id: str, reason: str) -> dict:
    return set_skill_status(repo_root, skill_id, "deprecated", reason)

def mark_skill_used(repo_root: Path, skill_id: str, task: str = "") -> dict:
    if get_skill(repo_root, skill_id) is None:
        raise KeyError(f"skill_not_found:{skill_id}")
    event = {"event": "use", "skill_id": skill_id, "task": task, "ts": utcnow()}
    _append(repo_root, event)
    return event

def skill_score(skill: dict, query: str) -> float:
    terms = _tokenize(query)
    if not terms:
        return 0.0
    fields = [
        skill.get("title", ""), skill.get("category", ""), skill.get("root_cause", ""),
        " ".join(skill.get("problem_signatures", [])),
        " ".join(skill.get("solution_steps", [])),
        " ".join(skill.get("commands", [])),
        " ".join(skill.get("verification", [])),
        " ".join(skill.get("applies_to", [])),
        " ".join(skill.get("tags", [])),
    ]
    hay = " ".join(fields).lower()
    sig_hay = " ".join(skill.get("problem_signatures", [])).lower()
    score = sum(1.0 for t in terms if t in hay)
    score += sum(0.75 for t in terms if t in sig_hay)
    if skill.get("status") == "approved":
        score += 1.0
    score += min(float(skill.get("confidence", 0.0)), 1.0)
    score += min(int(skill.get("times_used", 0)), 10) * 0.05
    return score

def search_skills(repo_root: Path, query: str, include_inactive: bool = False, limit: int = 10) -> list[dict]:
    rows = []
    for skill in read_skills(repo_root, include_inactive=include_inactive):
        score = skill_score(skill, query)
        if score > 0 or not query.strip():
            item = dict(skill)
            item["_score"] = round(score, 4)
            rows.append(item)
    rows.sort(key=lambda s: s["_score"], reverse=True)
    return rows[:limit]

def suggest_skills(repo_root: Path, task: str, limit: int = 5, min_score: float = 1.0) -> list[dict]:
    return [r for r in search_skills(repo_root, task, include_inactive=False, limit=limit) if r.get("_score", 0) >= min_score]

def skill_summary_for_task(repo_root: Path, task: str, limit: int = 5) -> str:
    rows = suggest_skills(repo_root, task, limit=limit, min_score=1.0)
    if not rows:
        return "No reusable skills matched this task."
    lines = ["# Relevant Reusable Skills", ""]
    for s in rows:
        lines.append(f"- [{s['status']}] {s['title']} (id={s['id']}, score={s.get('_score')}, used={s.get('times_used', 0)})")
        if s.get("problem_signatures"):
            lines.append(f"  - signatures: {', '.join(s['problem_signatures'][:5])}")
        if s.get("solution_steps"):
            lines.append(f"  - solution: {'; '.join(s['solution_steps'][:3])}")
        if s.get("commands"):
            lines.append(f"  - commands: {'; '.join(s['commands'][:3])}")
    return "\n".join(lines) + "\n"
