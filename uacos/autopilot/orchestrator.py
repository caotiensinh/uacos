from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json, uuid, traceback

from uacos.config import uacos_dir
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.agent.registry import init_agent_registry
from uacos.agent.adapter_config import init_adapter_config
from uacos.agent.task import create_task, load_task
from uacos.agent.real_adapters import run_named_adapter
from uacos.retrieval.context_pack import build_context_pack
from uacos.execution.artifacts import ingest_agent_output
from uacos.apply.patch_apply import apply_patch_with_backup, done_gate
from uacos.memory.regression import regression_check_patch
from uacos.semantic.search import build_semantic_index
from uacos.learning.auto import learn_from_file, learn_from_manifest
from uacos.dashboard.ops_summary import ops_summary

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def new_run_id() -> str:
    return "AUTO-" + uuid.uuid4().hex[:12]

def autopilot_config_path(repo_root: Path) -> Path:
    p = uacos_dir(repo_root)
    p.mkdir(parents=True, exist_ok=True)
    return p / "autopilot.json"

def autopilot_runs_dir(repo_root: Path) -> Path:
    p = uacos_dir(repo_root) / "autopilot_runs"
    p.mkdir(parents=True, exist_ok=True)
    return p

DEFAULT_AUTOPILOT_CONFIG = {
    "version": 1,
    "default_adapter": "manual_chat",
    "safe_mode": True,
    "auto_apply_default": False,
    "auto_learn_default": True,
    "auto_approve_learning_default": False,
    "require_done_gate": True,
    "build_semantic_index": True,
    "scan_before_run": True
}

