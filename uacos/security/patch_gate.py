from pathlib import Path
from uacos.security.diff_parser import parse_unified_diff, path_is_safe
from uacos.security.secret_scan import scan_text_for_secrets

BLOCKED_PATH_SUFFIXES = {".pem", ".key", ".pfx", ".crt", ".sqlite", ".sqlite3", ".db"}
BLOCKED_FILENAMES = {".env", ".env.local", ".env.production", ".env.development"}

def _path_allowed(path: str, allowed_files: set, allowed_dirs: set):
    if not path_is_safe(path):
        return False, "unsafe_path"
    name = Path(path).name
    if name in BLOCKED_FILENAMES or any(path.endswith(s) for s in BLOCKED_PATH_SUFFIXES):
        return False, "blocked_sensitive_path"
    if allowed_files and path in allowed_files:
        return True, "allowed_file"
    if allowed_dirs:
        normalized = path.replace("\\", "/")
        for d in allowed_dirs:
            prefix = d.strip("/").replace("\\", "/") + "/"
            if normalized.startswith(prefix):
                return True, "allowed_dir"
    if not allowed_files and not allowed_dirs:
        return True, "no_scope_restriction"
    return False, "outside_allowed_scope"

def validate_patch_text(patch_text: str, allowed_files=None, allowed_dirs=None, max_files: int = 8, max_added_lines: int = 800) -> dict:
    allowed_file_set = set(allowed_files or [])
    allowed_dir_set = set(allowed_dirs or [])
    patches = parse_unified_diff(patch_text)
    findings = []
    changed_files = []

    if not patches:
        return {
            "status": "fail",
            "reason": "no_unified_diff_detected",
            "changed_files": [],
            "findings": [{"severity": "high", "type": "no_diff", "message": "No unified diff detected"}],
        }

    total_added = 0
    for fp in patches:
        path = fp.path
        changed_files.append(path)
        ok, reason = _path_allowed(path, allowed_file_set, allowed_dir_set)
        if not ok:
            findings.append({"severity": "high", "type": "scope_violation", "path": path, "message": reason})

        total_added += len(fp.added_lines)
        added_text = "\\n".join(fp.added_lines)
        for secret in scan_text_for_secrets(added_text, path):
            findings.append({
                "severity": secret["severity"],
                "type": "secret_in_added_lines",
                "path": path,
                "line": secret["line"],
                "message": secret["type"],
                "evidence": secret["evidence"],
            })

    if len(changed_files) > max_files:
        findings.append({"severity": "medium", "type": "too_many_files", "message": f"changed_files={len(changed_files)} max_files={max_files}"})

    if total_added > max_added_lines:
        findings.append({"severity": "medium", "type": "too_many_added_lines", "message": f"added_lines={total_added} max_added_lines={max_added_lines}"})

    return {
        "status": "fail" if any(f["severity"] == "high" for f in findings) else "pass",
        "changed_files": changed_files,
        "files_count": len(changed_files),
        "added_lines": total_added,
        "findings": findings,
    }

def validate_patch_file(patch_path: Path, **kwargs) -> dict:
    text = patch_path.read_text(encoding="utf-8", errors="replace")
    return validate_patch_text(text, **kwargs)
