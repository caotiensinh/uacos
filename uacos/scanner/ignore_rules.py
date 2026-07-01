from pathlib import Path
from uacos.config import (
    DEFAULT_IGNORE_DIRS,
    DEFAULT_IGNORE_SUFFIXES,
    SECRET_LIKE_FILENAMES,
    MAX_TEXT_FILE_BYTES,
)
from uacos.scanner.language import looks_textual


def is_ignored_dir(path: Path) -> bool:
    return path.name in DEFAULT_IGNORE_DIRS


def is_secret_like(path: Path) -> bool:
    lower_name = path.name.lower()
    return lower_name in SECRET_LIKE_FILENAMES or lower_name.endswith(".pem") or lower_name.endswith(".key")


def should_index_file(path: Path) -> tuple[bool, str]:
    if is_secret_like(path):
        return False, "secret_like_filename"

    suffix = path.suffix.lower()
    if suffix in DEFAULT_IGNORE_SUFFIXES:
        return False, f"ignored_suffix:{suffix}"

    try:
        size = path.stat().st_size
    except OSError as exc:
        return False, f"stat_error:{exc}"

    if size > MAX_TEXT_FILE_BYTES:
        return False, f"too_large:{size}"

    if not looks_textual(path):
        return False, "non_text_extension"

    return True, "ok"
