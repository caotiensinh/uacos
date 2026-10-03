from __future__ import annotations

from pathlib import Path
from typing import Any, Callable
import json
import time

from uacos.agent.protocol import AgentRunRequest, AgentRunResult, normalize_agent_result
from uacos.config import uacos_dir
from uacos.graph.builder import build_graph
from uacos.impact.analyzer import smart_context
from uacos.patching.engine import validate_patch


def _extract_diff(text: str) -> str | None:
    if not text:
        return None
    marker = "diff --git "
    start = text.find(marker)
    if start < 0:
        return None
    body = text[start:]
    fence = body.find("```")
    if fence >= 0:
        body = body[:fence]
    return body.strip() + "\n"


def _runs_dir(repo_root: Path) -> Path:
    path = uacos_dir(repo_root) / "agent_runs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_evidence(repo_root: Path, report: dict) -> str:
    path = _runs_dir(repo_root) / f"{report['run_id']}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def _adapter_capabilities(adapter: Any) -> dict:
    caps = getattr(adapter, "capabilities", None)
    if caps is None:
        return {}
    if hasattr(caps, "__dataclass_fields__"):
        from dataclasses import asdict
        return asdict(caps)
    return dict(caps)


def run_agent_harness(
    repo_root: Path,
    task: str,
    adapter: Any,
    *,
    allowed_files: list[str] | None = None,
    allowed_dirs: list[str] | None = None,
    tests: list[str] | None = None,
    max_iterations: int = 3,
    timeout_seconds: int = 120,
    max_files: int = 8,
    max_context_chars: int = 18000,
    cancel_check: Callable[[], bool] | None = None,
) -> dict:
    """Run a bounded external-agent loop through one normalized contract.

    Phase WS3-A is intentionally validate-only: agent patches are never applied here.
    Transactional apply/tests are a separate runtime gate so adapters cannot bypass safety.
    """
    if max_iterations < 1:
        raise ValueError("max_iterations_must_be_positive")

    repo_root = repo_root.resolve()
    allowed_files = list(allowed_files or [])
    allowed_dirs = list(allowed_dirs or [])
    tests = list(tests or [])

    build_graph(repo_root)
    context = smart_context(repo_root, task, max_files=max_files, max_chars=max_context_chars)
    attempts: list[dict] = []
    run_id: str | None = None
    final_status = "failed"
    final_reason = "max_iterations_exhausted"

    for iteration in range(1, max_iterations + 1):
        if cancel_check and cancel_check():
            final_status = "cancelled"
            final_reason = "cancel_requested"
            break

        request = AgentRunRequest(
            task=task,
            context=context["content"],
            allowed_files=allowed_files,
            allowed_dirs=allowed_dirs,
            tests=tests,
            run_id=run_id or AgentRunRequest(task=task, context="").run_id,
            iteration=iteration,
            timeout_seconds=timeout_seconds,
            metadata={
                "context_model": context.get("context_model"),
                "included_files": context.get("included_files", []),
                "included_symbol_ids": [
                    row.get("symbol_id")
                    for row in context.get("included_context", [])
                    if row.get("symbol_id")
                ],
            },
        )
        run_id = request.run_id

        started = time.monotonic()
        try:
            raw = adapter.run(request)
            result = normalize_agent_result(adapter, raw, started)
        except TimeoutError as exc:
            result = AgentRunResult(
                adapter_name=str(getattr(adapter, "name", type(adapter).__name__)),
                adapter_version=getattr(adapter, "version", None),
                status="timeout",
                elapsed_ms=max(0, int((time.monotonic() - started) * 1000)),
                failure_class="adapter_timeout",
                evidence={"error": str(exc)},
            )
        except Exception as exc:
            result = AgentRunResult(
                adapter_name=str(getattr(adapter, "name", type(adapter).__name__)),
                adapter_version=getattr(adapter, "version", None),
                status="error",
                elapsed_ms=max(0, int((time.monotonic() - started) * 1000)),
                failure_class="adapter_error",
                evidence={"error": f"{type(exc).__name__}:{exc}"},
            )

        patch = result.patch or _extract_diff(result.output)
        validation = None
        attempt_status = result.status
        failure_class = result.failure_class

        if patch:
            validation = validate_patch(
                repo_root,
                patch,
                allowed_files=allowed_files,
                allowed_dirs=allowed_dirs,
            )
            if validation["status"] == "pass":
                attempt_status = "passed"
                failure_class = None
                final_status = "passed"
                final_reason = "patch_validated"
            else:
                attempt_status = "failed"
                failure_class = "patch_validation_failed"
                final_reason = "patch_validation_failed"
        elif result.status in {"timeout", "cancelled", "blocked", "error"}:
            final_reason = result.failure_class or result.status
        else:
            attempt_status = "failed"
            failure_class = "no_patch"
            final_reason = "no_patch"

        attempts.append(
            {
                "iteration": iteration,
                "status": attempt_status,
                "adapter_result": result.to_dict(),
                "patch_present": bool(patch),
                "patch_validation": validation,
                "failure_class": failure_class,
            }
        )
        if final_status == "passed":
            break
        if result.status in {"cancelled", "blocked"}:
            final_status = result.status
            break

    assert run_id is not None
    totals = {
        "attempt_count": len(attempts),
        "retry_count": max(0, len(attempts) - 1),
        "elapsed_ms": sum(int(a["adapter_result"].get("elapsed_ms") or 0) for a in attempts),
        "tokens_in": sum(int(a["adapter_result"].get("tokens_in") or 0) for a in attempts),
        "tokens_out": sum(int(a["adapter_result"].get("tokens_out") or 0) for a in attempts),
        "tool_calls": sum(int(a["adapter_result"].get("tool_calls") or 0) for a in attempts),
    }
    report = {
        "status": final_status,
        "reason": final_reason,
        "run_id": run_id,
        "task": task,
        "adapter": {
            "name": str(getattr(adapter, "name", type(adapter).__name__)),
            "version": getattr(adapter, "version", None),
            "capabilities": _adapter_capabilities(adapter),
        },
        "policy": {
            "validate_only": True,
            "max_iterations": max_iterations,
            "timeout_seconds": timeout_seconds,
            "allowed_files": allowed_files,
            "allowed_dirs": allowed_dirs,
            "tests": tests,
        },
        "context": {
            "model": context.get("context_model"),
            "char_count": context.get("char_count"),
            "included_files": context.get("included_files", []),
            "included_symbol_ids": sorted({
                row.get("symbol_id")
                for row in context.get("included_context", [])
                if row.get("symbol_id")
            }),
            "budget_utilization": context.get("budget_utilization"),
        },
        "attempts": attempts,
        "metrics": totals | {
            "first_pass_success": bool(attempts and attempts[0]["status"] == "passed"),
            "patch_valid": final_status == "passed",
        },
    }
    report["evidence_file"] = _write_evidence(repo_root, report)
    return report
