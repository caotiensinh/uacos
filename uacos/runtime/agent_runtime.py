from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import uuid
import re
import time

from uacos.config import uacos_dir
from uacos.compression.engine import compressed_context
from uacos.llm.hardened import run_llm_hardened
from uacos.adapters.openclaw import run_openclaw
from uacos.patching.engine import parse_unified_diff
from uacos.transaction.engine import run_transaction

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def new_job_id() -> str:
    return "JOB-" + uuid.uuid4().hex[:12]

def runtime_dir(repo_root: Path) -> Path:
    p = uacos_dir(repo_root) / "runtime"
    p.mkdir(parents=True, exist_ok=True)
    (p / "jobs").mkdir(exist_ok=True)
    return p

def runtime_config_path(repo_root: Path) -> Path:
    return runtime_dir(repo_root) / "runtime_config.json"

def job_path(repo_root: Path, job_id: str) -> Path:
    return runtime_dir(repo_root) / "jobs" / f"{job_id}.json"

def history_path(repo_root: Path) -> Path:
    return runtime_dir(repo_root) / "runtime_history.jsonl"

DEFAULT_CONFIG = {
    "version": 1,
    "mode": "dry_run",
    "default_backend": "manual",
    "provider": "dry_run",
    "openclaw_agent": "leader",
    "max_context_tokens": 6000,
    "max_context_files": 8,
    "require_transaction": True,
    "auto_apply_patch": False,
    "allowed_real_run": False,
    "job_lock_timeout_sec": 600
}

def init_runtime(repo_root: Path) -> dict:
    path = runtime_config_path(repo_root)
    if not path.exists():
        path.write_text(json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "ok", "config": str(path), "config_data": json.loads(path.read_text(encoding="utf-8"))}

def load_runtime_config(repo_root: Path) -> dict:
    path = runtime_config_path(repo_root)
    if not path.exists():
        init_runtime(repo_root)
    return json.loads(path.read_text(encoding="utf-8"))

def save_runtime_config(repo_root: Path, cfg: dict) -> dict:
    path = runtime_config_path(repo_root)
    path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "ok", "config": str(path)}

def configure_runtime(repo_root: Path, **kwargs) -> dict:
    cfg = load_runtime_config(repo_root)
    for k, v in kwargs.items():
        if v is not None:
            cfg[k] = v
    save_runtime_config(repo_root, cfg)
    return {"status": "ok", "config_data": cfg, "validation": validate_runtime(repo_root)}

def validate_runtime(repo_root: Path) -> dict:
    cfg = load_runtime_config(repo_root)
    findings = []
    if cfg.get("mode") not in {"dry_run", "real"}:
        findings.append({"severity": "error", "reason": "invalid_mode"})
    if cfg.get("default_backend") not in {"manual", "provider", "openclaw"}:
        findings.append({"severity": "error", "reason": "invalid_backend"})
    if int(cfg.get("max_context_tokens", 0)) < 1000:
        findings.append({"severity": "warning", "reason": "context_budget_low"})
    if cfg.get("mode") == "real" and not cfg.get("allowed_real_run"):
        findings.append({"severity": "error", "reason": "real_mode_requires_allowed_real_run"})
    return {"status": "pass" if not any(f["severity"] == "error" for f in findings) else "fail", "findings": findings, "config": cfg}

def _append_history(repo_root: Path, row: dict) -> None:
    row = dict(row)
    row.setdefault("ts", utcnow())
    with history_path(repo_root).open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def read_history(repo_root: Path, limit: int = 100) -> list[dict]:
    p = history_path(repo_root)
    if not p.exists():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows[-limit:]

