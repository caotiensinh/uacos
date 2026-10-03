from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json

from uacos.config import uacos_dir


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_json(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8")), _sha256_bytes(raw)


def build_run_replay(repo_root: Path, run_id: str) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    state_path = uacos_dir(repo_root) / "run_state" / f"{run_id}.json"
    evidence_path = uacos_dir(repo_root) / "agent_runs" / f"{run_id}.json"

    if not state_path.exists():
        raise FileNotFoundError(f"run_state_missing:{run_id}")

    state, state_sha256 = _load_json(state_path)
    if state.get("run_id") != run_id:
        raise ValueError("run_state_id_mismatch")

    evidence = None
    evidence_sha256 = None
    if evidence_path.exists():
        evidence, evidence_sha256 = _load_json(evidence_path)
        if evidence.get("run_id") != run_id:
            raise ValueError("agent_evidence_id_mismatch")

    events = list(state.get("events") or [])
    attempts = list((evidence or {}).get("attempts") or [])
    timeline: list[dict[str, Any]] = []
    for event in events:
        timeline.append({
            "kind": "state_event",
            "seq": int(event.get("seq") or 0),
            "iteration": (event.get("evidence") or {}).get("iteration"),
            "status": event.get("to"),
            "reason": event.get("reason"),
            "ts": event.get("ts"),
        })
    for attempt in attempts:
        timeline.append({
            "kind": "agent_attempt",
            "seq": None,
            "iteration": attempt.get("iteration"),
            "status": attempt.get("status"),
            "reason": attempt.get("failure_class"),
            "ts": None,
        })

    replay = {
        "run_id": run_id,
        "task": state.get("task"),
        "durable_status": state.get("status"),
        "iteration": state.get("iteration"),
        "max_iterations": state.get("max_iterations"),
        "state": state,
        "agent_evidence": evidence,
        "timeline": timeline,
        "source_hashes": {
            "run_state_sha256": state_sha256,
            "agent_evidence_sha256": evidence_sha256,
        },
    }
    replay["verification"] = verify_run_replay(replay)
    return replay


def verify_run_replay(replay: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    state = replay.get("state") or {}
    evidence = replay.get("agent_evidence") or {}
    run_id = replay.get("run_id")

    events = list(state.get("events") or [])
    expected_seq = list(range(1, len(events) + 1))
    actual_seq = [int(event.get("seq") or 0) for event in events]
    if actual_seq != expected_seq:
        findings.append({"reason": "non_contiguous_event_sequence", "actual": actual_seq})

    event_iterations = [
        int((event.get("evidence") or {}).get("iteration"))
        for event in events
        if (event.get("evidence") or {}).get("iteration") is not None
    ]
    if any(right < left for left, right in zip(event_iterations, event_iterations[1:])):
        findings.append({"reason": "non_monotonic_iteration_evidence", "iterations": event_iterations})

    if evidence:
        if evidence.get("run_id") != run_id:
            findings.append({"reason": "agent_evidence_id_mismatch"})
        if evidence.get("task") not in {None, state.get("task")}:
            findings.append({"reason": "task_mismatch"})
        evidence_status = evidence.get("status")
        durable_status = state.get("status")
        if evidence_status and durable_status and evidence_status != durable_status:
            findings.append({
                "reason": "terminal_status_mismatch",
                "agent_status": evidence_status,
                "durable_status": durable_status,
            })

    return {
        "status": "pass" if not findings else "fail",
        "findings": findings,
        "event_count": len(events),
        "attempt_count": len((evidence or {}).get("attempts") or []),
    }


def write_run_replay(repo_root: Path, run_id: str) -> str:
    replay = build_run_replay(repo_root, run_id)
    out_dir = uacos_dir(repo_root.resolve()) / "replay"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{run_id}.json"
    path.write_text(json.dumps(replay, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)
