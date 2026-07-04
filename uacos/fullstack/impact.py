from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import re
import ast

from uacos.config import uacos_dir
from uacos.graph.builder import build_graph, load_graph
from uacos.ast_engine.js_parser import parse_repo_js_ts
from uacos.llm.hardened import estimate_tokens
from uacos.impact.analyzer import impact_by_task
from uacos.compression.engine import build_summary_cache, load_compression_cache

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def fullstack_dir(repo_root: Path) -> Path:
    p = uacos_dir(repo_root) / "fullstack"
    p.mkdir(parents=True, exist_ok=True)
    return p

def latest_index_path(repo_root: Path) -> Path:
    return fullstack_dir(repo_root) / "fullstack_index.json"

def latest_context_path(repo_root: Path) -> Path:
    return fullstack_dir(repo_root) / "latest_fullstack_context.md"

def _norm_ep(ep: str) -> str:
    ep = ep.strip()
    ep = re.sub(r"\{[^}]+\}", "{var}", ep)
    ep = re.sub(r"<[^>]+>", "{var}", ep)
    ep = re.sub(r":[A-Za-z_][\w]*", "{var}", ep)
    ep = re.sub(r"/+", "/", ep)
    if ep != "/" and ep.endswith("/"):
        ep = ep[:-1]
    return ep

def _python_routes(path: Path, repo_root: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    rel = str(path.relative_to(repo_root)).replace("\\", "/")
    routes = []
    # FastAPI decorators: @app.get("/api/x"), @router.post("/api/x")
    pattern = re.compile(r"""(?m)^\s*@(?:app|router|api|bp)\.(get|post|put|delete|patch)\s*\(\s*['"]([^'"]+)['"]""")
    for m in pattern.finditer(text):
        routes.append({"method": m.group(1).upper(), "endpoint": _norm_ep(m.group(2)), "file": rel, "lineno": text[:m.start()].count("\n") + 1})
    return routes

def build_fullstack_index(repo_root: Path) -> dict:
    build_graph(repo_root)
    py_graph = load_graph(repo_root)
    js_docs = parse_repo_js_ts(repo_root)
    py_routes = []
    for p in repo_root.rglob("*.py"):
        if ".uacos" in p.parts or "__pycache__" in p.parts or ".venv" in p.parts:
            continue
        py_routes.extend(_python_routes(p, repo_root))
    frontend_api_calls = []
    for d in js_docs:
        for call in d.get("api_calls", []):
            frontend_api_calls.append({"file": d["path"], "endpoint": _norm_ep(call["endpoint"]), "lineno": call.get("lineno"), "kind": call.get("kind")})
    links = []
    for route in py_routes:
        for call in frontend_api_calls:
            if route["endpoint"] == call["endpoint"] or route["endpoint"].replace("{var}", "") in call["endpoint"]:
                links.append({"backend_file": route["file"], "frontend_file": call["file"], "endpoint": route["endpoint"], "method": route["method"], "route_lineno": route["lineno"], "call_lineno": call["lineno"]})
    index = {
        "status": "ok",
        "created_at": utcnow(),
        "python": {"graph_stats": py_graph.get("stats", {}), "routes": py_routes},
        "javascript": {"file_count": len(js_docs), "files": js_docs, "api_calls": frontend_api_calls},
        "links": links,
        "stats": {
            "python_routes": len(py_routes),
            "js_files": len(js_docs),
            "frontend_api_calls": len(frontend_api_calls),
            "backend_frontend_links": len(links),
        }
    }
    latest_index_path(repo_root).write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    return index

def load_fullstack_index(repo_root: Path, auto_build: bool = True) -> dict:
    p = latest_index_path(repo_root)
    if not p.exists():
        if not auto_build:
            raise FileNotFoundError(str(p))
        return build_fullstack_index(repo_root)
    return json.loads(p.read_text(encoding="utf-8"))

def fullstack_impact(repo_root: Path, task: str, limit: int = 12) -> dict:
    index = build_fullstack_index(repo_root)
    py_impact = impact_by_task(repo_root, task, limit=limit)
    scores = {}
    reasons = {}
    def add(file, score, reason):
        if not file:
            return
        scores[file] = max(scores.get(file, 0.0), score)
        reasons.setdefault(file, []).append(reason)
    for row in py_impact.get("impacted_files", []):
        add(row["file"], float(row.get("score", 0)), "python_impact")
    low = task.lower()
    tokens = [t for t in re.findall(r"[A-Za-z0-9_/-]+", low) if len(t) >= 3]
    for d in index["javascript"]["files"]:
        fscore = 0.0
        matched_reasons = []
        for t in tokens:
            if t in d["path"].lower():
                fscore += 0.4
                matched_reasons.append(f"js_path_match:{t}")
            if any(t in (fn.get("name", "").lower()) for fn in d.get("functions", [])):
                fscore += 0.5
                matched_reasons.append(f"js_function_name:{t}")
            if any(t in c.get("endpoint", "").lower() for c in d.get("api_calls", [])):
                fscore += 0.9
                matched_reasons.append(f"js_api_endpoint:{t}")
        if fscore:
            for reason in matched_reasons:
                add(d["path"], fscore, reason)
    # Cross-link backend impact -> frontend files
    for link in index.get("links", []):
        if link["backend_file"] in scores:
            add(link["frontend_file"], scores[link["backend_file"]] * 0.85, f"frontend_calls:{link['endpoint']}")
        if link["frontend_file"] in scores:
            add(link["backend_file"], scores[link["frontend_file"]] * 0.85, f"backend_route:{link['endpoint']}")
    ranked = [{"file": f, "score": round(s, 4), "reasons": reasons.get(f, [])} for f, s in scores.items()]
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return {"status": "ok", "task": task, "stats": index["stats"], "impacted_files": ranked[:limit], "links": index.get("links", [])}

def fullstack_context(repo_root: Path, task: str, max_tokens: int = 8000, limit: int = 10) -> dict:
    impact = fullstack_impact(repo_root, task, limit=limit)
    build_summary_cache(repo_root)
    cache = load_compression_cache(repo_root)
    lines = ["# UACOS Full-stack Context", "", f"Task: {task}", "", "## Full-stack Links"]
    for link in impact.get("links", [])[:30]:
        lines.append(f"- {link['method']} {link['endpoint']}: `{link['backend_file']}` ↔ `{link['frontend_file']}`")
    lines.append("")
    lines.append("## Impact Ranking")
    selected = []
    for row in impact["impacted_files"]:
        rel = row["file"]
        item = cache.get("files", {}).get(rel)
        path = repo_root / rel
        if item:
            summary = item.get("summary", "")
        elif path.exists():
            summary = path.read_text(encoding="utf-8", errors="replace")[:3000]
        else:
            continue
        chunk = f"### {rel}\n- score: {row['score']}\n- reasons: {', '.join(row.get('reasons', []))}\n```text\n{summary[:3500]}\n```\n"
        if estimate_tokens("\n".join(lines) + "\n" + chunk) > max_tokens:
            continue
        lines.append(chunk)
        selected.append(row)
    content = "\n".join(lines)
    out = latest_context_path(repo_root)
    out.write_text(content, encoding="utf-8")
    return {"status": "ok", "task": task, "selected_files": selected, "selected_file_count": len(selected), "tokens_est": estimate_tokens(content), "context_file": str(out), "content": content}
