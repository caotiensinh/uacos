from __future__ import annotations

from pathlib import Path, PurePosixPath
from threading import Event, Thread
from typing import Any, Callable

from uacos.agent.safe_execution import run_safe_agent_execution
from uacos.runtime.resource_lease import SQLiteResourceLeaseStore


SafeExecutionFn = Callable[..., dict[str, Any]]


def _normalized_path(value: str) -> str:
    return PurePosixPath(str(value).replace("\\", "/")).as_posix()


def _inside(path: str, directory: str) -> bool:
    p = PurePosixPath(path)
    d = PurePosixPath(directory)
    return p == d or d in p.parents


def _resource_scope(
    allowed_files: list[str] | None,
    allowed_dirs: list[str] | None,
) -> list[tuple[str, str]]:
    dirs = sorted({_normalized_path(v) for v in (allowed_dirs or []) if str(v or "").strip()}, key=lambda v: (len(PurePosixPath(v).parts), v))
    kept_dirs: list[str] = []
    for directory in dirs:
        if not any(_inside(directory, parent) for parent in kept_dirs):
            kept_dirs.append(directory)

    files = sorted({_normalized_path(v) for v in (allowed_files or []) if str(v or "").strip()})
    kept_files = [path for path in files if not any(_inside(path, directory) for directory in kept_dirs)]
    return [("dir", path) for path in kept_dirs] + [("file", path) for path in kept_files]


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
    """Acquire/fence mutation scope around the existing safe execution path.

    All leases must be acquired before execution. A background heartbeat keeps them
    alive, while an opt-in mutation guard re-validates every fencing token inside
    `run_safe_agent_execution` immediately before preconditions and `apply_patch`.
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
            releases = []
            for lease in reversed(acquired):
                releases.append(
                    store.release(
                        resource_type=lease["resource_type"],
                        resource_key=lease["resource_key"],
                        owner_id=owner,
                        lease_token=lease["lease_token"],
                    )
                )
            return {
                "status": "blocked",
                "reason": "resource_lease_conflict",
                "lease_report": {
                    "status": "blocked",
                    "scope": scope,
                    "acquired": list(acquired),
                    "conflict": decision,
                    "release_results": releases,
                },
            }
        acquired.append(dict(decision["lease"]))

    stop = Event()
    heartbeat_failures: list[dict[str, Any]] = []

    def refresh(lease: dict[str, Any]) -> dict[str, Any]:
        return store.heartbeat(
            resource_type=lease["resource_type"],
            resource_key=lease["resource_key"],
            owner_id=owner,
            lease_token=lease["lease_token"],
            ttl_seconds=ttl,
        )

    def mutation_guard() -> dict[str, Any]:
        if heartbeat_failures:
            return {"status": "fail", "reason": "lease_heartbeat_failed", "failures": list(heartbeat_failures)}
        checks = []
        for lease in acquired:
            check = refresh(lease)
            checks.append(check)
            if check.get("status") != "ok":
                return {
                    "status": "fail",
                    "reason": "lease_fencing_check_failed",
                    "resource_type": lease["resource_type"],
                    "resource_key": lease["resource_key"],
                    "check": check,
                }
        return {"status": "pass", "reason": "all_resource_leases_owned", "checks": checks}

    def heartbeat_loop() -> None:
        while not stop.wait(interval):
            for lease in acquired:
                check = refresh(lease)
                if check.get("status") != "ok":
                    heartbeat_failures.append(
                        {
                            "resource_type": lease["resource_type"],
                            "resource_key": lease["resource_key"],
                            "result": check,
                        }
                    )
                    stop.set()
                    return

    heartbeat_thread = Thread(target=heartbeat_loop, name="uacos-resource-lease-heartbeat", daemon=True)
    heartbeat_thread.start()
    execution_result: dict[str, Any] | None = None
    release_results: list[dict[str, Any]] = []
    execution_error: BaseException | None = None
    try:
        execution_result = dict(
            safe_execution_fn(
                root,
                task,
                adapter,
                allowed_files=list(allowed_files or []),
                allowed_dirs=list(allowed_dirs or []),
                mutation_guard=mutation_guard,
                **safe_execution_kwargs,
            )
        )
    except BaseException as exc:
        execution_error = exc
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

    if execution_error is not None:
        raise execution_error
    assert execution_result is not None
    execution_result["lease_report"] = {
        "status": "fail" if heartbeat_failures else "pass",
        "scope": scope,
        "acquired": acquired,
        "heartbeat_failures": heartbeat_failures,
        "release_results": release_results,
    }
    if heartbeat_failures:
        execution_result["status"] = "failed"
        execution_result["reason"] = "resource_lease_lost_during_execution"
    return execution_result
