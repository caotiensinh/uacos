from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib
import re
import ast

from uacos.config import uacos_dir
from uacos.llm.hardened import estimate_tokens
from uacos.impact.analyzer import impact_by_task
from uacos.ast_engine.js_parser import parse_js_ts_file
from uacos.graph.builder import build_graph, load_graph
from uacos.memory.store import search_memories
from uacos.skill.store import suggest_skills

SKIP_SUMMARY_DIRS = {".git", ".uacos", ".venv", "venv", "__pycache__", ".history", ".pytest_cache", "reports", "uacos.egg-info", "dist", "build", "node_modules"}

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def compression_dir(repo_root: Path) -> Path:
    p = uacos_dir(repo_root) / "compression"
    p.mkdir(parents=True, exist_ok=True)
    return p

def compression_cache_path(repo_root: Path) -> Path:
    return compression_dir(repo_root) / "summary_cache.json"

def latest_context_path(repo_root: Path) -> Path:
    return compression_dir(repo_root) / "latest_compressed_context.md"

def latest_report_path(repo_root: Path) -> Path:
    return compression_dir(repo_root) / "latest_compression_report.json"

def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _safe_read(path: Path, limit: int = 500000) -> str:
    return path.read_text(encoding="utf-8", errors="replace")[:limit]

def _extract_docstring(text: str) -> str:
    try:
        tree = ast.parse(text)
        return ast.get_docstring(tree) or ""
    except Exception:
        return ""

def _python_outline(text: str) -> dict:
    out = {
        "module_doc": _extract_docstring(text)[:800],
        "imports": [],
        "classes": [],
        "functions": [],
        "routes": [],
        "calls": [],
    }
    try:
        tree = ast.parse(text)
    except Exception as exc:
        out["parse_error"] = f"{type(exc).__name__}: {exc}"
        return out

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                out["imports"].append(a.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for a in node.names:
                out["imports"].append(f"{mod}.{a.name}" if mod else a.name)
        elif isinstance(node, ast.ClassDef):
            methods = [x.name for x in node.body if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef))]
            out["classes"].append({"name": node.name, "lineno": node.lineno, "methods": methods[:30]})
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [a.arg for a in node.args.args]
            doc = ast.get_docstring(node) or ""
            out["functions"].append({"name": node.name, "lineno": node.lineno, "args": args[:20], "doc": doc[:300]})
        elif isinstance(node, ast.Call):
            fname = ""
            f = node.func
            if isinstance(f, ast.Name):
                fname = f.id
            elif isinstance(f, ast.Attribute):
                parts = []
                cur = f
                while isinstance(cur, ast.Attribute):
                    parts.append(cur.attr)
                    cur = cur.value
                if isinstance(cur, ast.Name):
                    parts.append(cur.id)
                fname = ".".join(reversed(parts))
            if fname:
                out["calls"].append(fname)
    # FastAPI/Flask-ish route decorator text fallback.
    out["routes"] = re.findall(r"@(?:app|router|bp)\.(?:get|post|put|delete|patch)\([^\n]+", text)[:80]
    out["imports"] = sorted(set(out["imports"]))[:120]
    out["calls"] = sorted(set(out["calls"]))[:160]
    out["functions"] = out["functions"][:120]
    return out