def create_job(repo_root: Path, task: str, backend: str | None = None, allowed_files: list[str] | None = None, allowed_dirs: list[str] | None = None, tests: list[str] | None = None, auto_apply: bool | None = None) -> dict:
    cfg = load_runtime_config(repo_root)
    job_id = new_job_id()
    job = {
        "id": job_id,
        "status": "queued",
        "task": task,
        "backend": backend or cfg.get("default_backend", "manual"),
        "allowed_files": allowed_files or [],
        "allowed_dirs": allowed_dirs or [],
        "tests": tests or [],
        "auto_apply": cfg.get("auto_apply_patch", False) if auto_apply is None else bool(auto_apply),
        "created_at": utcnow(),
        "updated_at": utcnow(),
        "events": [{"ts": utcnow(), "event": "queued"}],
    }
    job_path(repo_root, job_id).write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
    _append_history(repo_root, {"event": "job_created", "job_id": job_id, "status": "queued", "backend": job["backend"]})
    return job

def load_job(repo_root: Path, job_id: str) -> dict:
    return json.loads(job_path(repo_root, job_id).read_text(encoding="utf-8"))

def save_job(repo_root: Path, job: dict) -> dict:
    job["updated_at"] = utcnow()
    job_path(repo_root, job["id"]).write_text(json.dumps(job, ensure_ascii=False, indent=2), encoding="utf-8")
    return job

def _event(job: dict, name: str, data: dict | None = None):
    job.setdefault("events", []).append({"ts": utcnow(), "event": name, "data": data or {}})

def list_jobs(repo_root: Path) -> dict:
    rows = []
    for p in sorted((runtime_dir(repo_root) / "jobs").glob("JOB-*.json")):
        try:
            j = json.loads(p.read_text(encoding="utf-8"))
            rows.append({"id": j.get("id"), "status": j.get("status"), "backend": j.get("backend"), "task": j.get("task"), "updated_at": j.get("updated_at"), "job_file": str(p)})
        except Exception as exc:
            rows.append({"job_file": str(p), "error": str(exc)})
    return {"status": "ok", "count": len(rows), "jobs": rows}

def next_queued_job(repo_root: Path) -> dict | None:
    jobs = list_jobs(repo_root)["jobs"]
    for j in jobs:
        if j.get("status") == "queued":
            return load_job(repo_root, j["id"])
    return None

def _extract_diff(text: str) -> str | None:
    if not text:
        return None
    m = re.search(r"```(?:diff)?\s*(diff --git .*?)```", text, flags=re.S)
    if m:
        return m.group(1).strip() + "\n"
    idx = text.find("diff --git ")
    if idx >= 0:
        return text[idx:].strip() + "\n"
    return None

def _build_runtime_prompt(job: dict, context: str) -> str:
    return f"""UACOS TRUE AGENT RUNTIME JOB

Job: {job['id']}
Task:
{job['task']}

Rules:
- Return a unified diff if code changes are required.
- Keep changes within allowed files/dirs.
- Explain tests/evidence briefly.
- Do not claim done without evidence.

Allowed files: {job.get('allowed_files', [])}
Allowed dirs: {job.get('allowed_dirs', [])}
Tests: {job.get('tests', [])}

Context:
{context}
"""

