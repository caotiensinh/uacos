from __future__ import annotations

from pathlib import Path
from typing import Iterable

from uacos.security.diff_parser import parse_unified_diff
from uacos.security.patch_gate import validate_patch_text

AUTH_KEYWORDS = ("auth", "login", "session", "jwt", "token", "oauth", "password", "permission", "rbac")
NETWORK_KEYWORDS = ("requests.", "urllib", "httpx", "socket", "websocket", "subprocess", "curl", "wget")
CI_PATH_HINTS = (".github/workflows/", "scripts/release", "release_gate", "ci", "tox.ini")
DEPENDENCY_FILES = {"requirements.txt", "requirements-dev.txt", "pyproject.toml", "poetry.lock", "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock"}
CONFIG_KEYWORDS = ("config", "settings", ".env", "secret", "credential", "key")


def _has_any(text: str, needles: Iterable[str]) -> bool:
    low = (text or "").lower()
    return any(needle.lower() in low for needle in needles)


def _risk_level(categories: list[str], validation: dict) -> str:
    if validation.get("status") == "fail":
        return "block"
    high = {"auth_change", "network_call", "ci_release_change", "dependency_change", "sensitive_config_change"}
    if any(category in high for category in categories):
        return "high"
    if "broad_rewrite" in categories or "many_removed_lines" in categories:
        return "medium"
    return "low"


def classify_file_patch(path: str, added_lines: list[str], removed_lines: list[str]) -> dict:
    joined_added = "\n".join(added_lines)
    joined_removed = "\n".join(removed_lines)
    joined = joined_added + "\n" + joined_removed
    name = Path(path).name
    normalized = path.replace("\\", "/")
    categories: list[str] = []

    if _has_any(normalized, AUTH_KEYWORDS) or _has_any(joined, AUTH_KEYWORDS):
        categories.append("auth_change")
    if _has_any(joined_added, NETWORK_KEYWORDS):
        categories.append("network_call")
    if _has_any(normalized, CI_PATH_HINTS):
        categories.append("ci_release_change")
    if name in DEPENDENCY_FILES:
        categories.append("dependency_change")
    if _has_any(normalized, CONFIG_KEYWORDS):
        categories.append("sensitive_config_change")
    if len(added_lines) + len(removed_lines) >= 200:
        categories.append("broad_rewrite")
    if len(removed_lines) >= 80:
        categories.append("many_removed_lines")

    return {
        "path": path,
        "categories": sorted(set(categories)),
        "added_lines": len(added_lines),
        "removed_lines": len(removed_lines),
    }


def review_patch_text(patch_text: str, allowed_files=None, allowed_dirs=None, tests=None) -> dict:
    validation = validate_patch_text(patch_text, allowed_files=allowed_files or [], allowed_dirs=allowed_dirs or [])
    patches = parse_unified_diff(patch_text)
    file_reviews = [classify_file_patch(fp.path, fp.added_lines, fp.removed_lines) for fp in patches]
    categories = sorted({category for review in file_reviews for category in review["categories"]})
    risk_level = _risk_level(categories, validation)
    required_next_steps = []

    if risk_level == "block":
        required_next_steps.append("fix_patch_gate_failures_before_apply")
    if risk_level in {"high", "block"}:
        required_next_steps.append("human_review_required")
    if categories:
        required_next_steps.append("explain_risk_categories_before_apply")
    if not tests:
        required_next_steps.append("tests_required_before_safe_apply")
    if validation.get("status") != "fail":
        required_next_steps.append("apply_only_through_guarded_transaction_or_explicit_mcp_apply")

    return {
        "status": "fail" if risk_level == "block" else "pass",
        "risk_level": risk_level,
        "risk_categories": categories,
        "changed_files": validation.get("changed_files", []),
        "files_count": validation.get("files_count", 0),
        "added_lines": validation.get("added_lines", 0),
        "file_reviews": file_reviews,
        "validation": validation,
        "tests": tests or [],
        "writes_code": False,
        "required_next_steps": required_next_steps,
        "claim": "Patch review classifies risk and validates safety gates. It does not prove correctness and does not apply code.",
    }


def review_patch_file(patch_path: Path, **kwargs) -> dict:
    return review_patch_text(patch_path.read_text(encoding="utf-8", errors="replace"), **kwargs)
