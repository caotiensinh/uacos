from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib

from uacos.patching.engine import parse_unified_diff


def _safe_target(repo_root: Path, rel: str) -> Path:
    candidate = (repo_root / rel).resolve(strict=False)
    root = repo_root.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"unsafe_precondition_path:{rel}") from exc
    return candidate


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _expect_existing(repo_root: Path, rel: str) -> dict[str, Any]:
    path = _safe_target(repo_root, rel)
    if path.is_symlink():
        return {"path": rel, "expect": "regular_file", "invalid": "symlink"}
    if not path.exists():
        return {"path": rel, "expect": "regular_file", "invalid": "missing"}
    if not path.is_file():
        return {"path": rel, "expect": "regular_file", "invalid": "not_regular_file"}
    stat = path.stat()
    return {
        "path": rel,
        "expect": "sha256",
        "sha256": _sha256_file(path),
        "size": int(stat.st_size),
    }


def _expect_absent(repo_root: Path, rel: str) -> dict[str, Any]:
    path = _safe_target(repo_root, rel)
    return {"path": rel, "expect": "absent", "exists": path.exists() or path.is_symlink()}


def capture_patch_preconditions(repo_root: Path, patch_text: str) -> dict[str, Any]:
    """Capture filesystem assumptions that must still hold when a patch is applied.

    The snapshot is intentionally content-based rather than mtime-based. Existing
    modify/delete/rename sources are pinned by SHA-256, while new/rename targets are
    required to remain absent. This allows a caller to detect stale patches after an
    agent spent time reasoning against an older workspace state.
    """
    repo_root = repo_root.resolve()
    rows: dict[str, dict[str, Any]] = {}
    for item in parse_unified_diff(patch_text):
        op = item.get("operation")
        old_path = item.get("old_path")
        new_path = item.get("new_path")

        if op in {"modify", "delete", "rename", "rename_modify"} and old_path:
            rows.setdefault(old_path, _expect_existing(repo_root, old_path))
        if op == "new" and new_path:
            rows.setdefault(new_path, _expect_absent(repo_root, new_path))
        if op in {"rename", "rename_modify"} and new_path:
            rows.setdefault(new_path, _expect_absent(repo_root, new_path))

    invalid = [row for row in rows.values() if row.get("invalid")]
    return {
        "version": 1,
        "status": "pass" if not invalid else "fail",
        "files": [rows[key] for key in sorted(rows)],
        "findings": [
            {"path": row["path"], "reason": f"precondition_capture_{row['invalid']}"}
            for row in invalid
        ],
    }


def verify_patch_preconditions(repo_root: Path, snapshot: dict[str, Any]) -> dict[str, Any]:
    """Verify a captured patch snapshot immediately before mutation."""
    repo_root = repo_root.resolve()
    findings: list[dict[str, Any]] = []

    if int(snapshot.get("version", 0)) != 1:
        return {
            "status": "fail",
            "stale": True,
            "findings": [{"path": None, "reason": "unsupported_precondition_version"}],
        }

    for expected in snapshot.get("files", []):
        rel = str(expected.get("path") or "")
        try:
            path = _safe_target(repo_root, rel)
        except ValueError:
            findings.append({"path": rel, "reason": "unsafe_precondition_path"})
            continue

        if path.is_symlink():
            findings.append({"path": rel, "reason": "precondition_symlink"})
            continue

        mode = expected.get("expect")
        if mode == "absent":
            if path.exists():
                findings.append({"path": rel, "reason": "stale_target_created"})
            continue

        if mode != "sha256":
            findings.append({"path": rel, "reason": "invalid_precondition_expectation"})
            continue

        if not path.exists():
            findings.append({"path": rel, "reason": "stale_source_missing"})
            continue
        if not path.is_file():
            findings.append({"path": rel, "reason": "stale_source_not_regular_file"})
            continue

        actual = _sha256_file(path)
        if actual != expected.get("sha256"):
            findings.append(
                {
                    "path": rel,
                    "reason": "stale_source_modified",
                    "expected_sha256": expected.get("sha256"),
                    "actual_sha256": actual,
                }
            )

    return {
        "status": "pass" if not findings else "fail",
        "stale": bool(findings),
        "findings": findings,
    }