def init_autopilot(repo_root: Path) -> dict:
    init_storage(repo_root)
    init_agent_registry(repo_root)
    init_adapter_config(repo_root)
    path = autopilot_config_path(repo_root)
    if not path.exists():
        path.write_text(json.dumps(DEFAULT_AUTOPILOT_CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "ok", "config": str(path), "config_data": json.loads(path.read_text(encoding="utf-8"))}

def load_autopilot_config(repo_root: Path) -> dict:
    path = autopilot_config_path(repo_root)
    if not path.exists():
        init_autopilot(repo_root)
    return json.loads(path.read_text(encoding="utf-8"))

def save_run(repo_root: Path, run: dict) -> dict:
    path = autopilot_runs_dir(repo_root) / f"{run['id']}.json"
    path.write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")
    run["run_file"] = str(path)
    return run

def autopilot_plan(repo_root: Path, title: str, objective: str, allowed_files=None, allowed_dirs=None, tests=None, commands=None, risk_level: str = "normal") -> dict:
    init_autopilot(repo_root)
    task_file = create_task(repo_root, title=title, objective=objective, allowed_files=allowed_files or [], allowed_dirs=allowed_dirs or [], tests=tests or [], commands=commands or [], risk_level=risk_level)
    context = build_context_pack(repo_root, objective, max_tokens=4500, search_limit=10)
    return {
        "status": "ok",
        "task_file": str(task_file),
        "title": title,
        "objective": objective,
        "context_id": context["id"],
        "context_token_count": context["token_count"],
        "gates": ["semantic_index", "context_pack", "adapter", "artifact_ingest", "regression_check", "apply_patch", "done_gate", "auto_learning"],
        "created_at": utcnow(),
    }

def _safe_step(run: dict, name: str, fn):
    try:
        result = fn()
        run["steps"].append({"name": name, "status": "ok", "result": result})
        return result
    except Exception as exc:
        run["steps"].append({"name": name, "status": "error", "error": {"type": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()}})
        run["status"] = "error"
        return None

def autopilot_run(repo_root: Path, task_file: Path, adapter: str | None = None, agent_output: Path | None = None, patch_file: Path | None = None, apply_changes: bool = False, auto_learn: bool | None = None, auto_approve_learning: bool | None = None) -> dict:
    config = load_autopilot_config(repo_root)
    adapter = adapter or config.get("default_adapter", "manual_chat")
    if auto_learn is None:
        auto_learn = bool(config.get("auto_learn_default", True))
    if auto_approve_learning is None:
        auto_approve_learning = bool(config.get("auto_approve_learning_default", False))

    task = load_task(task_file)
    run = {"id": new_run_id(), "status": "started", "repo": str(repo_root), "task_file": str(task_file), "task_id": task["id"], "task_title": task.get("title"), "adapter": adapter, "apply_requested": apply_changes, "auto_learn": auto_learn, "steps": [], "created_at": utcnow()}

    _safe_step(run, "bootstrap_scan", lambda: scan_repo(repo_root) if config.get("scan_before_run", True) else {"scan": "skipped"})
    if run["status"] == "error": return save_run(repo_root, run)
    if config.get("build_semantic_index", True):
        _safe_step(run, "semantic_index", lambda: build_semantic_index(repo_root))
        if run["status"] == "error": return save_run(repo_root, run)

    context = _safe_step(run, "context_pack", lambda: build_context_pack(repo_root, task.get("objective", ""), max_tokens=4500, search_limit=10))
    if run["status"] == "error": return save_run(repo_root, run)

    adapter_result = _safe_step(run, "adapter", lambda: run_named_adapter(repo_root, adapter, task_file, None))
    if run["status"] == "error": return save_run(repo_root, run)

    artifact = None
    extracted_patch = patch_file
    if agent_output:
        artifact = _safe_step(run, "artifact_ingest", lambda: ingest_agent_output(repo_root, task_file, agent_output))
        if artifact and artifact.get("diff_file"):
            extracted_patch = Path(artifact["diff_file"])
        if run["status"] == "error": return save_run(repo_root, run)

    regression = None
    if extracted_patch:
        regression = _safe_step(run, "regression_check", lambda: regression_check_patch(repo_root, extracted_patch))
        if run["status"] == "error": return save_run(repo_root, run)

    manifest = None
    gate = None
    if apply_changes and extracted_patch:
        manifest = _safe_step(run, "apply_patch", lambda: apply_patch_with_backup(repo_root, task_file, extracted_patch))
        if manifest and manifest.get("manifest_file"):
            gate = _safe_step(run, "done_gate", lambda: done_gate(repo_root, Path(manifest["manifest_file"])))
        if run["status"] == "error": return save_run(repo_root, run)
    elif apply_changes and not extracted_patch:
        run["steps"].append({"name": "apply_patch", "status": "blocked", "reason": "apply requested but no patch/diff provided"})
        run["status"] = "blocked"
        return save_run(repo_root, run)

    learning = None
    if auto_learn:
        if manifest and manifest.get("manifest_file"):
            learning = _safe_step(run, "learn_from_manifest", lambda: learn_from_manifest(repo_root, Path(manifest["manifest_file"]), auto_approve=auto_approve_learning))
        elif agent_output:
            learning = _safe_step(run, "learn_from_agent_output", lambda: learn_from_file(repo_root, agent_output, title=f"Learn from {task.get('title', task['id'])}", auto_approve=auto_approve_learning))

    final = "ready_for_agent"
    if agent_output and artifact and artifact.get("status") == "pass":
        final = "validated_agent_output"
    if gate and gate.get("status") == "done":
        final = "done"
    if manifest and manifest.get("status") == "rolled_back":
        final = "rolled_back"
    if any(s.get("status") in {"error", "blocked"} for s in run["steps"]):
        final = "blocked"

    run["status"] = final
    run["summary"] = {
        "context_id": context.get("id") if context else None,
        "adapter_status": adapter_result.get("status") if adapter_result else None,
        "artifact_status": artifact.get("status") if artifact else None,
        "regression_status": regression.get("status") if regression else None,
        "manifest_status": manifest.get("status") if manifest else None,
        "done_gate": gate.get("status") if gate else None,
        "learning_skill_id": (learning.get("skill", {}) or {}).get("id") if learning else None,
    }
    run["ops_summary"] = ops_summary(repo_root)
    return save_run(repo_root, run)

LOOPABLE_ADAPTERS = {"openclaw_cli", "aider_cli", "ollama_openai"}

def autopilot_loop(repo_root: Path, title: str, objective: str, max_iterations: int = 3, adapter: str | None = None, allowed_files=None, allowed_dirs=None, tests=None, commands=None, risk_level: str = "normal", auto_learn: bool | None = None, auto_approve_learning: bool | None = None) -> dict:
    config = load_autopilot_config(repo_root)
    adapter = adapter or config.get("default_adapter", "manual_chat")
    if adapter not in LOOPABLE_ADAPTERS:
        return {
            "status": "blocked",
            "reason": "adapter_cannot_loop_unattended",
            "adapter": adapter,
            "hint": f"autopilot-loop needs an adapter that runs without a human in the loop ({sorted(LOOPABLE_ADAPTERS)}); use autopilot-plan + autopilot-run for a manual pass with '{adapter}'",
        }
    if max_iterations < 1:
        return {"status": "blocked", "reason": "max_iterations_must_be_at_least_1"}

    plan = autopilot_plan(repo_root, title, objective, allowed_files=allowed_files, allowed_dirs=allowed_dirs, tests=tests, commands=commands, risk_level=risk_level)
    task_file = Path(plan["task_file"])

    attempts = []
    final_run = None
    for i in range(1, max_iterations + 1):
        run = autopilot_run(repo_root, task_file, adapter=adapter, apply_changes=True, auto_learn=auto_learn, auto_approve_learning=auto_approve_learning)
        attempts.append({"iteration": i, "run_id": run.get("id"), "status": run.get("status")})
        final_run = run
        if run.get("status") == "done":
            break

    succeeded = bool(final_run and final_run.get("status") == "done")
    return {
        "status": "done" if succeeded else "exhausted",
        "title": title,
        "objective": objective,
        "adapter": adapter,
        "max_iterations": max_iterations,
        "iterations_used": len(attempts),
        "attempts": attempts,
        "task_file": str(task_file),
        "final_run_id": final_run.get("id") if final_run else None,
        "final_run_status": final_run.get("status") if final_run else None,
        "created_at": utcnow(),
    }

def list_autopilot_runs(repo_root: Path) -> dict:
    d = autopilot_runs_dir(repo_root)
    rows = []
    for p in sorted(d.glob("AUTO-*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            rows.append({"id": data.get("id"), "status": data.get("status"), "task_id": data.get("task_id"), "task_title": data.get("task_title"), "created_at": data.get("created_at"), "run_file": str(p)})
        except Exception as exc:
            rows.append({"run_file": str(p), "error": str(exc)})
    return {"status": "ok", "count": len(rows), "runs": rows}

def load_autopilot_run(repo_root: Path, run_id: str) -> dict:
    return json.loads((autopilot_runs_dir(repo_root) / f"{run_id}.json").read_text(encoding="utf-8"))

def autopilot_report_markdown(repo_root: Path, run_id: str) -> str:
    run = load_autopilot_run(repo_root, run_id)
    lines = [f"# UACOS Autopilot Report — {run_id}", "", f"Status: **{run.get('status')}**", f"Task: {run.get('task_title')} (`{run.get('task_id')}`)", f"Adapter: `{run.get('adapter')}`", "", "## Summary"]
    for k, v in (run.get("summary") or {}).items():
        lines.append(f"- {k}: `{v}`")
    lines.append("")
    lines.append("## Steps")
    for s in run.get("steps", []):
        lines.append(f"- {s.get('name')}: **{s.get('status')}**")
    return "\n".join(lines) + "\n"
