from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib
import json
import os
import uuid

from uacos.config import uacos_dir

GENESIS_HASH = "0" * 64


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(value: bytes | str) -> str:
    raw = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(raw).hexdigest()


def evidence_ledger_path(repo_root: Path) -> Path:
    path = uacos_dir(repo_root) / "evidence" / "ledger.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _read_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"evidence_ledger_invalid_json:{lineno}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"evidence_ledger_non_object:{lineno}")
        rows.append(row)
    return rows


def read_evidence_ledger(repo_root: Path) -> list[dict[str, Any]]:
    return _read_rows(evidence_ledger_path(repo_root))


def append_evidence_event(
    repo_root: Path,
    *,
    event_type: str,
    source: str,
    status: str,
    task_id: str | None = None,
    run_id: str | None = None,
    action_id: str | None = None,
    command: str | None = None,
    input_hash: str | None = None,
    output_hash: str | None = None,
    exit_code: int | None = None,
    workspace_before_hash: str | None = None,
    workspace_after_hash: str | None = None,
    diff_hash: str | None = None,
    token_usage: dict[str, Any] | None = None,
    evidence_refs: list[str] | None = None,
    parent_event_ids: list[str] | None = None,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Append one canonical, hash-chained evidence event.

    This ledger does not decide PASS/FAIL. It records host-observed facts so contract,
    claim, and verification layers can reference immutable event IDs later.
    """
    event_type = str(event_type or "").strip()
    source = str(source or "").strip()
    status = str(status or "").strip()
    if not event_type or not source or not status:
        raise ValueError("event_type_source_status_required")

    path = evidence_ledger_path(repo_root)
    existing = _read_rows(path)
    previous_hash = existing[-1].get("event_hash", GENESIS_HASH) if existing else GENESIS_HASH
    seq = len(existing) + 1
    event_id = "EV-" + uuid.uuid4().hex[:16]
    payload: dict[str, Any] = {
        "version": 1,
        "seq": seq,
        "event_id": event_id,
        "ts": _utcnow(),
        "event_type": event_type,
        "source": source,
        "status": status,
        "task_id": task_id,
        "run_id": run_id,
        "action_id": action_id,
        "command": command,
        "input_hash": input_hash,
        "output_hash": output_hash,
        "exit_code": exit_code,
        "workspace_before_hash": workspace_before_hash,
        "workspace_after_hash": workspace_after_hash,
        "diff_hash": diff_hash,
        "token_usage": dict(token_usage or {}),
        "evidence_refs": list(evidence_refs or []),
        "parent_event_ids": list(parent_event_ids or []),
        "data": dict(data or {}),
        "prev_hash": previous_hash,
    }
    payload_hash = _sha256(_canonical(payload))
    record = dict(payload)
    record["payload_hash"] = payload_hash
    record["event_hash"] = _sha256(f"{previous_hash}:{payload_hash}")

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
        f.flush()
        os.fsync(f.fileno())
    return record


def verify_evidence_ledger(repo_root: Path) -> dict[str, Any]:
    path = evidence_ledger_path(repo_root)
    try:
        rows = _read_rows(path)
    except ValueError as exc:
        return {"status": "fail", "reason": str(exc), "records": 0, "head_hash": None}

    previous = GENESIS_HASH
    for index, row in enumerate(rows, start=1):
        if row.get("seq") != index:
            return {"status": "fail", "reason": f"seq_mismatch:{index}", "records": len(rows), "head_hash": previous}
        if row.get("prev_hash") != previous:
            return {"status": "fail", "reason": f"prev_hash_mismatch:{index}", "records": len(rows), "head_hash": previous}
        unsigned = {k: v for k, v in row.items() if k not in {"payload_hash", "event_hash"}}
        expected_payload = _sha256(_canonical(unsigned))
        if row.get("payload_hash") != expected_payload:
            return {"status": "fail", "reason": f"payload_hash_mismatch:{index}", "records": len(rows), "head_hash": previous}
        expected_event = _sha256(f"{previous}:{expected_payload}")
        if row.get("event_hash") != expected_event:
            return {"status": "fail", "reason": f"event_hash_mismatch:{index}", "records": len(rows), "head_hash": previous}
        previous = expected_event

    return {
        "status": "pass",
        "reason": "hash_chain_valid",
        "records": len(rows),
        "head_hash": previous if rows else GENESIS_HASH,
        "path": str(path),
    }


def hash_text(value: str | bytes) -> str:
    return _sha256(value)
