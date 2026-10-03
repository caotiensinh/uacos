from __future__ import annotations

from pathlib import Path
from typing import Any

from uacos.agent.harness import run_agent_harness
from uacos.runtime.run_state import (
    TERMINAL,
    begin_iteration,
    create_run_state,
    enforce_runtime_conditions,
    load_run_state,
    transition_run,
)


def _last_reason(state: dict) -> str:
    events = state.get("events") or []
    if not events:
        return str(state.get("status") or "runtime_stopped")
    return str(events[-1].get("reason") or state.get("status") or "runtime_stopped")


def run_reliable_agent_harness(
    repo_root: Path,
    task: str,
    adapter: Any,
    *,
    allowed_files: list[str] | None = None,
    allowed_dirs: list[str] | None = None,
    tests: list[str] | None = None,
    max_iterations: int = 3,
    timeout_seconds: int = 120,
    deadline_seconds: int | None = None,
    max_files: int = 8,
    max_context_chars: int = 18000,
    run_id: str | None = None,
) -> dict:
    """Run the normalized agent harness while durably persisting lifecycle state."""
    repo_root = repo_root.resolve()
    created = create_run_state(
        repo_root,
        task,
        max_iterations=max_iterations,
        deadline_seconds=deadline_seconds,
        run_id=run_id,
        metadata={
            "adapter": str(getattr(adapter, "name", type(adapter).__name__)),
            "timeout_seconds": timeout_seconds,
        },
    )
    durable_run_id = str(created["run_id"])

    def cancelled() -> bool:
        return bool(load_run_state(repo_root, durable_run_id).get("cancel_requested"))

    def pre_iteration(iteration: int):
        state = enforce_runtime_conditions(repo_root, durable_run_id)
        if state["status"] in TERMINAL:
            return str(state["status"]), _last_reason(state)
        begin_iteration(
            repo_root,
            durable_run_id,
            idempotency_key=f"iteration:{iteration}:begin",
        )
        return None

    def record_attempt(attempt: dict) -> None:
        state = load_run_state(repo_root, durable_run_id)
        if state["status"] in TERMINAL:
            return

        iteration = int(attempt["iteration"])
        adapter_status = str(attempt.get("adapter_result", {}).get("status") or "")
        failure_class = str(attempt.get("failure_class") or "attempt_failed")
        evidence = {
            "iteration": iteration,
            "attempt_status": attempt.get("status"),
            "adapter_status": adapter_status,
            "failure_class": attempt.get("failure_class"),
            "patch_present": bool(attempt.get("patch_present")),
        }

        if attempt.get("status") == "passed":
            transition_run(
                repo_root,
                durable_run_id,
                "validating",
                reason="patch_received",
                evidence=evidence,
                idempotency_key=f"iteration:{iteration}:validating",
            )
            transition_run(
                repo_root,
                durable_run_id,
                "passed",
                reason="patch_validated",
                evidence=evidence,
                idempotency_key=f"iteration:{iteration}:passed",
            )
            return

        if adapter_status == "timeout":
            transition_run(
                repo_root,
                durable_run_id,
                "timed_out",
                reason=attempt.get("failure_class") or "adapter_timeout",
                evidence=evidence,
                idempotency_key=f"iteration:{iteration}:timed_out",
            )
            return
        if adapter_status == "cancelled":
            transition_run(
                repo_root,
                durable_run_id,
                "cancelled",
                reason=attempt.get("failure_class") or "adapter_cancelled",
                evidence=evidence,
                idempotency_key=f"iteration:{iteration}:cancelled",
            )
            return
        if adapter_status == "blocked":
            transition_run(
                repo_root,
                durable_run_id,
                "blocked",
                reason=attempt.get("failure_class") or "adapter_blocked",
                evidence=evidence,
                idempotency_key=f"iteration:{iteration}:blocked",
            )
            return

        if iteration >= max_iterations:
            transition_run(
                repo_root,
                durable_run_id,
                "failed",
                reason=failure_class,
                evidence=evidence,
                idempotency_key=f"iteration:{iteration}:failed",
            )
        else:
            transition_run(
                repo_root,
                durable_run_id,
                "retrying",
                reason=failure_class,
                evidence=evidence,
                idempotency_key=f"iteration:{iteration}:retrying",
            )

    report = run_agent_harness(
        repo_root,
        task,
        adapter,
        allowed_files=allowed_files,
        allowed_dirs=allowed_dirs,
        tests=tests,
        max_iterations=max_iterations,
        timeout_seconds=timeout_seconds,
        max_files=max_files,
        max_context_chars=max_context_chars,
        cancel_check=cancelled,
        run_id=durable_run_id,
        pre_iteration_check=pre_iteration,
        attempt_hook=record_attempt,
    )

    state = load_run_state(repo_root, durable_run_id)
    if state["status"] not in TERMINAL:
        target = report["status"] if report["status"] in TERMINAL else "failed"
        transition_run(
            repo_root,
            durable_run_id,
            target,
            reason=report.get("reason") or "harness_finished",
            evidence={"attempt_count": report.get("metrics", {}).get("attempt_count", 0)},
            idempotency_key="harness:terminal",
        )
        state = load_run_state(repo_root, durable_run_id)

    report["durable_state"] = state
    report["durable_status"] = state["status"]
    return report