def summarize_file(repo_root: Path, rel: str, max_raw_lines: int = 80) -> dict:
    path = repo_root / rel
    text = _safe_read(path)
    suffix = path.suffix.lower()
    raw_tokens = estimate_tokens(text)
    base = {
        "path": rel,
        "sha256": _sha(path),
        "suffix": suffix,
        "line_count": text.count("\n") + 1 if text else 0,
        "raw_tokens_est": raw_tokens,
        "summarized_at": utcnow(),
    }
    if suffix == ".py":
        outline = _python_outline(text)
        summary_lines = [f"# {rel}", f"Lines: {base['line_count']}", f"Raw tokens est: {raw_tokens}"]
        if outline.get("module_doc"):
            summary_lines.append("Module doc: " + outline["module_doc"])
        if outline.get("imports"):
            summary_lines.append("Imports: " + ", ".join(outline["imports"][:35]))
        if outline.get("classes"):
            summary_lines.append("Classes:")
            for c in outline["classes"][:30]:
                summary_lines.append(f"- {c['name']} methods={','.join(c.get('methods', [])[:12])}")
        if outline.get("functions"):
            summary_lines.append("Functions:")
            for f in outline["functions"][:60]:
                args = ", ".join(f.get("args", [])[:8])
                doc = (" - " + f.get("doc", "")) if f.get("doc") else ""
                summary_lines.append(f"- {f['name']}({args}) line={f['lineno']}{doc}")
        if outline.get("routes"):
            summary_lines.append("Routes: " + "; ".join(outline["routes"][:20]))
        if outline.get("calls"):
            summary_lines.append("Calls: " + ", ".join(outline["calls"][:60]))
        if outline.get("parse_error"):
            summary_lines.append("Parse error: " + outline["parse_error"])
        summary = "\n".join(summary_lines)
        base.update({"kind": "python_ast", "outline": outline, "summary": summary, "summary_tokens_est": estimate_tokens(summary)})
        return base


    if suffix in {".js", ".jsx", ".ts", ".tsx"}:
        parsed = parse_js_ts_file(path, repo_root=repo_root)
        summary_lines = [f"# {rel}", f"Lines: {base['line_count']}", f"Raw tokens est: {raw_tokens}", f"Language: {parsed['language']}"]
        if parsed.get("imports"):
            summary_lines.append("Imports: " + ", ".join(parsed["imports"][:60]))
        if parsed.get("classes"):
            summary_lines.append("Classes: " + ", ".join(c["name"] for c in parsed["classes"][:40]))
        if parsed.get("functions"):
            summary_lines.append("Functions:")
            for f in parsed["functions"][:80]:
                summary_lines.append(f"- {f['name']} kind={f.get('kind')} line={f.get('lineno')}")
        if parsed.get("api_calls"):
            summary_lines.append("API calls:")
            for c in parsed["api_calls"][:80]:
                summary_lines.append(f"- {c['endpoint']} line={c.get('lineno')} kind={c.get('kind')}")
        summary = "\n".join(summary_lines)
        base.update({"kind": "js_ts", "outline": parsed, "summary": summary, "summary_tokens_est": estimate_tokens(summary)})
        return base

    # Generic non-Python summary.
    lines = [l.rstrip() for l in text.splitlines()]
    nonempty = [l for l in lines if l.strip()]
    head = "\n".join(nonempty[:max_raw_lines])
    headings = [l for l in nonempty if l.lstrip().startswith("#")][:40]
    summary = f"# {rel}\nLines: {base['line_count']}\nRaw tokens est: {raw_tokens}\n"
    if headings:
        summary += "Headings:\n" + "\n".join("- " + h[:160] for h in headings) + "\n"
    summary += "Head excerpt:\n" + head[:3500]
    base.update({"kind": "generic", "summary": summary, "summary_tokens_est": estimate_tokens(summary)})
    return base

def load_compression_cache(repo_root: Path) -> dict:
    path = compression_cache_path(repo_root)
    if not path.exists():
        return {"version": 1, "files": {}, "updated_at": None}
    return json.loads(path.read_text(encoding="utf-8"))

def save_compression_cache(repo_root: Path, cache: dict) -> dict:
    cache["updated_at"] = utcnow()
    path = compression_cache_path(repo_root)
    path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "ok", "cache_file": str(path)}

def build_summary_cache(repo_root: Path, include_exts: list[str] | None = None) -> dict:
    include_exts = include_exts or [".py", ".md", ".js", ".ts", ".tsx", ".go", ".rs", ".java", ".yaml", ".yml", ".json"]
    cache = load_compression_cache(repo_root)
    files = cache.setdefault("files", {})
    updated = 0
    skipped = 0
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_SUMMARY_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in include_exts:
            continue
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        sha = _sha(path)
        if files.get(rel, {}).get("sha256") == sha:
            skipped += 1
            continue
        files[rel] = summarize_file(repo_root, rel)
        updated += 1
    save_compression_cache(repo_root, cache)
    raw = sum(v.get("raw_tokens_est", 0) for v in files.values())
    compressed = sum(v.get("summary_tokens_est", 0) for v in files.values())
    ratio = round((compressed / raw), 4) if raw else 0
    return {"status": "ok", "updated": updated, "skipped": skipped, "file_count": len(files), "raw_tokens_est": raw, "summary_tokens_est": compressed, "compression_ratio": ratio, "cache_file": str(compression_cache_path(repo_root))}

