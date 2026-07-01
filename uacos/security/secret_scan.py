from pathlib import Path
import re
from uacos.scanner.ignore_rules import should_index_file, is_secret_like
from uacos.scanner.hash_cache import read_text_safely

SECRET_PATTERNS = [
    ("generic_api_key", re.compile(r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret)\b\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b")),
    ("private_key_block", re.compile(r"-----BEGIN (RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("jwt_like", re.compile(r"\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{20,}\b")),
]

MAX_SCAN_BYTES = 1_000_000
IGNORED_DIRS = {".git", ".uacos", ".venv", "venv", "node_modules", "dist", "build", "__pycache__"}

def iter_scan_files(repo_root: Path):
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        parts = path.relative_to(repo_root).parts
        if any(part in IGNORED_DIRS for part in parts[:-1]):
            continue
        yield path

def mask_secret(line: str) -> str:
    if len(line) <= 20:
        return "***"
    return line[:8] + "..." + line[-4:]

def scan_text_for_secrets(text: str, rel_path: str) -> list:
    findings = []
    for idx, line in enumerate(text.splitlines(), start=1):
        for name, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append({
                    "type": name,
                    "path": rel_path,
                    "line": idx,
                    "severity": "high",
                    "evidence": mask_secret(line.strip()),
                })
    return findings

def security_scan(repo_root: Path) -> dict:
    findings = []
    skipped = []
    files_scanned = 0

    for path in iter_scan_files(repo_root):
        rel = str(path.relative_to(repo_root)).replace("\\", "/")

        if is_secret_like(path):
            findings.append({
                "type": "secret_like_filename",
                "path": rel,
                "line": 0,
                "severity": "high",
                "evidence": "secret-like filename should not be sent to AI context",
            })
            continue

        try:
            size = path.stat().st_size
            if size > MAX_SCAN_BYTES:
                skipped.append({"path": rel, "reason": f"too_large:{size}"})
                continue

            ok, reason = should_index_file(path)
            if not ok:
                # Ignore binary/db/etc, but record non-binary suspicious skips.
                if "secret" in reason:
                    skipped.append({"path": rel, "reason": reason})
                continue

            text = read_text_safely(path)
            files_scanned += 1
            findings.extend(scan_text_for_secrets(text, rel))
        except Exception as exc:
            skipped.append({"path": rel, "reason": f"error:{type(exc).__name__}:{exc}"})

    return {
        "status": "fail" if findings else "pass",
        "files_scanned": files_scanned,
        "findings_count": len(findings),
        "findings": findings,
        "skipped": skipped[:100],
    }
