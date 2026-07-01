from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import html
import http.server
import socketserver
import threading
from uacos.config import uacos_dir

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def _read_json(path: Path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default

def _read_jsonl(path: Path, limit: int = 10000):
    rows = []
    try:
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rows.append(json.loads(line))
    except Exception:
        pass
    return rows[-limit:]

def _count_files(path: Path, pattern: str = "*") -> int:
    try:
        return len(list(path.glob(pattern))) if path.exists() else 0
    except Exception:
        return 0

def metrics_dir(repo_root: Path) -> Path:
    p = uacos_dir(repo_root) / "metrics"
    p.mkdir(parents=True, exist_ok=True)
    return p

def collect_production_metrics(repo_root: Path) -> dict:
    udir = uacos_dir(repo_root)
    graph = _read_json(udir / "graph" / "dependency_graph.json", {})
    budget_report = _read_json(udir / "budget" / "latest_context_budget_report.json", {})
    feedback_scores = _read_json(udir / "skill_feedback_scores.json", {"skills": {}})
    provider_history = _read_jsonl(udir / "llm_provider_history.jsonl")
    openclaw_history = _read_jsonl(udir / "openclaw" / "openclaw_history.jsonl")
    autopilot_runs = []
    ardir = udir / "autopilot_runs"
    if ardir.exists():
        for p in sorted(ardir.glob("AUTO-*.json")):
            autopilot_runs.append(_read_json(p, {}))
    patch_runs = []
    prdir = udir / "patch_runs"
    if prdir.exists():
        for p in sorted(prdir.glob("PATCH-*/manifest.json")):
            patch_runs.append(_read_json(p, {}))
    skill_exec = _read_jsonl(udir / "skill_execution_history.jsonl")
    learning_events = _read_jsonl(udir / "learning_events.jsonl")
    feedback_events = _read_jsonl(udir / "feedback_events.jsonl")
    semantic_index = _read_json(udir / "semantic_index.json", {})

    provider_cost = 0.0
    for row in provider_history:
        provider_cost += float((row.get("estimated_cost") or {}).get("estimated_cost_usd", 0.0))

    def by_status(rows):
        out = {}
        for r in rows:
            st = r.get("status", "unknown")
            out[st] = out.get(st, 0) + 1
        return out

    errors = []
    warnings = []
    if not udir.exists():
        errors.append("uacos_dir_missing")
    if graph and graph.get("stats", {}).get("parse_errors", 0):
        warnings.append("ast_parse_errors_present")
    if provider_history and any(r.get("status") == "error" for r in provider_history):
        warnings.append("llm_provider_errors_present")
    if patch_runs and any(r.get("status") in {"error", "rolled_back", "blocked"} for r in patch_runs):
        warnings.append("patch_issues_present")
    if autopilot_runs and any(r.get("status") in {"error", "blocked", "rolled_back"} for r in autopilot_runs):
        warnings.append("autopilot_issues_present")

    score = 100
    score -= len(errors) * 25
    score -= len(warnings) * 8
    if not graph:
        score -= 5
    if not semantic_index:
        score -= 5
    score = max(0, min(100, score))
    health = "green" if score >= 85 else "yellow" if score >= 60 else "red"

    return {
        "status": "ok",
        "created_at": utcnow(),
        "repo": str(repo_root),
        "health": {"score": score, "level": health, "errors": errors, "warnings": warnings},
        "counts": {
            "graph_files": len(graph.get("files", [])) if graph else 0,
            "graph_symbols": graph.get("stats", {}).get("symbol_count", 0) if graph else 0,
            "graph_calls": graph.get("stats", {}).get("call_edge_count", 0) if graph else 0,
            "semantic_docs": semantic_index.get("doc_count", 0) if semantic_index else 0,
            "autopilot_runs": len(autopilot_runs),
            "patch_runs": len(patch_runs),
            "skill_executions": len(skill_exec),
            "learning_events": len(learning_events),
            "feedback_events": len(feedback_events),
            "tracked_skill_feedback": len(feedback_scores.get("skills", {})),
            "provider_runs": len(provider_history),
            "openclaw_runs": len(openclaw_history),
            "budget_selected_files": budget_report.get("selected_file_count", 0) if budget_report else 0,
        },
        "statuses": {
            "autopilot": by_status(autopilot_runs),
            "patch": by_status(patch_runs),
            "skill_execution": by_status(skill_exec),
            "openclaw": by_status(openclaw_history),
            "provider": by_status(provider_history),
        },
        "cost": {
            "provider_estimated_cost_usd": round(provider_cost, 8),
        },
        "latest": {
            "budget_report": budget_report,
            "recent_autopilot": autopilot_runs[-5:],
            "recent_patch": patch_runs[-5:],
            "recent_provider": provider_history[-5:],
            "recent_openclaw": openclaw_history[-5:],
            "recent_feedback": feedback_events[-5:],
        },
    }

def write_metrics_report(repo_root: Path) -> dict:
    metrics = collect_production_metrics(repo_root)
    out = metrics_dir(repo_root) / "production_metrics.json"
    out.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "ok", "report": str(out), "metrics": metrics}

