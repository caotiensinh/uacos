from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib

from uacos.agent.harness import run_agent_harness
from uacos.execution.test_runner import run_allowed_command
from uacos.patching.engine import apply_patch, rollback_patch
from uacos.patching.preconditions import capture_patch_preconditions, verify_patch_preconditions
from uacos.config import uacos_dir
from uacos.security.approval import verify_approval_record
from uacos.security.patch_review import review_patch_text
from uacos.security.policy import evaluate_patch_policy, load_policy


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


def _rollback_after_test_failure(repo_root: Path, applied: dict, preconditions: dict) -> dict:
    engine_result = rollback_patch(repo_root, applied)
    verification = verify_patch_preconditions(repo_root, preconditions)
    engine_ok = engine_result.get("status") == "ok"
    verification_ok = verification.get("status") == "pass"
    return {
        "status": "rolled_back" if engine_ok and verification_ok else "rollback_failed",
        "rolled_back": int(engine_result.get("rolled_back", 0)),
        "engine_result": engine_result,
        "verification": verification,
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
    policy_path: Path | None = None,
    approval_record: dict | None = None,
) -> dict:
    """Run agent -> policy/approval -> stale-check -> apply -> tests -> verified rollback."""
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
        "patch_review": None,
        "policy_decision": None,
        "approval_verification": None,
        "preconditions": None,
        "precondition_verification": None,
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

    # Policy is optional for backward compatibility. When configured it is
    # enforced before any precondition capture or filesystem mutation.
    if policy_path is not None:
        review = review_patch_text(
            patch_text,
            allowed_files=allowed_files,
            allowed_dirs=allowed_dirs,
            tests=tests,
            repo_root=repo_root,
        )
        result["patch_review"] = review
        try:
            policy = load_policy(Path(policy_path))
            decision = evaluate_patch_policy(review, policy)
        except Exception as exc:
            result["status"] = "blocked"
            result["reason"] = "policy_load_failed"
            result["policy_decision"] = {"action": "deny", "error": f"{type(exc).__name__}: {exc}"}
            return result
        result["policy_decision"] = decision

        if decision["action"] == "deny":
            result["status"] = "blocked"
            result["reason"] = "policy_denied"
            return result
        if decision["action"] == "approval_required":
            approval_verification = verify_approval_record(approval_record, patch_text, decision)
            result["approval_verification"] = approval_verification
            if approval_verification.get("status") != "pass":
                result["status"] = "blocked"
                result["reason"] = "human_approval_required" if approval_record is None else "invalid_human_approval"
                return result

    preconditions = capture_patch_preconditions(repo_root, patch_text)
    result["preconditions"] = preconditions
    if preconditions.get("status") != "pass":
        result["status"] = "failed"
        result["reason"] = "patch_precondition_capture_failed"
        return result

    precondition_verification = verify_patch_preconditions(repo_root, preconditions)
    result["precondition_verification"] = precondition_verification
    if precondition_verification.get("status") != "pass":
        result["status"] = "failed"
        result["reason"] = "stale_patch_precondition_failed"
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

    rollback = _rollback_after_test_failure(repo_root, applied, preconditions)
    result["rollback"] = rollback
    result["status"] = "failed"
    statuses = [row.get("status") for row in test_report["results"]]
    if rollback["status"] != "rolled_back":
        if rollback.get("engine_result", {}).get("status") == "ok" and rollback.get("verification", {}).get("status") != "pass":
            result["reason"] = "rollback_verification_failed"
        else:
            result["reason"] = "rollback_failed"
    elif "blocked" in statuses:
        result["reason"] = "test_command_blocked"
    elif "timeout" in statuses:
        result["reason"] = "tests_timed_out"
    else:
        result["reason"] = "tests_failed"
    return result
