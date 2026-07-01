from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
from uacos.config import uacos_dir
from uacos.skill.store import get_skill, search_skills, read_skills
from uacos.skill.executor import read_skill_execution_history, skill_execution_summary
from uacos.autopilot.orchestrator import list_autopilot_runs, load_autopilot_run

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def feedback_events_path(repo_root: Path) -> Path:
    p = uacos_dir(repo_root)
    p.mkdir(parents=True, exist_ok=True)
    return p / "feedback_events.jsonl"

def feedback_scores_path(repo_root: Path) -> Path:
    p = uacos_dir(repo_root)
    p.mkdir(parents=True, exist_ok=True)
    return p / "skill_feedback_scores.json"

def _append_event(repo_root: Path, event: dict) -> dict:
    event = dict(event)
    event.setdefault("ts", utcnow())
    with feedback_events_path(repo_root).open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event

def read_feedback_events(repo_root: Path) -> list[dict]:
    path = feedback_events_path(repo_root)
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows

def load_feedback_scores(repo_root: Path) -> dict:
    path = feedback_scores_path(repo_root)
    if not path.exists():
        return {"version": 1, "skills": {}, "updated_at": None}
    return json.loads(path.read_text(encoding="utf-8"))

def save_feedback_scores(repo_root: Path, scores: dict) -> dict:
    scores["updated_at"] = utcnow()
    path = feedback_scores_path(repo_root)
    path.write_text(json.dumps(scores, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "ok", "scores_file": str(path)}

def _ensure_skill_score(scores: dict, skill_id: str) -> dict:
    skills = scores.setdefault("skills", {})
    if skill_id not in skills:
        skills[skill_id] = {
            "skill_id": skill_id,
            "success_count": 0,
            "failure_count": 0,
            "blocked_count": 0,
            "dry_run_count": 0,
            "last_status": None,
            "last_event_at": None,
            "reliability": 0.5,
            "confidence_delta": 0.0,
        }
    return skills[skill_id]

def _recompute_score(row: dict) -> dict:
    success = int(row.get("success_count", 0))
    failure = int(row.get("failure_count", 0))
    blocked = int(row.get("blocked_count", 0))
    dry = int(row.get("dry_run_count", 0))
    # Conservative Bayesian-like score.
    total_real = success + failure + blocked
    row["reliability"] = round((success + 1) / (total_real + 2), 4)
    row["activity"] = success + failure + blocked + dry
    row["confidence_delta"] = round((success * 0.03) - (failure * 0.06) - (blocked * 0.03), 4)
    return row

def ingest_skill_execution(repo_root: Path, execution_file: Path | None = None, execution: dict | None = None) -> dict:
    if execution is None:
        if execution_file is None:
            raise ValueError("execution_file_or_execution_required")
        execution = json.loads(execution_file.read_text(encoding="utf-8"))
    skill_id = execution.get("skill_id")
    if not skill_id:
        raise ValueError("execution_missing_skill_id")
    status = execution.get("status")
    scores = load_feedback_scores(repo_root)
    row = _ensure_skill_score(scores, skill_id)
    if status == "done":
        row["success_count"] += 1
    elif status == "failed":
        row["failure_count"] += 1
    elif status == "blocked":
        row["blocked_count"] += 1
    elif status == "dry_run":
        row["dry_run_count"] += 1
    else:
        row["failure_count"] += 1
    row["last_status"] = status
    row["last_event_at"] = utcnow()
    _recompute_score(row)
    save_feedback_scores(repo_root, scores)
    event = _append_event(repo_root, {
        "event": "ingest_skill_execution",
        "skill_id": skill_id,
        "execution_id": execution.get("id"),
        "execution_status": status,
        "score": row,
    })
    return {"status": "ok", "skill_id": skill_id, "score": row, "event": event}

def ingest_all_skill_executions(repo_root: Path) -> dict:
    rows = read_skill_execution_history(repo_root)
    done = []
    for row in rows:
        f = row.get("execution_file")
        if f and Path(f).exists():
            done.append(ingest_skill_execution(repo_root, execution_file=Path(f)))
    return {"status": "ok", "ingested": len(done), "results": done[-20:]}

def ingest_autopilot_run(repo_root: Path, run_id: str) -> dict:
    run = load_autopilot_run(repo_root, run_id)
    status = run.get("status")
    skill_id = (run.get("summary") or {}).get("learning_skill_id")
    event = _append_event(repo_root, {
        "event": "ingest_autopilot_run",
        "run_id": run_id,
        "run_status": status,
        "learning_skill_id": skill_id,
        "task_id": run.get("task_id"),
        "task_title": run.get("task_title"),
    })
    return {"status": "ok", "run_id": run_id, "run_status": status, "event": event}

def skill_feedback_score(repo_root: Path, skill_id: str) -> dict:
    scores = load_feedback_scores(repo_root)
    row = scores.get("skills", {}).get(skill_id)
    if not row:
        row = _ensure_skill_score(scores, skill_id)
        _recompute_score(row)
    skill = get_skill(repo_root, skill_id)
    return {"status": "ok", "skill": skill, "score": row}

def recommend_skills(repo_root: Path, task: str, limit: int = 5) -> dict:
    candidates = search_skills(repo_root, task, include_inactive=False, limit=max(limit * 3, 10))
    scores = load_feedback_scores(repo_root).get("skills", {})
    ranked = []
    for skill in candidates:
        sid = skill["id"]
        fb = scores.get(sid, {"reliability": 0.5, "activity": 0, "confidence_delta": 0.0})
        base = float(skill.get("_score", 0))
        reliability = float(fb.get("reliability", 0.5))
        activity = min(int(fb.get("activity", 0)), 20) * 0.02
        final = base + reliability + activity + float(fb.get("confidence_delta", 0.0))
        item = dict(skill)
        item["feedback"] = fb
        item["recommendation_score"] = round(final, 4)
        ranked.append(item)
    ranked.sort(key=lambda x: x["recommendation_score"], reverse=True)
    return {"status": "ok", "task": task, "recommendations": ranked[:limit]}

def feedback_summary(repo_root: Path) -> dict:
    events = read_feedback_events(repo_root)
    scores = load_feedback_scores(repo_root)
    skills = scores.get("skills", {})
    by_last_status = {}
    for row in skills.values():
        st = row.get("last_status") or "unknown"
        by_last_status[st] = by_last_status.get(st, 0) + 1
    top = sorted(skills.values(), key=lambda r: (r.get("reliability", 0), r.get("activity", 0)), reverse=True)[:10]
    return {
        "status": "ok",
        "feedback_events": len(events),
        "tracked_skills": len(skills),
        "by_last_status": by_last_status,
        "top_skills": top,
        "recent_events": events[-20:],
    }
