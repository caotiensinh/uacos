from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from uacos.ast_engine.js_parser import parse_repo_js_ts
from uacos.ast_engine.parser import parse_repo_python
from uacos.ast_engine.tree_sitter_js_ts import (
    parse_repo_js_ts_tree_sitter,
    tree_sitter_available,
)
from uacos.ast_engine.tree_sitter_rust_go import (
    parse_repo_go_tree_sitter,
    parse_repo_rust_tree_sitter,
    tree_sitter_go_available,
    tree_sitter_rust_available,
)
from uacos.ast_engine.tree_sitter_java import (
    parse_repo_java_tree_sitter,
    tree_sitter_java_available,
)
from uacos.ast_engine.tree_sitter_c_cpp import (
    parse_repo_c_tree_sitter,
    parse_repo_cpp_tree_sitter,
    tree_sitter_c_available,
    tree_sitter_cpp_available,
)


@dataclass(frozen=True)
class LanguageBackend:
    name: str
    languages: tuple[str, ...]
    extensions: tuple[str, ...]
    semantic_level: str
    parse_repo: Callable[[Path, bool], list[dict]]
    parser_engine: str
    available: Callable[[], bool] | None = None

    def is_available(self) -> bool:
        return True if self.available is None else bool(self.available())


def _parse_python(repo_root: Path, include_tests: bool = True) -> list[dict]:
    return parse_repo_python(repo_root, include_tests=include_tests)


def _filter_tests(docs: list[dict], include_tests: bool) -> list[dict]:
    if include_tests:
        return docs
    filtered = []
    for doc in docs:
        rel = str(doc.get("path") or "").replace("\\", "/")
        lower = rel.lower()
        name = Path(rel).name.lower()
        if "/test/" in f"/{lower}/" or "/tests/" in f"/{lower}/" or "/src/test/" in f"/{lower}/":
            continue
        if name.endswith((
            ".test.js", ".test.jsx", ".test.ts", ".test.tsx",
            ".spec.js", ".spec.jsx", ".spec.ts", ".spec.tsx",
            "_test.go",
        )):
            continue
        filtered.append(doc)
    return filtered


def _parse_js_ts_tree_sitter(repo_root: Path, include_tests: bool = True) -> list[dict]:
    return _filter_tests(parse_repo_js_ts_tree_sitter(repo_root), include_tests)


def _parse_js_ts_fallback(repo_root: Path, include_tests: bool = True) -> list[dict]:
    return _filter_tests(parse_repo_js_ts(repo_root), include_tests)


def _parse_rust_tree_sitter(repo_root: Path, include_tests: bool = True) -> list[dict]:
    return _filter_tests(parse_repo_rust_tree_sitter(repo_root), include_tests)


def _parse_go_tree_sitter(repo_root: Path, include_tests: bool = True) -> list[dict]:
    return _filter_tests(parse_repo_go_tree_sitter(repo_root), include_tests)


def _parse_java_tree_sitter(repo_root: Path, include_tests: bool = True) -> list[dict]:
    return _filter_tests(parse_repo_java_tree_sitter(repo_root), include_tests)


def _parse_c_tree_sitter(repo_root: Path, include_tests: bool = True) -> list[dict]:
    return _filter_tests(parse_repo_c_tree_sitter(repo_root), include_tests)


def _parse_cpp_tree_sitter(repo_root: Path, include_tests: bool = True) -> list[dict]:
    return _filter_tests(parse_repo_cpp_tree_sitter(repo_root), include_tests)


BACKENDS: tuple[LanguageBackend, ...] = (
    LanguageBackend(
        name="python_ast",
        languages=("python",),
        extensions=(".py",),
        semantic_level="native_ast",
        parse_repo=_parse_python,
        parser_engine="python_ast",
    ),
    LanguageBackend(
        name="javascript_typescript",
        languages=("javascript", "typescript"),
        extensions=(".js", ".jsx", ".ts", ".tsx"),
        semantic_level="tree_sitter_ast",
        parse_repo=_parse_js_ts_tree_sitter,
        parser_engine="tree_sitter",
        available=tree_sitter_available,
    ),
    LanguageBackend(
        name="javascript_typescript_fallback",
        languages=("javascript", "typescript"),
        extensions=(".js", ".jsx", ".ts", ".tsx"),
        semantic_level="structured_regex",
        parse_repo=_parse_js_ts_fallback,
        parser_engine="regex",
    ),
    LanguageBackend(
        name="rust",
        languages=("rust",),
        extensions=(".rs",),
        semantic_level="tree_sitter_ast",
        parse_repo=_parse_rust_tree_sitter,
        parser_engine="tree_sitter",
        available=tree_sitter_rust_available,
    ),
    LanguageBackend(
        name="go",
        languages=("go",),
        extensions=(".go",),
        semantic_level="tree_sitter_ast",
        parse_repo=_parse_go_tree_sitter,
        parser_engine="tree_sitter",
        available=tree_sitter_go_available,
    ),
    LanguageBackend(
        name="java",
        languages=("java",),
        extensions=(".java",),
        semantic_level="tree_sitter_ast",
        parse_repo=_parse_java_tree_sitter,
        parser_engine="tree_sitter",
        available=tree_sitter_java_available,
    ),
    LanguageBackend(
        name="c",
        languages=("c",),
        extensions=(".c", ".h"),
        semantic_level="tree_sitter_ast",
        parse_repo=_parse_c_tree_sitter,
        parser_engine="tree_sitter",
        available=tree_sitter_c_available,
    ),
    LanguageBackend(
        name="cpp",
        languages=("cpp",),
        extensions=(".cc", ".cpp", ".cxx", ".hh", ".hpp", ".hxx"),
        semantic_level="tree_sitter_ast",
        parse_repo=_parse_cpp_tree_sitter,
        parser_engine="tree_sitter",
        available=tree_sitter_cpp_available,
    ),
)


def available_backends() -> list[dict]:
    rows = []
    for backend in BACKENDS:
        rows.append({
            "name": backend.name,
            "languages": list(backend.languages),
            "extensions": list(backend.extensions),
            "semantic_level": backend.semantic_level,
            "parser_engine": backend.parser_engine,
            "available": backend.is_available(),
        })
    return rows


def parse_repo_languages(
    repo_root: Path,
    include_tests: bool = True,
    backend_names: set[str] | None = None,
) -> list[dict]:
    parsed: list[dict] = []
    claimed_extensions: set[str] = set()

    for backend in BACKENDS:
        if backend_names is not None and backend.name not in backend_names:
            continue
        if not backend.is_available():
            continue
        if backend_names is None and any(ext in claimed_extensions for ext in backend.extensions):
            continue

        for doc in backend.parse_repo(repo_root, include_tests):
            item = dict(doc)
            item.setdefault("backend", backend.name)
            item.setdefault("semantic_level", backend.semantic_level)
            item.setdefault("parser_engine", backend.parser_engine)
            parsed.append(item)
        claimed_extensions.update(backend.extensions)

    parsed.sort(key=lambda row: str(row.get("path") or ""))
    return parsed
