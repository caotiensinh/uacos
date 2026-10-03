from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from uacos.ast_engine.js_parser import parse_repo_js_ts
from uacos.ast_engine.parser import parse_repo_python


@dataclass(frozen=True)
class LanguageBackend:
    name: str
    languages: tuple[str, ...]
    extensions: tuple[str, ...]
    semantic_level: str
    parse_repo: Callable[[Path, bool], list[dict]]


def _parse_python(repo_root: Path, include_tests: bool = True) -> list[dict]:
    return parse_repo_python(repo_root, include_tests=include_tests)


def _parse_js_ts(repo_root: Path, include_tests: bool = True) -> list[dict]:
    docs = parse_repo_js_ts(repo_root)
    if include_tests:
        return docs
    filtered = []
    for doc in docs:
        rel = str(doc.get("path") or "").replace("\\", "/")
        name = Path(rel).name.lower()
        if "/test/" in f"/{rel.lower()}/" or "/tests/" in f"/{rel.lower()}/":
            continue
        if name.endswith((".test.js", ".test.jsx", ".test.ts", ".test.tsx", ".spec.js", ".spec.jsx", ".spec.ts", ".spec.tsx")):
            continue
        filtered.append(doc)
    return filtered


BACKENDS: tuple[LanguageBackend, ...] = (
    LanguageBackend(
        name="python_ast",
        languages=("python",),
        extensions=(".py",),
        semantic_level="native_ast",
        parse_repo=_parse_python,
    ),
    LanguageBackend(
        name="javascript_typescript",
        languages=("javascript", "typescript"),
        extensions=(".js", ".jsx", ".ts", ".tsx"),
        semantic_level="structured_regex",
        parse_repo=_parse_js_ts,
    ),
)


def available_backends() -> list[dict]:
    return [
        {
            "name": backend.name,
            "languages": list(backend.languages),
            "extensions": list(backend.extensions),
            "semantic_level": backend.semantic_level,
        }
        for backend in BACKENDS
    ]


def parse_repo_languages(
    repo_root: Path,
    include_tests: bool = True,
    backend_names: set[str] | None = None,
) -> list[dict]:
    parsed: list[dict] = []
    for backend in BACKENDS:
        if backend_names is not None and backend.name not in backend_names:
            continue
        for doc in backend.parse_repo(repo_root, include_tests):
            item = dict(doc)
            item.setdefault("backend", backend.name)
            item.setdefault("semantic_level", backend.semantic_level)
            parsed.append(item)
    parsed.sort(key=lambda row: str(row.get("path") or ""))
    return parsed