def render_html(metrics: dict) -> str:
    h = html.escape
    counts = metrics.get("counts", {})
    statuses = metrics.get("statuses", {})
    health = metrics.get("health", {})
    rows = "".join(f"<tr><td>{h(str(k))}</td><td>{h(str(v))}</td></tr>" for k, v in counts.items())
    status_blocks = ""
    for name, data in statuses.items():
        items = "".join(f"<li>{h(str(k))}: {h(str(v))}</li>" for k, v in data.items())
        status_blocks += f"<h3>{h(name)}</h3><ul>{items}</ul>"
    latest_json = h(json.dumps(metrics.get("latest", {}), ensure_ascii=False, indent=2)[:12000])
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>UACOS Production Dashboard</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 24px; background: #0b1020; color: #e8eefc; }}
.card {{ background: #141b34; border: 1px solid #27325a; border-radius: 12px; padding: 16px; margin: 14px 0; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ border-bottom: 1px solid #27325a; padding: 8px; text-align: left; }}
.badge {{ display: inline-block; padding: 6px 10px; border-radius: 999px; background: #25345f; }}
pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #090d1a; padding: 12px; border-radius: 8px; }}
</style>
</head>
<body>
<h1>UACOS Production Dashboard</h1>
<div class="card">
<h2>Health <span class="badge">{h(str(health.get("level")))}</span></h2>
<p>Score: {h(str(health.get("score")))}</p>
<p>Warnings: {h(", ".join(health.get("warnings", [])))}</p>
<p>Errors: {h(", ".join(health.get("errors", [])))}</p>
</div>
<div class="card">
<h2>Counts</h2>
<table><tbody>{rows}</tbody></table>
</div>
<div class="card">
<h2>Statuses</h2>
{status_blocks}
</div>
<div class="card">
<h2>Latest</h2>
<pre>{latest_json}</pre>
</div>
</body>
</html>"""

def write_html_dashboard(repo_root: Path) -> dict:
    metrics = collect_production_metrics(repo_root)
    html_text = render_html(metrics)
    out = metrics_dir(repo_root) / "production_dashboard.html"
    out.write_text(html_text, encoding="utf-8")
    return {"status": "ok", "dashboard": str(out), "health": metrics.get("health")}

def production_doctor(repo_root: Path) -> dict:
    report = write_metrics_report(repo_root)
    html_report = write_html_dashboard(repo_root)
    metrics = report["metrics"]
    checks = []
    checks.append({"name": "uacos_dir", "status": "pass" if uacos_dir(repo_root).exists() else "fail"})
    checks.append({"name": "health_score", "status": "pass" if metrics["health"]["score"] >= 60 else "fail", "score": metrics["health"]["score"]})
    checks.append({"name": "metrics_report", "status": "pass", "path": report["report"]})
    checks.append({"name": "html_dashboard", "status": "pass", "path": html_report["dashboard"]})
    return {"status": "pass" if all(c["status"] == "pass" for c in checks) else "fail", "checks": checks, "health": metrics["health"], "report": report["report"], "dashboard": html_report["dashboard"]}

def serve_dashboard(repo_root: Path, host: str = "127.0.0.1", port: int = 8787) -> dict:
    write_html_dashboard(repo_root)
    directory = metrics_dir(repo_root)
    handler = http.server.SimpleHTTPRequestHandler
    class Handler(handler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)
    with socketserver.TCPServer((host, port), Handler) as httpd:
        print(f"UACOS production dashboard: http://{host}:{port}/production_dashboard.html")
        httpd.serve_forever()
