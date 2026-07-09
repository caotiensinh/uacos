from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json

from uacos.config import uacos_dir
from uacos.security.patch_review import review_patch_file
from uacos.transaction.engine import run_transaction


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def lifecycle_dir(repo_root: Path) -> Path:
    path = uacos_dir(repo_root) / "patch_lifecycle"
    path.mkdir(parents=True, exist_ok=True)
    return path


def latest_lifecycle_report_path(repo_root: Path) -> Path:
    return lifecycle_dir(repo_root) / "latest_patch_lifecycle_report.json"


def write_lifecycle_report(repo_root: Path, report: dict) -> dict:
    path = latest_lifecycle_report_path(repo_root)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report["report_file"] = str(path)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def safe_apply_patch_file(
    repo_root: Path,
    patch_path: Path,
    *,
    title: str = "Safe patch apply",
    objective: str = "Apply patch through UACOS guarded lifecycle",
    allowed_files: list[str] | None = None,
    allowed_dirs: list[str] | None = None,
    tests: list[str] | None = None,
    yes: bool = False,
    allow_high_risk: bool = False,
) -> dict:
    """Review, checkpoint, apply, test, rollback/report through the existing transaction engine.

    This wrapper does not implement a new patch application mechanism. It gates the
    existing run_transaction() path with risk review, explicit confirmation, and
    required tests, then writes a last-run lifecycle report.
    """

    allowed_files = allowed_files or []
    allowed_dirs = allowed_dirs or []
    tests = tests or []
    patch_path = Path(patch_path).resolve()

    review = review_patch_file(patch_path, allowed_files=allowed_files, allowed_dirs=allowed_dirs, tests=tests)
    blocked_reasons: list[str] = []
    if not yes:
        blocked_reasons.append("explicit_yes_required")
    if not tests:
        blocked_reasons.append("tests_required")
    if review.get("status") == "fail" or review.get("risk_level") == "block":
        blocked_reasons.append("patch_review_blocked")
    if review.get("risk_level") == "high" and not allow_high_risk:
        blocked_reasons.append("high_risk_requires_allow_high_risk")

    if blocked_reasons:
        return write_lifecycle_report(repo_root, {
            "status": "blocked",
            "created_at": utcnow(),
            "mode": "apply_safe",
            "repo": str(repo_root),
            "patch": str(patch_path),
            "title": title,
            "objective": objective,
            "writes_code": False,
            "blocked_reasons": blocked_reasons,
            "review": review,
            "transaction": None,
            "next_step": "fix blocked_reasons, provide tests, and pass --yes before applying through the guarded transaction path",
        })

    tx = run_transaction(
        repo_root,
        patch_path,
        title=title,
        objective=objective,
        allowed_files=allowed_files,
        allowed_dirs=allowed_dirs,
        tests=tests,
        dry_run=False,
        auto_rollback=True,
    )
    status = "pass" if tx.get("status") == "committed" else "fail"
    return write_lifecycle_report(repo_root, {
        "status": status,
        "created_at": utcnow(),
        "mode": "apply_safe",
        "repo": str(repo_root),
        "patch": str(patch_path),
        "title": title,
        "objective": objective,
        "writes_code": True,
        "blocked_reasons": [],
        "review": review,
        "transaction": tx,
        "next_step": "inspect transaction manifest and latest patch lifecycle report before claiming done",
    })


def latest_lifecycle_report(repo_root: Path) -> dict:
    path = latest_lifecycle_report_path(repo_root)
    if not path.exists():
        return {"status": "missing", "report_file": str(path)}
    return json.loads(path.read_text(encoding="utf-8"))
