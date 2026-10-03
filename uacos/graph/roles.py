from __future__ import annotations

from pathlib import PurePosixPath


GENERATED_PARTS = {
    "dist", "build", "out", "coverage", ".next", ".nuxt", "generated", "gen",
}
VENDOR_PARTS = {
    "vendor", "node_modules", "third_party", "third-party", "external", ".venv", "venv",
}
IGNORED_PARTS = {".git", ".uacos", "__pycache__"}


def normalized_parts(path: str) -> tuple[str, ...]:
    return tuple(part.lower() for part in PurePosixPath(path.replace("\\", "/")).parts)


def classify_source_path(path: str) -> str:
    parts = set(normalized_parts(path))
    if parts & IGNORED_PARTS:
        return "ignored"
    if parts & VENDOR_PARTS:
        return "vendor"
    if parts & GENERATED_PARTS:
        return "generated"
    return "source"


def is_test_path(path: str) -> bool:
    parts = normalized_parts(path)
    name = PurePosixPath(path.replace("\\", "/")).name.lower()
    return (
        "test" in parts
        or "tests" in parts
        or "__tests__" in parts
        or name.startswith("test_")
        or name.endswith("_test.go")
        or ".test." in name
        or ".spec." in name
    )


def semantic_file_role(path: str) -> str:
    lower = path.replace("\\", "/").lower()
    if is_test_path(path):
        return "test"
    if any(token in lower for token in ("/repository/", "/repositories/", "/repo/", "/dao/", "/db/", "/database/")):
        return "database"
    stem = PurePosixPath(lower).stem
    if stem.endswith(("_repository", "repository", "_repo", "dao", "database", "db")):
        return "database"
    if "/service/" in lower or "/services/" in lower or stem.endswith(("_service", "service")):
        return "service"
    if any(token in lower for token in ("/route/", "/routes/", "/controller/", "/controllers/", "/handler/", "/handlers/", "/api/")):
        return "handler"
    return "source"
