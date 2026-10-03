from __future__ import annotations

from pathlib import Path
from typing import Any

from uacos.agent.harness import run_agent_harness
from uacos.runtime.retry_policy import decide_retry
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


def _prepare_resume(
    repo_root: Path,
    run_id: str,
    task: str,
    adapter_name: str,
    requested_max_iterations: int,
) -> tuple[dict, int, bool]:
    state = load_run_state(repo_root, run_id)
    if state.get("task") != task:
        raise ValueError("resume_task_mismatch")
    if state.get("status") in TERMINAL:
        raise ValueError(f"terminal_run_not_resumable:{state['status']}")

    persisted_max = int(state.get("max_iterations") or 0)
    if persisted_max != int(requested_max_iterations):
        raise ValueError("resume_max_iterations_mismatch")

    persisted_adapter = str((state.get("metadata") or {}).get("adapter") or "")
    if persisted_adapter and persisted_adapter != adapter_name:
        raise ValueError("resume_adapter_mismatch")

    iteration = int(state.get("iteration") or 0)
    if iteration >= persisted_max:
        state = transition_run(
            repo_root,
            run_id,
            "failed",
            reason="max_iterations_exhausted",
            idempotency_key="resume:max_iterations_exhausted",
        )
        return state, persisted_max + 1, True

    if state["status"] not in {"queued", "retrying"}:
        state = transition_run(
            repo_root,
            run_id,
            "retrying",
            reason="resume_interrupted_run",
            evidence={"interrupted_status": state["status"], "iteration": iteration},
            idempotency_key=f"resume:{iteration}:retrying",
        )

    start_iteration = 1 if int(state.get("iteration") or 0) == 0 else int(state["iteration"]) + 1
    return state, start_iteration, True


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
    """Run or resume the normalized agent harness with durable lifecycle state."""
    repo_root = repo_root.resolve()
    adapter_name = str(getattr(adapter, "name", type(adapter).__name__))
    created = create_run_state(
        repo_root,
        task,
        max_iterations=max_iterations,
        deadline_seconds=deadline_seconds,
        run_id=run_id,
        metadata={
            "adapter": adapter_name,
            "timeout_seconds": timeout_seconds,
        },
    )
    durable_run_id = str(created["run_id"])
    resumed = bool(created.get("idempotent_replay"))
    start_iteration = 1

    if resumed:
        state, start_iteration, _ = _prepare_resume(
            repo_root,
            durable_run_id,
            task,
            adapter_name,
            max_iterations,
        )
        if state["status"] in TERMINAL:
            return {
                "status": state["status"],
                "reason": _last_reason(state),
                "run_id": durable_run_id,
                "task": task,
                "attempts": [],
                "metrics": {"attempt_count": 0, "retry_count": 0, "resumed": True},
                "durable_state": state,
                "durable_status": state["status"],
            }

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

        decision = decide_retry(
            failure_class,
            iteration=iteration,
            max_iterations=max_iterations,
            no_progress_stalled=bool((attempt.get("no_progress") or {}).get("stalled") and iteration < max_iterations),
        )
        evidence["retry_decision"] = decision.to_dict()

        if decision.action == "retry":
            transition_run(
                repo_root,
                durable_run_id,
                "retrying",
                reason=decision.reason,
                evidence=evidence,
                idempotency_key=f"iteration:{iteration}:retrying",
            )
            return

        terminal_reason = decision.reason
        terminal_status = "timed_out" if adapter_status == "timeout" and decision.reason == "max_iterations_exhausted" else "failed"
        transition_run(
            repo_root,
            durable_run_id,
            terminal_status,
            reason=terminal_reason,
            evidence=evidence,
            idempotency_key=f"iteration:{iteration}:{terminal_status}",
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
        start_iteration=start_iteration,
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

    report["metrics"]["resumed"] = resumed
    report["policy"]["start_iteration"] = start_iteration
    report["durable_state"] = state
    report["durable_status"] = state["status"]
    return report
