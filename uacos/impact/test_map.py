from __future__ import annotations

from pathlib import Path
import re

SKIP_DIRS = {".git", ".uacos", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build", "reports"}
TEST_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx"}
SOURCE_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx"}


def _safe_rel(path: Path, repo_root: Path) -> str:
    return str(path.relative_to(repo_root)).replace("\\", "/")


def _skip(path: Path, repo_root: Path) -> bool:
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        return True
    return any(part in SKIP_DIRS for part in rel.parts)


def is_test_file(path: Path, repo_root: Path) -> bool:
    if not path.is_file() or path.suffix.lower() not in TEST_EXTS or _skip(path, repo_root):
        return False
    rel = _safe_rel(path, repo_root).lower()
    name = path.name.lower()
    return (
        "/test" in rel
        or rel.startswith("test")
        or name.startswith("test_")
        or name.endswith("_test.py")
        or name.endswith(".test.ts")
        or name.endswith(".test.tsx")
        or name.endswith(".test.js")
        or name.endswith(".test.jsx")
        or name.endswith(".spec.ts")
        or name.endswith(".spec.tsx")
        or name.endswith(".spec.js")
        or name.endswith(".spec.jsx")
    )


def _module_stem(rel: str) -> str:
    path = Path(rel)
    name = path.name
    for prefix in ["test_"]:
        if name.startswith(prefix):
            name = name[len(prefix):]
    for suffix in ["_test.py", ".test.ts", ".test.tsx", ".test.js", ".test.jsx", ".spec.ts", ".spec.tsx", ".spec.js", ".spec.jsx"]:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return Path(name).stem.lower()


def _source_key(rel: str) -> str:
    return Path(rel).stem.lower()


def _imports_source(test_text: str, source_rel: str) -> bool:
    stem = _source_key(source_rel)
    dotted = source_rel.replace("/", ".").rsplit(".", 1)[0]
    candidates = {stem, dotted, dotted.split(".")[-1]}
    low = test_text.lower()
    return any(candidate and candidate.lower() in low for candidate in candidates)


def _pytest_command(test_rel: str, test_name: str | None = None) -> str:
    if test_name:
        return f"python -m pytest -q {test_rel}::{test_name}"
    return f"python -m pytest -q {test_rel}"


def _js_test_command(test_rel: str) -> str:
    return f"npm test -- {test_rel}"


def _recommended_command(test_rel: str, test_name: str | None = None) -> str:
    suffix = Path(test_rel).suffix.lower()
    if suffix == ".py":
        return _pytest_command(test_rel, test_name=test_name)
    return _js_test_command(test_rel)


def _extract_pytest_names(text: str) -> list[str]:
    return re.findall(r"^\s*def\s+(test_[A-Za-z0-9_]+)\s*\(", text, flags=re.MULTILINE)[:50]


def list_source_files(repo_root: Path) -> list[str]:
    rows = []
    for path in sorted(repo_root.rglob("*")):
        if path.is_file() and path.suffix.lower() in SOURCE_EXTS and not _skip(path, repo_root) and not is_test_file(path, repo_root):
            rows.append(_safe_rel(path, repo_root))
    return rows


def list_test_files(repo_root: Path) -> list[str]:
    rows = []
    for path in sorted(repo_root.rglob("*")):
        if is_test_file(path, repo_root):
            rows.append(_safe_rel(path, repo_root))
    return rows


def map_tests_to_sources(repo_root: Path, source_files: list[str] | None = None, max_tests: int = 200) -> dict:
    """Map source files to likely tests through naming and import heuristics.

    The mapping is intentionally conservative and reviewable. It does not run tests.
    """

    sources = source_files or list_source_files(repo_root)
    tests = list_test_files(repo_root)[:max_tests]
    results = []
    for source in sources:
        source_stem = _source_key(source)
        matches = []
        for test_rel in tests:
            test_path = repo_root / test_rel
            try:
                text = test_path.read_text(encoding="utf-8", errors="replace")[:300000]
            except OSError:
                text = ""
            test_stem = _module_stem(test_rel)
            reasons = []
            if test_stem == source_stem or source_stem in test_stem or test_stem in source_stem:
                reasons.append("name_match")
            if _imports_source(text, source):
                reasons.append("import_or_reference_match")
            if not reasons:
                continue
            names = _extract_pytest_names(text) if test_rel.endswith(".py") else []
            matches.append({
                "test_file": test_rel,
                "reasons": sorted(set(reasons)),
                "test_names": names[:10],
                "recommended_commands": [_recommended_command(test_rel)] + [_recommended_command(test_rel, name) for name in names[:3]],
            })
        results.append({
            "source_file": source,
            "tests": matches,
            "test_count": len(matches),
            "confidence": "high" if any("import_or_reference_match" in m["reasons"] for m in matches) else "medium" if matches else "low",
        })
    return {
        "status": "ok",
        "source_count": len(sources),
        "test_file_count": len(tests),
        "mapped_source_count": len([row for row in results if row["test_count"] > 0]),
        "mappings": results,
        "claim": "Test-to-source mapping is heuristic. Recommended commands are evidence candidates, not proof until executed.",
    }


def suggest_tests_for_selected_files(repo_root: Path, selected_files: list[dict]) -> dict:
    sources = [item.get("file") or item.get("path") for item in selected_files or [] if item.get("file") or item.get("path")]
    sources = [source for source in sources if (repo_root / source).suffix.lower() in SOURCE_EXTS]
    return map_tests_to_sources(repo_root, source_files=sources)
