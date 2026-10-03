from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib

from uacos.agent.harness import run_agent_harness
from uacos.execution.test_runner import run_allowed_command
from uacos.patching.engine import apply_patch, rollback_patch
from uacos.config import uacos_dir


def _extract_diff(text: str) -> str | None:
    if not text:
        return None
    start = text.find("diff --git ")
    if start < 0:
        return None
    body = text[start:]
    fence = body.find("```")
    if fence >= 0:
        body = body[:fence]
    body = body.strip()
    return body + "\n" if body else None


def _patch_file(repo_root: Path, run_id: str, patch_text: str) -> Path:
    root = uacos_dir(repo_root) / "agent_runs" / run_id
    root.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(patch_text.encode("utf-8")).hexdigest()[:16]
    path = root / f"patch-{digest}.diff"
    path.write_text(patch_text, encoding="utf-8")
    return path


def _run_policy_tests(repo_root: Path, tests: list[str], timeout_seconds: int) -> dict:
    rows = []
    for command in tests:
        row = run_allowed_command(repo_root, command, timeout=timeout_seconds)
        rows.append(row)
        if row["status"] != "pass":
            break
    return {
        "status": "pass" if all(row["status"] == "pass" for row in rows) else "fail",
        "results": rows,
    }


def run_safe_agent_execution(
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
) -> dict:
    """Run agent -> validate -> apply -> policy-aware tests -> rollback/commit.

    This execution gate deliberately calls ``apply_patch(..., tests=[])`` and runs
    every requested command through ``run_allowed_command`` afterwards. That keeps
    task-supplied test commands behind UACOS command policy instead of the legacy
    transaction helpers that execute shell commands directly.
    """
    repo_root = repo_root.resolve()
    allowed_files = list(allowed_files or [])
    allowed_dirs = list(allowed_dirs or [])
    tests = list(tests or [])

    harness = run_agent_harness(
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
    )
    result = {
        "status": harness["status"],
        "reason": harness["reason"],
        "run_id": harness["run_id"],
        "harness": harness,
        "patch_apply": None,
        "tests": None,
        "rollback": None,
    }
    if harness["status"] != "passed":
        return result

    winning = next((row for row in reversed(harness["attempts"]) if row["status"] == "passed"), None)
    if not winning:
        result["status"] = "failed"
        result["reason"] = "validated_attempt_missing"
        return result

    output = winning["adapter_result"].get("output") or ""
    patch_text = winning["adapter_result"].get("patch") or _extract_diff(output)
    if not patch_text:
        result["status"] = "failed"
        result["reason"] = "validated_patch_missing"
        return result

    patch_path = _patch_file(repo_root, harness["run_id"], patch_text)
    applied = apply_patch(
        repo_root,
        patch_path,
        allowed_files=allowed_files,
        allowed_dirs=allowed_dirs,
        tests=[],
        dry_run=False,
    )
    result["patch_apply"] = applied
    result["patch_file"] = str(patch_path)
    if applied.get("status") != "applied":
        result["status"] = "failed"
        result["reason"] = "patch_apply_failed"
        return result

    test_report = _run_policy_tests(repo_root, tests, timeout_seconds)
    result["tests"] = test_report
    if test_report["status"] == "pass":
        result["status"] = "passed"
        result["reason"] = "patch_applied_tests_passed"
        return result

    rollback = rollback_patch(repo_root, applied)
    result["rollback"] = rollback
    result["status"] = "failed"
    statuses = [row.get("status") for row in test_report["results"]]
    if "blocked" in statuses:
        result["reason"] = "test_command_blocked"
    elif "timeout" in statuses:
        result["reason"] = "tests_timed_out"
    else:
        result["reason"] = "tests_failed"
    return result
