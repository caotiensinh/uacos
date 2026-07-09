from __future__ import annotations

from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]

TEXT_EXTS = {
    ".md",
    ".py",
    ".json",
    ".toml",
    ".yml",
    ".yaml",
    ".txt",
    ".ini",
    ".cfg",
}

SKIP_DIRS = {
    ".git",
    ".uacos",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "reports",
}

# Unicode ranges and escaped code points keep this checker compatible with the
# repository English-only policy while still detecting common non-English prose.
NON_ENGLISH_RE = re.compile(
    "["
    "\\u3040-\\u30ff"  # Japanese Hiragana/Katakana
    "\\u3400-\\u9fff"  # CJK ideographs
    "\\uac00-\\ud7af"  # Korean Hangul
    "\\u0102\\u0103\\u00c2\\u00e2\\u0110\\u0111\\u00ca\\u00ea\\u00d4\\u00f4\\u01a0\\u01a1\\u01af\\u01b0"
    "\\u00c0-\\u00c3\\u00c8-\\u00ca\\u00cc-\\u00cd\\u00d2-\\u00d5\\u00d9-\\u00da\\u00dd"
    "\\u00e0-\\u00e3\\u00e8-\\u00ea\\u00ec-\\u00ed\\u00f2-\\u00f5\\u00f9-\\u00fa\\u00fd"
    "\\u1ea0-\\u1ef9"
    "]"
)


def should_scan(path: Path, repo_root: Path) -> bool:
    if not path.is_file() or path.suffix.lower() not in TEXT_EXTS:
        return False
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        return False
    return not any(part in SKIP_DIRS for part in rel.parts)


def scan_file(path: Path, repo_root: Path) -> list[dict]:
    rel = str(path.relative_to(repo_root)).replace("\\", "/")
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [{"file": rel, "line": 0, "match": "<read-error>", "reason": str(exc)}]

    findings = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        match = NON_ENGLISH_RE.search(line)
        if match:
            findings.append({
                "file": rel,
                "line": line_no,
                "match": match.group(0),
                "excerpt": line.strip()[:160],
            })
    return findings


def scan_repo(repo_root: Path) -> dict:
    files_scanned = 0
    findings: list[dict] = []
    for path in sorted(repo_root.rglob("*")):
        if not should_scan(path, repo_root):
            continue
        files_scanned += 1
        findings.extend(scan_file(path, repo_root))

    return {
        "status": "pass" if not findings else "fail",
        "repo": str(repo_root),
        "files_scanned": files_scanned,
        "finding_count": len(findings),
        "findings": findings[:200],
        "claim": "This is a conservative repository text check for common non-English scripts and Vietnamese diacritics. Allowed exceptions should be isolated and documented in English.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check repository text files for non-English prose markers.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    report = scan_repo(Path(args.repo).resolve())
    if args.summary:
        output = {key: report[key] for key in ["status", "files_scanned", "finding_count", "claim"]}
    else:
        output = report
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
