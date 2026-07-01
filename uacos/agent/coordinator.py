from __future__ import annotations

from pathlib import Path
from uacos.config import uacos_dir
from uacos.agent.models import Assignment, WorkflowPlan, new_id, dataclass_to_dict, save_json, load_json, utcnow
from uacos.agent.registry import select_agent
from uacos.agent.task import load_task
from uacos.retrieval.context_pack import build_context_pack
from uacos.security.command_policy import check_command
from uacos.security.patch_gate import validate_patch_file
from uacos.agent.adapters import get_adapter

def plans_dir(repo_root: Path) -> Path:
    return uacos_dir(repo_root) / "plans"

def runs_dir(repo_root: Path) -> Path:
    return uacos_dir(repo_root) / "runs"

def create_plan(repo_root: Path, task_file: Path) -> Path:
    task = load_task(task_file)
    assignments = []
    for role, resp in [
        ("planner", "Confirm scope, context, and safe execution order."),
        ("coder", "Prepare implementation patch within allowed scope."),
        ("reviewer", "Review patch for security, scope, and regression risk."),
        ("tester", "Run approved tests and collect evidence."),
    ]:
        agent = select_agent(repo_root, role)
        if agent:
            assignments.append(Assignment(agent=agent["name"], role=role, responsibility=resp))

    plan = WorkflowPlan(
        id=new_id("PLAN"),
        task_id=task["id"],
        assignments=assignments,
        gates=[
            "context_pack_required",
            "command_allowlist_required",
            "patch_scope_check_required",
            "evidence_report_required",
        ],
    )
    path = plans_dir(repo_root) / f"{plan.id}.json"
    save_json(path, dataclass_to_dict(plan))
    return path

def preflight_task(repo_root: Path, task: dict) -> dict:
    findings = []
    for cmd in task.get("tests", []) + task.get("commands", []):
        result = check_command(cmd)
        if not result["allowed"]:
            findings.append({"type": "command_blocked", "command": cmd, "reason": result["reason"]})

    for f in task.get("forbidden_files", []):
        if f in task.get("allowed_files", []):
            findings.append({"type": "scope_conflict", "path": f, "reason": "file both allowed and forbidden"})

    return {
        "status": "fail" if findings else "pass",
        "findings": findings,
    }

def run_workflow(repo_root: Path, task_file: Path, patch_file: Path | None = None) -> dict:
    task = load_task(task_file)
    preflight = preflight_task(repo_root, task)
    context_pack = build_context_pack(repo_root, task["objective"], max_tokens=3500, search_limit=8)

    plan_file = create_plan(repo_root, task_file)
    plan = load_json(plan_file)

    steps = []
    for assignment in plan["assignments"]:
        agent = select_agent(repo_root, assignment["role"])
        if not agent:
            steps.append({"role": assignment["role"], "status": "skipped", "reason": "no_agent"})
            continue
        adapter = get_adapter(agent.get("adapter", "dry_run"))
        step = adapter.run(repo_root, agent, task, context_pack, assignment["role"])
        steps.append(step)

    patch_check = None
    if patch_file:
        patch_check = validate_patch_file(
            patch_file,
            allowed_files=task.get("allowed_files", []),
            allowed_dirs=task.get("allowed_dirs", []),
        )

    status = "pass"
    if preflight["status"] != "pass":
        status = "fail"
    if patch_check and patch_check["status"] != "pass":
        status = "fail"
    if any(s.get("status") not in {"ok", "skipped"} for s in steps):
        status = "fail"

    run = {
        "id": new_id("RUN"),
        "task": task,
        "plan_file": str(plan_file),
        "context_id": context_pack["id"],
        "context_token_count": context_pack["token_count"],
        "preflight": preflight,
        "patch_check": patch_check,
        "steps": steps,
        "status": status,
        "created_at": utcnow(),
    }
    path = runs_dir(repo_root) / f"{run['id']}.json"
    save_json(path, run)
    run["run_file"] = str(path)
    return run

def load_run(repo_root: Path, run_id: str) -> dict:
    path = runs_dir(repo_root) / f"{run_id}.json"
    return load_json(path)

def evidence_markdown(run: dict) -> str:
    lines = []
    lines.append(f"# UACOS Evidence Report — {run['id']}")
    lines.append("")
    lines.append(f"Status: **{run['status']}**")
    lines.append(f"Task: {run['task']['title']}")
    lines.append(f"Context ID: `{run['context_id']}`")
    lines.append(f"Context tokens estimate: {run['context_token_count']}")
    lines.append("")
    lines.append("## Preflight")
    lines.append(f"- Status: {run['preflight']['status']}")
    for f in run["preflight"].get("findings", []):
        lines.append(f"- {f}")
    lines.append("")
    lines.append("## Patch Check")
    if run.get("patch_check"):
        lines.append(f"- Status: {run['patch_check']['status']}")
        lines.append(f"- Changed files: {run['patch_check'].get('changed_files')}")
        for f in run["patch_check"].get("findings", []):
            lines.append(f"- {f}")
    else:
        lines.append("- No patch supplied.")
    lines.append("")
    lines.append("## Agent Steps")
    for s in run.get("steps", []):
        lines.append(f"- {s.get('role')} / {s.get('agent')}: {s.get('status')} — {s.get('message', s.get('reason', ''))}")
    lines.append("")
    return "\n".join(lines)
