from __future__ import annotations

from pathlib import Path
import json
from datetime import datetime, timezone
from uacos.config import uacos_dir
from uacos.agent.task import load_task
from uacos.execution.diff_extract import extract_unified_diff
from uacos.security.patch_gate import validate_patch_text
from uacos.execution.failed_memory import record_failure

def utcnow():
    return datetime.now(timezone.utc).isoformat()

def evidence_dir(repo_root: Path) -> Path:
    p = uacos_dir(repo_root) / "evidence"
    p.mkdir(parents=True, exist_ok=True)
    return p

def ingest_agent_output(repo_root: Path, task_file: Path, agent_output: Path) -> dict:
    task = load_task(task_file)
    text = agent_output.read_text(encoding="utf-8", errors="replace")
    diff = extract_unified_diff(text)
    patch_check = None
    status = "pass"

    if diff:
        patch_check = validate_patch_text(diff, allowed_files=task.get("allowed_files", []), allowed_dirs=task.get("allowed_dirs", []))
        if patch_check["status"] != "pass":
            status = "fail"
            record_failure(repo_root, task["id"], "patch_check_failed", patch_check)
    else:
        status = "partial"
        record_failure(repo_root, task["id"], "no_diff_found", {"agent_output": str(agent_output)})

    out = {
        "task_id": task["id"],
        "agent_output": str(agent_output),
        "has_diff": bool(diff),
        "patch_check": patch_check,
        "status": status,
        "created_at": utcnow(),
    }

    base = evidence_dir(repo_root) / f"{task['id']}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    json_path = base.with_suffix(".artifact.json")
    diff_path = base.with_suffix(".diff")
    json_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    if diff:
        diff_path.write_text(diff, encoding="utf-8")
        out["diff_file"] = str(diff_path)
    out["artifact_file"] = str(json_path)
    return out

def evidence_report_v2(repo_root: Path, task_file: Path, agent_output: Path | None = None, test_result: dict | None = None, token_summary: dict | None = None) -> str:
    task = load_task(task_file)
    artifact = ingest_agent_output(repo_root, task_file, agent_output) if agent_output else None

    lines = [
        f"# UACOS Evidence Report v2 — {task['id']}",
        "",
        f"Task: **{task.get('title')}**",
        f"Objective: {task.get('objective')}",
        f"Risk: `{task.get('risk_level', 'normal')}`",
        "",
        "## Scope",
        "Allowed files:",
    ]
    lines.extend([f"- `{x}`" for x in task.get("allowed_files", [])] or ["- (none)"])
    lines.append("")
    lines.append("Allowed dirs:")
    lines.extend([f"- `{x}`" for x in task.get("allowed_dirs", [])] or ["- (none)"])
    lines.append("")

    lines.append("## Agent Artifact")
    if artifact:
        lines.append(f"- Status: **{artifact['status']}**")
        lines.append(f"- Has diff: `{artifact['has_diff']}`")
        lines.append(f"- Artifact file: `{artifact['artifact_file']}`")
        if artifact.get("diff_file"):
            lines.append(f"- Diff file: `{artifact['diff_file']}`")
        if artifact.get("patch_check"):
            lines.append(f"- Patch check: **{artifact['patch_check']['status']}**")
            for f in artifact["patch_check"].get("findings", []):
                lines.append(f"  - {f}")
    else:
        lines.append("- No agent output supplied.")
    lines.append("")

    lines.append("## Test Results")
    if test_result:
        lines.append(f"- Status: **{test_result['status']}**")
        lines.append(f"- Result file: `{test_result.get('result_file')}`")
        for r in test_result.get("results", []):
            lines.append(f"  - `{r['command']}` -> {r['status']} ({r.get('reason')})")
    else:
        lines.append("- No tests run.")
    lines.append("")

    lines.append("## Token Ledger")
    if token_summary:
        lines.append(f"- Records: {token_summary.get('records')}")
        lines.append(f"- Input tokens: {token_summary.get('input_tokens')}")
        lines.append(f"- Output tokens: {token_summary.get('output_tokens')}")
        lines.append(f"- Estimated cost USD: {token_summary.get('estimated_cost_usd')}")
    else:
        lines.append("- No token ledger summary supplied.")
    lines.append("")

    final_status = "PASS"
    if artifact and artifact["status"] == "fail":
        final_status = "FAIL"
    if test_result and test_result["status"] == "fail":
        final_status = "FAIL"
    if artifact and artifact["status"] == "partial":
        final_status = "PARTIAL"

    lines.append(f"## Final Status: {final_status}")
    lines.append("")
    return "\n".join(lines)
