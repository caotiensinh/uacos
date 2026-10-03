from __future__ import annotations

from pathlib import Path
import hashlib

from uacos.ast_engine.parser import parse_python_file
from uacos.ast_engine.tree_sitter_js_ts import parse_js_ts_file_tree_sitter
from uacos.ast_engine.tree_sitter_rust_go import parse_rust_file_tree_sitter, parse_go_file_tree_sitter
from uacos.ast_engine.tree_sitter_java import parse_java_file_tree_sitter
from uacos.ast_engine.tree_sitter_c_cpp import parse_c_file_tree_sitter, parse_cpp_file_tree_sitter
from uacos.graph.roles import classify_source_path, is_test_path


SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".rs", ".go", ".java",
    ".c", ".h", ".cc", ".cpp", ".cxx", ".hh", ".hpp", ".hxx",
}


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def discover_source_files(repo_root: Path, include_tests: bool = True) -> list[Path]:
    files: list[Path] = []
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        if classify_source_path(rel) != "source":
            continue
        if not include_tests and is_test_path(rel):
            continue
        files.append(path)
    return files


def parse_source_file(path: Path, repo_root: Path) -> dict:
    suffix = path.suffix.lower()
    if suffix == ".py":
        doc = parse_python_file(path, repo_root=repo_root)
    elif suffix in {".js", ".jsx", ".ts", ".tsx"}:
        doc = parse_js_ts_file_tree_sitter(path, repo_root=repo_root)
    elif suffix == ".rs":
        doc = parse_rust_file_tree_sitter(path, repo_root)
    elif suffix == ".go":
        doc = parse_go_file_tree_sitter(path, repo_root)
    elif suffix == ".java":
        doc = parse_java_file_tree_sitter(path, repo_root)
    elif suffix in {".c", ".h"}:
        doc = parse_c_file_tree_sitter(path, repo_root)
    elif suffix in {".cc", ".cpp", ".cxx", ".hh", ".hpp", ".hxx"}:
        doc = parse_cpp_file_tree_sitter(path, repo_root)
    else:
        raise ValueError(f"unsupported source extension: {suffix}")
    return doc


def incremental_parse_repo(
    repo_root: Path,
    previous_graph: dict | None,
    include_tests: bool = True,
) -> tuple[list[dict], dict]:
    """Parse only changed/new supported files and reuse unchanged parsed docs."""
    previous_docs = {
        str(doc.get("path") or ""): doc
        for doc in (previous_graph or {}).get("parsed", []) or []
    }
    current_files = discover_source_files(repo_root, include_tests=include_tests)
    current_paths = {str(path.relative_to(repo_root)).replace("\\", "/") for path in current_files}

    parsed: list[dict] = []
    reused = 0
    reparsed = 0
    for path in current_files:
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        digest = _sha_file(path)
        old = previous_docs.get(rel)
        if old and old.get("sha256") == digest:
            parsed.append(old)
            reused += 1
            continue
        parsed.append(parse_source_file(path, repo_root))
        reparsed += 1

    deleted = sorted(set(previous_docs) - current_paths)
    parsed.sort(key=lambda row: str(row.get("path") or ""))
    return parsed, {
        "mode": "incremental",
        "reused_file_count": reused,
        "reparsed_file_count": reparsed,
        "deleted_file_count": len(deleted),
        "deleted_files": deleted,
    }
