from pathlib import Path
from uacos.scanner.hash_cache import read_text_safely

def extract_snippet(repo_root: Path, rel_path: str, start: int, end: int, context: int = 2) -> dict:
    start = max(1, start)
    end = max(start, end)
    target = (repo_root / rel_path).resolve()
    try:
        target.relative_to(repo_root.resolve())
    except ValueError:
        raise ValueError("File path escapes repository root")
    if not target.exists() or not target.is_file():
        raise FileNotFoundError(f"File not found: {rel_path}")

    lines = read_text_safely(target).splitlines()
    s = max(1, start - context)
    e = min(len(lines), end + context)
    selected = []
    for line_no in range(s, e + 1):
        if 1 <= line_no <= len(lines):
            selected.append(f"{line_no:>5}: {lines[line_no - 1]}")
    return {"path": rel_path, "start": s, "end": e, "content": "\n".join(selected)}
