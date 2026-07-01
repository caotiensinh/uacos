from __future__ import annotations

from pathlib import Path

UACOS_DIR = ".uacos"
DB_NAME = "repo_index.sqlite"

DEFAULT_IGNORE_DIRS = {
    ".git",
    ".uacos",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".next",
    ".nuxt",
    "target",
    "coverage",
    ".idea",
    ".vscode",
}

DEFAULT_IGNORE_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".so",
    ".dll",
    ".exe",
    ".bin",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".log",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".rar",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".pem",
    ".key",
    ".crt",
    ".pfx",
}

SECRET_LIKE_FILENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
}

MAX_TEXT_FILE_BYTES = 1_000_000


def resolve_repo(repo: str | None) -> Path:
    root = Path(repo or ".").expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {root}")
    return root


def uacos_dir(repo_root: Path) -> Path:
    return repo_root / UACOS_DIR


def db_path(repo_root: Path) -> Path:
    return uacos_dir(repo_root) / DB_NAME
