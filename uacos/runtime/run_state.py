from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import json
import os
import uuid

from uacos.config import uacos_dir


TERMINAL = {"passed", "failed", "blocked", "cancelled", "timed_out"}
ALLOWED_TRANSITIONS = {
    "queued": {"running", "cancelled", "timed_out"},
    "running": {"awaiting_patch", "validating", "retrying", "passed", "failed", "blocked", "cancelled", "timed_out"},
    "awaiting_patch": {"validating", "retrying", "failed", "blocked", "cancelled", "timed_out"},
    "validating": {"testing", "retrying", "passed", "failed", "blocked", "cancelled", "timed_out"},
    "testing": {"retrying", "passed", "failed", "blocked", "cancelled", "timed_out"},
    "retrying": {"running", "failed", "blocked", "cancelled", "timed_out"},
    "passed": set(),
    "failed": set(),
    "blocked": set(),
    "cancelled": set(),
    "timed_out": set(),
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _run_dir(repo_root: Path) -> Path:
    path = uacos_dir(repo_root) / "run_state"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _run_path(repo_root: Path, run_id: str) -> Path:
    return _run_dir(repo_root) / f"{run_id}.json"


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def create_run_state(
    repo_root: Path,
    task: str,
    *,
    max_iterations: int = 3,
    deadline_seconds: int | None = None,
    run_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if max_iterations < 1:
        raise ValueError("max_iterations_must_be_positive")
    now = _utcnow()
    rid = run_id or "RUN-" + uuid.uuid4().hex[:12]
    path = _run_path(repo_root, rid)
    if path.exists():
        existing = load_run_state(repo_root, rid)
        if existing.get("task") != task:
            raise ValueError("run_id_collision")
        return existing | {"idempotent_replay": True}

    payload = {
        "run_id": rid,
        "task": task,
        "status": "queued",
        "iteration": 0,
        "max_iterations": int(max_iterations),
        "cancel_requested": False,
        "created_at": _iso(now),
        "updated_at": _iso(now),
        "deadline_at": _iso(now + timedelta(seconds=deadline_seconds)) if deadline_seconds else None,
        "metadata": dict(metadata or {}),
        "events": [
            {
                "seq": 1,
                "ts": _iso(now),
                "from": None,
                "to": "queued",
                "reason": "created",
                "idempotency_key": None,
                "evidence": {},
            }
        ],
        "idempotency_keys": [],
    }
    _atomic_write(path, payload)
    return payload


def load_run_state(repo_root: Path, run_id: str) -> dict[str, Any]:
    path = _run_path(repo_root, run_id)
    if not path.exists():
        raise FileNotFoundError(run_id)
    return json.loads(path.read_text(encoding="utf-8"))


def transition_run(
    repo_root: Path,
    run_id: str,
    to_status: str,
    *,
    reason: str,
    evidence: dict[str, Any] | None = None,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    state = load_run_state(repo_root, run_id)
    current = str(state["status"])
    if idempotency_key and idempotency_key in state.get("idempotency_keys", []):
        return state | {"idempotent_replay": True}
    if to_status == current:
        return state | {"idempotent_replay": True}
    if to_status not in ALLOWED_TRANSITIONS.get(current, set()):
        raise ValueError(f"invalid_transition:{current}->{to_status}")

    now = _utcnow()
    state["status"] = to_status
    state["updated_at"] = _iso(now)
    event = {
        "seq": len(state.get("events", [])) + 1,
        "ts": _iso(now),
        "from": current,
        "to": to_status,
        "reason": reason,
        "idempotency_key": idempotency_key,
        "evidence": dict(evidence or {}),
    }
    state.setdefault("events", []).append(event)
    if idempotency_key:
        state.setdefault("idempotency_keys", []).append(idempotency_key)
    _atomic_write(_run_path(repo_root, run_id), state)
    return state


def begin_iteration(repo_root: Path, run_id: str, *, idempotency_key: str | None = None) -> dict[str, Any]:
    state = load_run_state(repo_root, run_id)
    if idempotency_key and idempotency_key in state.get("idempotency_keys", []):
        return state | {"idempotent_replay": True}
    if state["status"] in TERMINAL:
        raise ValueError(f"terminal_run:{state['status']}")
    if int(state["iteration"]) >= int(state["max_iterations"]):
        return transition_run(
            repo_root,
            run_id,
            "failed",
            reason="max_iterations_exhausted",
            idempotency_key=idempotency_key,
        )

    if state["status"] == "queued":
        state = transition_run(repo_root, run_id, "running", reason="iteration_started")
    elif state["status"] == "retrying":
        state = transition_run(repo_root, run_id, "running", reason="retry_iteration_started")
    elif state["status"] != "running":
        raise ValueError(f"cannot_begin_iteration_from:{state['status']}")

    state = load_run_state(repo_root, run_id)
    state["iteration"] = int(state["iteration"]) + 1
    state["updated_at"] = _iso(_utcnow())
    if idempotency_key:
        state.setdefault("idempotency_keys", []).append(idempotency_key)
    state.setdefault("events", []).append(
        {
            "seq": len(state.get("events", [])) + 1,
            "ts": state["updated_at"],
            "from": "running",
            "to": "running",
            "reason": "iteration_incremented",
            "idempotency_key": idempotency_key,
            "evidence": {"iteration": state["iteration"]},
        }
    )
    _atomic_write(_run_path(repo_root, run_id), state)
    return state


def request_cancel(repo_root: Path, run_id: str) -> dict[str, Any]:
    state = load_run_state(repo_root, run_id)
    if state.get("cancel_requested"):
        return state | {"idempotent_replay": True}
    state["cancel_requested"] = True
    state["updated_at"] = _iso(_utcnow())
    _atomic_write(_run_path(repo_root, run_id), state)
    return state


def enforce_runtime_conditions(repo_root: Path, run_id: str, *, now: datetime | None = None) -> dict[str, Any]:
    state = load_run_state(repo_root, run_id)
    if state["status"] in TERMINAL:
        return state
    if state.get("cancel_requested"):
        return transition_run(repo_root, run_id, "cancelled", reason="cancel_requested")

    deadline = state.get("deadline_at")
    current = now or _utcnow()
    if deadline and current >= datetime.fromisoformat(deadline):
        return transition_run(repo_root, run_id, "timed_out", reason="deadline_exceeded")
    return state
