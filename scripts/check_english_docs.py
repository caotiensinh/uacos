from __future__ import annotations

from pathlib import Path
import argparse
import ast
import io
import json
import re
import tokenize

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

ALLOW_MARKER = "language-policy: allow-non-english"

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


def _is_allowed_line(lines: list[str], line_no: int) -> bool:
    """Allow one explicitly documented exception on the marker line or next line."""
    current = lines[line_no - 1] if 0 < line_no <= len(lines) else ""
    previous = lines[line_no - 2] if line_no > 1 else ""
    return ALLOW_MARKER in current or ALLOW_MARKER in previous


def _is_allowed_proper_noun(line: str) -> bool:
    """Allow an isolated possessive proper name such as a maintainer name.

    The whole line is not exempt: exactly one whitespace-delimited token may
    contain a detected character, and that token must look like a capitalized
    possessive name. This keeps ordinary non-English prose detectable.
    """
    flagged_tokens = [token.strip("`*_#()[]{}.,:;!?\"") for token in line.split() if NON_ENGLISH_RE.search(token)]
    if len(flagged_tokens) != 1:
        return False
    token = flagged_tokens[0]
    return bool(token and token[0].isupper() and (token.endswith("'s") or token.endswith("’s")))


def _finding(rel: str, line_no: int, line: str, match: re.Match[str]) -> dict:
    return {
        "file": rel,
        "line": line_no,
        "match": match.group(0),
        "excerpt": line.strip()[:160],
    }


def _scan_line_numbers(rel: str, lines: list[str], line_numbers: set[int]) -> list[dict]:
    findings = []
    for line_no in sorted(line_numbers):
        if line_no < 1 or line_no > len(lines) or _is_allowed_line(lines, line_no):
            continue
        line = lines[line_no - 1]
        match = NON_ENGLISH_RE.search(line)
        if match and not _is_allowed_proper_noun(line):
            findings.append(_finding(rel, line_no, line, match))
    return findings


def _python_prose_lines(text: str) -> set[int]:
    """Return Python line numbers that are comments or real docstrings.

    Runtime string literals are intentionally excluded because UACOS contains
    localization labels, multilingual keyword fixtures, and Unicode test data.
    """
    line_numbers: set[int] = set()

    try:
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type == tokenize.COMMENT:
                line_numbers.add(token.start[0])
    except (IndentationError, tokenize.TokenError):
        # compileall/pytest own syntax validity. Keep the language check focused
        # on prose that can be classified reliably.
        pass

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return line_numbers

    docstring_nodes = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
    for node in ast.walk(tree):
        if not isinstance(node, docstring_nodes) or not node.body:
            continue
        first = node.body[0]
        if not isinstance(first, ast.Expr):
            continue
        value = first.value
        if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
            continue
        start = getattr(value, "lineno", getattr(first, "lineno", 0))
        end = getattr(value, "end_lineno", start)
        if start:
            line_numbers.update(range(start, end + 1))

    return line_numbers


def scan_file(path: Path, repo_root: Path) -> list[dict]:
    rel = str(path.relative_to(repo_root)).replace("\\", "/")
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [{"file": rel, "line": 0, "match": "<read-error>", "reason": str(exc)}]

    lines = text.splitlines()
    if path.suffix.lower() == ".py":
        return _scan_line_numbers(rel, lines, _python_prose_lines(text))

    return _scan_line_numbers(rel, lines, set(range(1, len(lines) + 1)))


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
        "claim": (
            "This is a conservative repository prose check for common non-English scripts and Vietnamese "
            "diacritics. Python runtime string literals are excluded so localization and Unicode fixtures remain "
            "supported; Python comments/docstrings and other text files are checked. Explicit technical exceptions "
            f"may use the marker '{ALLOW_MARKER}'."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check repository prose for non-English markers.")
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
