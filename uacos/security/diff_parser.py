from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath
import re


@dataclass
class FilePatch:
    old_path: str | None
    new_path: str | None
    added_lines: list[str] = field(default_factory=list)
    removed_lines: list[str] = field(default_factory=list)
    old_changed_lines: list[int] = field(default_factory=list)
    new_changed_lines: list[int] = field(default_factory=list)

    @property
    def path(self) -> str:
        return self.new_path or self.old_path or ""


def _clean_path(raw: str):
    raw = raw.strip()
    if raw == "/dev/null":
        return None
    if raw.startswith("a/") or raw.startswith("b/"):
        raw = raw[2:]
    return raw


def parse_unified_diff(text: str) -> list:
    patches = []
    current = None
    old_line = None
    new_line = None
    hunk_re = re.compile(r"^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@")

    for line in text.splitlines():
        if line.startswith("diff --git "):
            if current:
                patches.append(current)
            parts = line.split()
            old_path = _clean_path(parts[2]) if len(parts) > 2 else None
            new_path = _clean_path(parts[3]) if len(parts) > 3 else None
            current = FilePatch(old_path=old_path, new_path=new_path)
            old_line = None
            new_line = None
            continue
        if current is None:
            continue
        if line.startswith("--- "):
            current.old_path = _clean_path(line[4:])
            continue
        if line.startswith("+++ "):
            current.new_path = _clean_path(line[4:])
            continue

        hunk = hunk_re.match(line)
        if hunk:
            old_line = int(hunk.group(1))
            new_line = int(hunk.group(3))
            continue

        if line.startswith("+") and not line.startswith("+++"):
            current.added_lines.append(line[1:])
            if new_line is not None:
                current.new_changed_lines.append(new_line)
                new_line += 1
            continue
        if line.startswith("-") and not line.startswith("---"):
            current.removed_lines.append(line[1:])
            if old_line is not None:
                current.old_changed_lines.append(old_line)
                old_line += 1
            continue
        if line.startswith(" "):
            if old_line is not None:
                old_line += 1
            if new_line is not None:
                new_line += 1

    if current:
        patches.append(current)
    return patches


def path_is_safe(path: str) -> bool:
    if not path:
        return False
    p = PurePosixPath(path)
    if p.is_absolute():
        return False
    if ".." in p.parts:
        return False
    return True