def run_job_once(repo_root: Path, job_id: str | None = None, real: bool = False) -> dict:
    cfg = load_runtime_config(repo_root)
    validation = validate_runtime(repo_root)
    if validation["status"] != "pass":
        return {"status": "blocked", "reason": "runtime_validation_failed", "validation": validation}
    if real and not cfg.get("allowed_real_run"):
        return {"status": "blocked", "reason": "allowed_real_run_false"}

    job = load_job(repo_root, job_id) if job_id else next_queued_job(repo_root)
    if not job:
        return {"status": "idle", "reason": "no_queued_jobs"}

    job["status"] = "running"
    _event(job, "started", {"real": real})
    save_job(repo_root, job)

    try:
        ctx = compressed_context(repo_root, job["task"], max_tokens=int(cfg.get("max_context_tokens", 6000)), max_files=int(cfg.get("max_context_files", 8)))
        prompt = _build_runtime_prompt(job, ctx["content"])
        prompt_file = runtime_dir(repo_root) / f"{job['id']}_prompt.md"
        prompt_file.write_text(prompt, encoding="utf-8")
        job["prompt_file"] = str(prompt_file)
        job["context_file"] = ctx["context_file"]
        _event(job, "context_prepared", {"tokens": ctx.get("compressed_tokens_est"), "files": ctx.get("selected_file_count")})

        backend = job.get("backend") or cfg.get("default_backend", "manual")
        output = ""
        backend_result = None
        if backend == "manual":
            backend_result = {"status": "manual_waiting", "prompt_file": str(prompt_file)}
            job["status"] = "waiting_manual"
            _event(job, "manual_prompt_ready", backend_result)
        elif backend == "provider":
            backend_result = run_llm_hardened(repo_root, prompt, provider=cfg.get("provider"), task=job["task"], dry_run=not real)
            output = ((backend_result.get("result") or {}).get("content") or "")
            _event(job, "provider_completed", {"status": backend_result.get("status")})
        elif backend == "openclaw":
            backend_result = run_openclaw(repo_root, job["task"], agent=cfg.get("openclaw_agent"), real=real)
            out_file = backend_result.get("output_file")
            if out_file and Path(out_file).exists():
                output = Path(out_file).read_text(encoding="utf-8", errors="replace")
            _event(job, "openclaw_completed", {"status": backend_result.get("status")})
        else:
            raise ValueError(f"unsupported_backend:{backend}")

        job["backend_result"] = backend_result

        diff = _extract_diff(output)
        if diff:
            diff_file = runtime_dir(repo_root) / f"{job['id']}.diff"
            diff_file.write_text(diff, encoding="utf-8")
            job["diff_file"] = str(diff_file)
            _event(job, "diff_extracted", {"diff_file": str(diff_file), "file_count": len(parse_unified_diff(diff))})
            if job.get("auto_apply"):
                tx = run_transaction(repo_root, diff_file, title=f"Runtime job {job['id']}", objective=job["task"], allowed_files=job.get("allowed_files", []), allowed_dirs=job.get("allowed_dirs", []), tests=job.get("tests", []))
                job["transaction"] = tx
                job["status"] = "done" if tx.get("status") == "committed" else tx.get("status", "failed")
                _event(job, "transaction_completed", {"status": tx.get("status"), "tx_id": tx.get("id")})
            else:
                job["status"] = "diff_ready"
                _event(job, "awaiting_apply", {})
        elif job["status"] == "waiting_manual":
            pass
        else:
            job["status"] = "completed_no_diff"
            _event(job, "completed_no_diff", {})
    except Exception as exc:
        job["status"] = "error"
        job["error"] = {"type": type(exc).__name__, "message": str(exc)}
        _event(job, "error", job["error"])

    save_job(repo_root, job)
    _append_history(repo_root, {"event": "job_finished", "job_id": job["id"], "status": job["status"], "backend": job.get("backend")})
    return job

def runtime_status(repo_root: Path) -> dict:
    jobs = list_jobs(repo_root)
    by_status = {}
    for j in jobs["jobs"]:
        st = j.get("status", "unknown")
        by_status[st] = by_status.get(st, 0) + 1
    return {"status": "ok", "validation": validate_runtime(repo_root), "jobs": jobs["count"], "by_status": by_status, "recent_history": read_history(repo_root, limit=20)}

def job_report(repo_root: Path, job_id: str) -> str:
    job = load_job(repo_root, job_id)
    lines = [f"# UACOS Runtime Job Report — {job_id}", "", f"Status: **{job.get('status')}**", f"Backend: `{job.get('backend')}`", "", "## Task", job.get("task", ""), "", "## Files"]
    for k in ["prompt_file", "context_file", "diff_file"]:
        if job.get(k):
            lines.append(f"- {k}: `{job[k]}`")
    if job.get("transaction"):
        lines.append(f"- transaction: `{job['transaction'].get('id')}` status={job['transaction'].get('status')}")
    lines.append("")
    lines.append("## Events")
    for e in job.get("events", []):
        lines.append(f"- {e.get('ts')} — {e.get('event')}")
    return "\n".join(lines) + "\n"
