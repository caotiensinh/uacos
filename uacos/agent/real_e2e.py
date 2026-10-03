from __future__ import annotations

from pathlib import Path
import json
import shutil
import time
import uuid

from uacos.agent.provider_profiles import create_provider_adapter, get_provider_profile
from uacos.agent.safe_execution import run_safe_agent_execution
from uacos.config import uacos_dir


def _evidence_dir(repo_root: Path) -> Path:
    path = uacos_dir(repo_root) / "real_agent_e2e"
    path.mkdir(parents=True, exist_ok=True)
    return path


def run_real_provider_e2e(
    repo_root: Path,
    provider: str,
    argv: list[str],
    task: str,
    *,
    allowed_files: list[str] | None = None,
    allowed_dirs: list[str] | None = None,
    tests: list[str] | None = None,
    max_iterations: int = 2,
    timeout_seconds: int = 120,
    policy_path: Path | None = None,
    approval_record: dict | None = None,
) -> dict:
    """Execute a real provider CLI through the normalized UACOS safe path.

    This function never treats provider absence as a pass. It records explicit
    evidence for availability, invocation, guarded execution, tests, and the
    final bounded outcome.
    """
    root = Path(repo_root).resolve()
    profile = get_provider_profile(provider)
    if not argv:
        raise ValueError("provider_argv_required")

    resolved = shutil.which(argv[0]) if not Path(argv[0]).is_absolute() else str(Path(argv[0]))
    run_id = f"REAL-E2E-{uuid.uuid4().hex[:12]}"
    started = time.time()

    evidence = {
        "version": 1,
        "run_id": run_id,
        "provider": provider,
        "display_name": profile.display_name,
        "argv": list(argv),
        "resolved_executable": resolved,
        "started_at_epoch": started,
        "status": "unavailable" if not resolved or not Path(resolved).exists() else "running",
        "execution": None,
    }

    output_path = _evidence_dir(root) / f"{run_id}.json"
    if evidence["status"] == "unavailable":
        evidence["reason"] = "provider_executable_unavailable"
        evidence["finished_at_epoch"] = time.time()
        output_path.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
        evidence["evidence_file"] = str(output_path)
        return evidence

    adapter = create_provider_adapter(provider, argv=argv, cwd=root)
    execution = run_safe_agent_execution(
        root,
        task,
        adapter,
        allowed_files=allowed_files or [],
        allowed_dirs=allowed_dirs or [],
        tests=tests or [],
        max_iterations=max_iterations,
        timeout_seconds=timeout_seconds,
        policy_path=policy_path,
        approval_record=approval_record,
    )
    evidence["execution"] = execution
    evidence["status"] = "passed" if execution.get("status") == "passed" else execution.get("status", "failed")
    evidence["reason"] = execution.get("reason")
    evidence["finished_at_epoch"] = time.time()
    evidence["elapsed_ms"] = max(0, int((evidence["finished_at_epoch"] - started) * 1000))
    output_path.write_text(json.dumps(evidence, indent=2, sort_keys=True, default=str), encoding="utf-8")
    evidence["evidence_file"] = str(output_path)
    return evidence


def run_real_provider_matrix(repo_root: Path, cases: list[dict]) -> dict:
    """Run explicit provider cases; missing providers stay unavailable, never PASS."""
    results = []
    for case in cases:
        results.append(
            run_real_provider_e2e(
                repo_root,
                case["provider"],
                list(case["argv"]),
                case["task"],
                allowed_files=list(case.get("allowed_files") or []),
                allowed_dirs=list(case.get("allowed_dirs") or []),
                tests=list(case.get("tests") or []),
                max_iterations=int(case.get("max_iterations", 2)),
                timeout_seconds=int(case.get("timeout_seconds", 120)),
                policy_path=Path(case["policy_path"]) if case.get("policy_path") else None,
                approval_record=case.get("approval_record"),
            )
        )

    counts = {
        "passed": sum(1 for row in results if row.get("status") == "passed"),
        "failed": sum(1 for row in results if row.get("status") == "failed"),
        "blocked": sum(1 for row in results if row.get("status") == "blocked"),
        "unavailable": sum(1 for row in results if row.get("status") == "unavailable"),
    }
    return {
        "status": "pass" if results and counts["passed"] == len(results) else "incomplete",
        "counts": counts,
        "results": results,
        "claim": "Only rows with status=passed represent executed provider E2E success; unavailable providers are never counted as pass.",
    }
