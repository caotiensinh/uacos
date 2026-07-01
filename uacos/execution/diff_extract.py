from __future__ import annotations

from pathlib import Path
import re

DIFF_START_RE = re.compile(r"^diff --git ", re.MULTILINE)

def extract_unified_diff(text: str) -> str:
    m = DIFF_START_RE.search(text)
    if not m:
        return ""
    diff = text[m.start():].strip()
    fence_idx = diff.find("\n```")
    if fence_idx != -1:
        diff = diff[:fence_idx].strip()
    return diff + ("\n" if diff else "")

def extract_diff_from_file(agent_output: Path, output: Path | None = None) -> dict:
    text = agent_output.read_text(encoding="utf-8", errors="replace")
    diff = extract_unified_diff(text)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(diff, encoding="utf-8")
    return {
        "status": "ok" if diff else "fail",
        "has_diff": bool(diff),
        "output": str(output) if output else None,
        "diff": diff if not output else None,
    }
