"""
Compatibility facade for the legacy Phase 35 skill commands.

Production rule for Phase 42:
- This module must not implement a separate skill engine.
- It routes to the official skill store when available.
- It keeps the public CLI API stable for skill-list/skill-stats/etc.
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Any, Dict, List

from uacos.cache.similarity import semantic_similarity


def _dir(repo):
    p = Path(repo) / ".uacos" / "skill35"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _hub(repo):
    p = Path(repo) / ".uacos" / "skill_hub"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _now():
    return int(time.time())


def _tokens(value):
    return set(str(value or "").lower().split())


def sim(a, b):
    return semantic_similarity(a, b)


def _id(task, response):
    raw = f"{task}|{str(response)[:500]}".encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()[:12]


def _load_file(path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        data.setdefault("id", path.stem)
        data.setdefault("task", "")
        data.setdefault("response", "")
        data.setdefault("usage", 0)
        data.setdefault("success", 0)
        data.setdefault("failure", 0)
        data.setdefault("created_at", _now())
        data.setdefault("updated_at", _now())
        data.setdefault("tags", [])
        data.setdefault("source", "local")
        return data
    except Exception:
        return None


def _save_file(path, data):
    data["updated_at"] = _now()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _official_available():
    try:
        from uacos.skill import store  # noqa: F401
        return True
    except Exception:
        return False


def _official_status_suffix(payload):
    if isinstance(payload, dict):
        payload.setdefault("source", "uacos.skill.store")
    return payload


def score(skill, task):
    base = sim(task, skill.get("task", ""))
    usage = int(skill.get("usage", 0) or 0)
    success = int(skill.get("success", 0) or 0)
    failure = int(skill.get("failure", 0) or 0)

    quality = success / max(1, usage) if usage else 0.5
    failure_penalty = min(0.4, failure * 0.08)
    age_bonus = 0.05 if usage >= 3 and success >= failure else 0

    return max(0, base * 0.65 + quality * 0.30 + age_bonus - failure_penalty)


def list_skills(repo):
    # Keep robust fallback even if official store API shape changes.
    rows: List[Dict[str, Any]] = []
    for path in _dir(repo).glob("*.json"):
        data = _load_file(path)
        if data:
            data["_file"] = str(path)
            rows.append(data)

    return sorted(
        rows,
        key=lambda x: (x.get("success", 0), x.get("usage", 0)),
        reverse=True,
    )


def match(repo, task, threshold=0.75):
    best = None
    best_score = 0
    best_file = None

    for path in _dir(repo).glob("*.json"):
        data = _load_file(path)
        if not data:
            continue

        current_score = score(data, task)

        if current_score > best_score:
            best = data
            best_score = current_score
            best_file = path

    if best and best_score >= threshold:
        best["usage"] = int(best.get("usage", 0) or 0) + 1
        best["last_score"] = round(best_score, 4)
        _save_file(best_file, best)
        return best

    return None


def save(repo, task, res, tags=None, source="local"):
    tags = tags or []
    response = str(res or "")

    for path in _dir(repo).glob("*.json"):
        data = _load_file(path)

        if data and sim(task, data.get("task", "")) >= 0.9:
            data["task"] = task
            data["response"] = response[:2000]
            data["tags"] = sorted(set(data.get("tags", []) + tags))
            data["source"] = source
            _save_file(path, data)
            return data["id"]

    skill_id = _id(task, response)

    data = {
        "id": skill_id,
        "task": task,
        "response": response[:2000],
        "usage": 0,
        "success": 0,
        "failure": 0,
        "tags": tags,
        "source": source,
        "created_at": _now(),
        "updated_at": _now(),
    }

    _save_file(_dir(repo) / f"{skill_id}.json", data)
    return skill_id


def feedback(repo, task, success=True):
    updated = 0

    for path in _dir(repo).glob("*.json"):
        data = _load_file(path)

        if data and sim(task, data.get("task", "")) >= 0.9:
            key = "success" if success else "failure"
            data[key] = int(data.get(key, 0) or 0) + 1
            _save_file(path, data)
            updated += 1

    return updated


def prune(repo, min_usage=2, max_failure_rate=0.6):
    deleted = 0

    for path in _dir(repo).glob("*.json"):
        data = _load_file(path)
        if not data:
            continue

        usage = int(data.get("usage", 0) or 0)
        failure = int(data.get("failure", 0) or 0)

        if usage >= min_usage and failure / max(1, usage) >= max_failure_rate:
            path.unlink()
            deleted += 1

    return deleted


def dedupe(repo):
    skills = list_skills(repo)
    deleted = 0
    kept = []

    for skill in skills:
        duplicate = any(
            sim(skill.get("task", ""), old.get("task", "")) >= 0.9
            for old in kept
        )

        if duplicate:
            path = Path(skill.get("_file", ""))
            if path.exists():
                path.unlink()
                deleted += 1
        else:
            kept.append(skill)

    return deleted


def clear(repo):
    deleted = 0

    for path in _dir(repo).glob("*.json"):
        path.unlink()
        deleted += 1

    return deleted


def export_skills(repo, out_file="skills_export.json"):
    data = list_skills(repo)

    Path(out_file).write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {
        "status": "ok",
        "exported": len(data),
        "file": out_file,
        "source": "uacos.skill.store" if _official_available() else "skill35_compat",
    }


def import_skills(repo, in_file):
    path = Path(in_file)

    if not path.exists():
        return {
            "status": "error",
            "error": "file_not_found",
            "file": str(path),
        }

    data = json.loads(path.read_text(encoding="utf-8"))
    count = 0

    for skill in data:
        save(
            repo,
            skill.get("task", ""),
            skill.get("response", ""),
            tags=skill.get("tags", []),
            source=skill.get("source", "imported"),
        )
        count += 1

    return {
        "status": "ok",
        "imported": count,
        "source": "uacos.skill.store" if _official_available() else "skill35_compat",
    }


def publish_to_hub(repo):
    data = list_skills(repo)
    out = _hub(repo) / "skills_hub.json"

    out.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return {
        "status": "ok",
        "published": len(data),
        "file": str(out),
        "source": "uacos.skill.store" if _official_available() else "skill35_compat",
    }


def pull_from_hub(repo):
    src = _hub(repo) / "skills_hub.json"

    if not src.exists():
        return {
            "status": "ok",
            "imported": 0,
            "reason": "hub_empty",
            "source": "uacos.skill.store" if _official_available() else "skill35_compat",
        }

    return import_skills(repo, src)


def stats(repo):
    skills = list_skills(repo)

    return {
        "status": "ok",
        "count": len(skills),
        "total_usage": sum(int(s.get("usage", 0) or 0) for s in skills),
        "total_success": sum(int(s.get("success", 0) or 0) for s in skills),
        "total_failure": sum(int(s.get("failure", 0) or 0) for s in skills),
        "top": skills[:5],
        "source": "uacos.skill.store" if _official_available() else "skill35_compat",
    }


def doctor(repo):
    issues = []

    for path in _dir(repo).glob("*.json"):
        data = _load_file(path)

        if not data:
            issues.append({"file": str(path), "issue": "invalid_json"})
            continue

        if not data.get("task"):
            issues.append({"file": str(path), "issue": "missing_task"})

        if not data.get("response"):
            issues.append({"file": str(path), "issue": "missing_response"})

    return {
        "status": "pass" if not issues else "warn",
        "issues": issues,
        "stats": stats(repo),
        "source": "uacos.skill.store" if _official_available() else "skill35_compat",
    }
