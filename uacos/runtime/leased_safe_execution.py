from __future__ import annotations

from pathlib import Path
from threading import Event, Thread
from typing import Any, Callable
import time

from uacos.agent.safe_execution import run_safe_agent_execution
from uacos.runtime.resource_lease import SQLiteResourceLeaseStore


SafeExecutionFn = Callable[..., dict[str, Any]]


def _resource_scope(
    allowed_files: list[str] | None,
    allowed_dirs: list[str] | None,
) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for kind, values in (("dir", allowed_dirs or []), ("file", allowed_files or [])):
        for raw in values:
            key = str(raw or "").strip()
            item = (kind, key)
            if key and item not in seen:
                rows.append(item)
                seen.add(item)
    return rows


def run_leased_safe_agent_execution(
    repo_root: Path,
    task: str,
    adapter: Any,
    *,
    owner_id: str,
    lease_ttl_seconds: float = 30.0,
    heartbeat_interval_seconds: float | None = None,
    lease_store: SQLiteResourceLeaseStore | None = None,
    safe_execution_fn: SafeExecutionFn = run_safe_agent_execution,
    allowed_files: list[str] | None = None,
    allowed_dirs: list[str] | None = None,
    **safe_execution_kwargs: Any,
) -> dict[str, Any]:
    """Acquire scope leases before safe execution and keep them alive while it runs.

    This wrapper does not alter patch/policy/evidence semantics. If every requested
    resource lease cannot be acquired, safe execution is never invoked. Leases are
    released in ``finally`` and heartbeat failure is surfaced in the returned lease
    report so callers cannot silently treat a lost lease as healthy coordination.
    """
    root = Path(repo_root).resolve()
    owner = str(owner_id or "").strip()
    if not owner:
        raise ValueError("owner_id_required")
    ttl = float(lease_ttl_seconds)
    if ttl <= 0:
        raise ValueError("lease_ttl_seconds_must_be_positive")
    interval = float(heartbeat_interval_seconds) if heartbeat_interval_seconds is not None else max(0.1, ttl / 3.0)
    if interval <= 0 or interval >= ttl:
        raise ValueError("heartbeat_interval_must_be_positive_and_less_than_ttl")

    scope = _resource_scope(allowed_files, allowed_dirs)
    if not scope:
        return {
            "status": "blocked",
            "reason": "resource_lease_scope_required",
            "lease_report": {"status": "blocked", "acquired": [], "conflict": None},
        }

    store = lease_store or SQLiteResourceLeaseStore(root)
    acquired: list[dict[str, Any]] = []
    for resource_type, resource_key in scope:
        decision = store.acquire(
            resource_type=resource_type,
            resource_key=resource_key,
            owner_id=owner,
            ttl_seconds=ttl,
            metadata={"purpose": "safe_mutation"},
        )
        if decision.get("status") != "ok":
            for lease in reversed(acquired):
                store.release(
                    resource_type=lease["resource_type"],
                    resource_key=lease["resource_key"],
                    owner_id=owner,
                    lease_token=lease["lease_token"],
                )
            return {
                "status": "blocked",
                "reason": "resource_lease_conflict",
                "lease_report": {
                    "status": "blocked",
                    "acquired": list(acquired),
                    "conflict": decision,
                },
            }
        acquired.append(dict(decision["lease"]))

    stop = Event()
    heartbeat_failures: list[dict[str, Any]] = []

    def heartbeat_loop() -> None:
        while not stop.wait(interval):
            for lease in acquired:
                result = store.heartbeat(
                    resource_type=lease["resource_type"],
                    resource_key=lease["resource_key"],
                    owner_id=owner,
                    lease_token=lease["lease_token"],
                    ttl_seconds=ttl,
                )
                if result.get("status") != "ok":
                    heartbeat_failures.append(
                        {
                            "resource_type": lease["resource_type"],
                            "resource_key": lease["resource_key"],
                            "result": result,
                        }
                    )
                    stop.set()
                    return

    heartbeat_thread = Thread(target=heartbeat_loop, name="uacos-resource-lease-heartbeat", daemon=True)
    heartbeat_thread.start()
    release_results: list[dict[str, Any]] = []
    try:
        result = safe_execution_fn(
            root,
            task,
            adapter,
            allowed_files=list(allowed_files or []),
            allowed_dirs=list(allowed_dirs or []),
            **safe_execution_kwargs,
        )
        result = dict(result)
        if heartbeat_failures:
            result["status"] = "blocked"
            result["reason"] = "resource_lease_lost_during_execution"
        return result
    finally:
        stop.set()
        heartbeat_thread.join(timeout=max(1.0, interval * 2.0))
        for lease in reversed(acquired):
            release_results.append(
                store.release(
                    resource_type=lease["resource_type"],
                    resource_key=lease["resource_key"],
                    owner_id=owner,
                    lease_token=lease["lease_token"],
                )
            )