def project_summary(repo_root: Path, max_files: int = 80) -> dict:
    build_graph(repo_root)
    cache_result = build_summary_cache(repo_root)
    cache = load_compression_cache(repo_root)
    graph = load_graph(repo_root)
    files = list(cache.get("files", {}).values())
    files.sort(key=lambda x: x.get("raw_tokens_est", 0), reverse=True)
    lines = ["# UACOS Project Compressed Summary", "", f"Repo: {repo_root}", "", "## Graph Stats"]
    stats = graph.get("stats", {})
    lines.append(f"- files: {stats.get('file_count', 0)}")
    lines.append(f"- symbols: {stats.get('symbol_count', 0)}")
    lines.append(f"- calls: {stats.get('call_edge_count', 0)}")
    lines.append("")
    lines.append("## File Summaries")
    for f in files[:max_files]:
        lines.append(f"### {f['path']}")
        lines.append(f"- kind: {f.get('kind')}")
        lines.append(f"- lines: {f.get('line_count')}")
        lines.append(f"- raw_tokens_est: {f.get('raw_tokens_est')}")
        lines.append(f"- summary_tokens_est: {f.get('summary_tokens_est')}")
        summ = f.get("summary", "")
        lines.append("```text\n" + summ[:2200] + "\n```")
        lines.append("")
    content = "\n".join(lines)
    out = compression_dir(repo_root) / "project_compressed_summary.md"
    out.write_text(content, encoding="utf-8")
    return {"status": "ok", "summary_file": str(out), "tokens_est": estimate_tokens(content), "cache": cache_result, "content": content}

def compressed_context(repo_root: Path, task: str, max_tokens: int = 6000, max_files: int = 8, include_raw_for_top: int = 1, refresh_cache: bool = True) -> dict:
    if refresh_cache:
        build_summary_cache(repo_root)
    cache = load_compression_cache(repo_root)
    impact = impact_by_task(repo_root, task, limit=max_files * 2)
    try:
        memories = search_memories(repo_root, task, limit=5)
    except Exception:
        memories = []
    skills = suggest_skills(repo_root, task, limit=5, min_score=1.0)

    selected = []
    lines = ["# UACOS Compressed Task Context", "", f"Task: {task}", "", "## Skills"]
    for s in skills:
        chunk = f"- {s.get('title')} ({s.get('id')}): {'; '.join(s.get('solution_steps', [])[:3])}"
        if estimate_tokens("\n".join(lines) + "\n" + chunk) <= max_tokens:
            lines.append(chunk)
    lines.append("")
    lines.append("## Memories")
    for m in memories:
        chunk = f"- {m.get('key')}: {str(m.get('value',''))[:500]}"
        if estimate_tokens("\n".join(lines) + "\n" + chunk) <= max_tokens:
            lines.append(chunk)

    lines.append("")
    lines.append("## Impact Files")
    for idx, row in enumerate(impact.get("impacted_files", [])[:max_files]):
        rel = row["file"]
        item = cache.get("files", {}).get(rel)
        if not item:
            continue
        summary = item.get("summary", "")
        chunk = f"### {rel}\n- impact_score: {row.get('score')}\n- reasons: {', '.join(row.get('reasons', []))}\n- raw_tokens_est: {item.get('raw_tokens_est')}\n- summary_tokens_est: {item.get('summary_tokens_est')}\n```text\n{summary[:3000]}\n```\n"
        if idx < include_raw_for_top:
            path = repo_root / rel
            if path.exists() and path.stat().st_size < 60000:
                raw = _safe_read(path, 12000)
                chunk += f"\n#### Raw excerpt\n```text\n{raw[:5000]}\n```\n"
        if estimate_tokens("\n".join(lines) + "\n" + chunk) > max_tokens:
            continue
        lines.append(chunk)
        selected.append({"file": rel, "score": row.get("score"), "summary_tokens": item.get("summary_tokens_est"), "raw_tokens": item.get("raw_tokens_est")})

    content = "\n".join(lines)
    out = latest_context_path(repo_root)
    out.write_text(content, encoding="utf-8")
    raw_total = sum(x.get("raw_tokens", 0) for x in selected)
    compressed_tokens = estimate_tokens(content)
    report = {
        "status": "ok",
        "task": task,
        "max_tokens": max_tokens,
        "selected_files": selected,
        "selected_file_count": len(selected),
        "raw_selected_tokens_est": raw_total,
        "compressed_tokens_est": compressed_tokens,
        "compression_ratio_vs_selected_raw": round(compressed_tokens / raw_total, 4) if raw_total else 0,
        "context_file": str(out),
        "created_at": utcnow(),
    }
    latest_report_path(repo_root).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report["content"] = content
    return report

def compression_report(repo_root: Path) -> dict:
    p = latest_report_path(repo_root)
    cache = load_compression_cache(repo_root)
    raw = sum(v.get("raw_tokens_est", 0) for v in cache.get("files", {}).values())
    summary = sum(v.get("summary_tokens_est", 0) for v in cache.get("files", {}).values())
    base = {"status": "ok", "cache_file_count": len(cache.get("files", {})), "cache_raw_tokens_est": raw, "cache_summary_tokens_est": summary, "cache_compression_ratio": round(summary/raw, 4) if raw else 0}
    if p.exists():
        base["latest_context"] = json.loads(p.read_text(encoding="utf-8"))
    return base
