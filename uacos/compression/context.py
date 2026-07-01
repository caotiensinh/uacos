from __future__ import annotations

from pathlib import Path
import re
import json
from uacos.scanner.file_scanner import scan_repo
from uacos.search import search_repo
from uacos.config import uacos_dir

def _read_text_safe(path: Path, max_chars: int = 20000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return text[:max_chars]
    except Exception:
        return ""

def summarize_python(text: str) -> dict:
    functions = re.findall(r"(?m)^def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", text)
    async_functions = re.findall(r"(?m)^async\s+def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(", text)
    classes = re.findall(r"(?m)^class\s+([A-Za-z_][A-Za-z0-9_]*)", text)
    routes = re.findall(r"@(?:app|router)\.(get|post|put|delete|patch)\([^\n]+", text)
    imports = re.findall(r"(?m)^(?:from\s+\S+\s+import\s+.+|import\s+.+)$", text)
    return {
        "classes": classes[:50],
        "functions": functions[:80],
        "async_functions": async_functions[:80],
        "routes": routes[:50],
        "imports": imports[:80],
        "line_count": text.count("\n") + 1 if text else 0,
    }

def summarize_file(repo_root: Path, rel_path: str) -> dict:
    path = repo_root / rel_path
    text = _read_text_safe(path)
    suffix = path.suffix.lower()
    summary = {"path": rel_path, "suffix": suffix, "line_count": text.count("\n") + 1 if text else 0}
    if suffix == ".py":
        summary.update(summarize_python(text))
    else:
        # Generic lightweight summary.
        summary["head"] = "\n".join([line for line in text.splitlines()[:20] if line.strip()])[:2000]
    return summary

def compress_context(repo_root: Path, task: str, max_files: int = 12, max_chars: int = 12000) -> dict:
    scan_repo(repo_root)
    hits = search_repo(repo_root, task, limit=max_files)
    summaries = []
    used = set()
    for hit in hits:
        rel = hit.get("path") or hit.get("file_path")
        if not rel or rel in used:
            continue
        used.add(rel)
        summaries.append(summarize_file(repo_root, rel))

    # fallback important source files: search may return no rows in tiny/new repos
    if len(summaries) < min(3, max_files):
        for path in sorted(repo_root.rglob("*")):
            if len(summaries) >= max_files:
                break
            if not path.is_file():
                continue
            if ".uacos" in path.parts or "__pycache__" in path.parts:
                continue
            if path.suffix.lower() not in {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".md"}:
                continue
            rel = str(path.relative_to(repo_root)).replace("\\", "/")
            if rel in used:
                continue
            used.add(rel)
            summaries.append(summarize_file(repo_root, rel))
    content_lines = ["# Compressed Repo Context", "", f"Task: {task}", ""]
    for s in summaries:
        content_lines.append(f"## {s['path']}")
        content_lines.append(f"- lines: {s.get('line_count')}")
        if s.get("classes"):
            content_lines.append("- classes: " + ", ".join(s["classes"][:20]))
        if s.get("functions"):
            content_lines.append("- functions: " + ", ".join(s["functions"][:30]))
        if s.get("async_functions"):
            content_lines.append("- async functions: " + ", ".join(s["async_functions"][:30]))
        if s.get("imports"):
            content_lines.append("- imports: " + "; ".join(s["imports"][:20]))
        if s.get("head"):
            content_lines.append("```text\n" + s["head"][:1500] + "\n```")
        content_lines.append("")
    content = "\n".join(content_lines)[:max_chars]
    out_dir = uacos_dir(repo_root) / "compressed_context"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "latest_compressed_context.md"
    out_path.write_text(content, encoding="utf-8")
    return {"status": "ok", "task": task, "file_count": len(summaries), "context_file": str(out_path), "content": content, "char_count": len(content)}
