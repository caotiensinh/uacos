from __future__ import annotations

from pathlib import Path
import json
from datetime import datetime, timezone
from uacos.config import uacos_dir
from uacos.agent.task import load_task
from uacos.execution.diff_extract import extract_unified_diff
from uacos.security.patch_gate import validate_patch_text
from uacos.execution.failed_memory import record_failure
from uacos.execution.evidence_ledger import append_evidence_event, hash_text

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
    if diff:
        diff_path.write_text(diff, encoding="utf-8")
        out["diff_file"] = str(diff_path)
    out["artifact_file"] = str(json_path)

    # Persist the referenced artifact before the canonical event is appended. If the
    # process crashes during ledger append, the ledger will never point at a file that
    # was not created yet. The file is then rewritten once with its event ID.
    json_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    event = append_evidence_event(
        repo_root,
        event_type="agent_artifact",
        source="artifacts",
        status=status,
        task_id=task["id"],
        input_hash=hash_text(text),
        diff_hash=hash_text(diff) if diff else None,
        evidence_refs=[str(json_path)] + ([str(diff_path)] if diff else []),
        data={
            "has_diff": bool(diff),
            "patch_check_status": patch_check.get("status") if patch_check else None,
        },
    )
    out["evidence_event_id"] = event["event_id"]
    json_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out

def evidence_report_v2(repo_root: Path, task_file: Path, agent_output: Path | None = None, test_result: dict | None = None, token_summary: dict | None = None, claim_report: dict | None = None) -> str:
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
        lines.append(f"- Evidence event: `{artifact['evidence_event_id']}`")
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
        if test_result.get("evidence_event_ids"):
            lines.append(f"- Evidence events: {', '.join(test_result['evidence_event_ids'])}")
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

    lines.append("## Evidence-Bound Claims")
    if claim_report:
        supported = [item for item in claim_report.get("results", []) if item.get("status") == "SUPPORTED"]
        blocked = [item for item in claim_report.get("results", []) if item.get("status") != "SUPPORTED"]
        if supported:
            for item in supported:
                refs = ", ".join(item.get("accepted_event_ids") or item.get("evidence_event_ids") or [])
                lines.append(f"- VERIFIED `{item.get('claim_id')}` / `{item.get('claim_type')}` -> evidence: {refs}")
        else:
            lines.append("- No supported factual claims.")
        if blocked:
            lines.append("- Blocked claims (not rendered as facts):")
            for item in blocked:
                lines.append(f"  - `{item.get('claim_id')}` -> {item.get('status')} ({item.get('reason')})")
    else:
        lines.append("- No claim-firewall report supplied; no agent claims are promoted to facts.")
    lines.append("")

    final_status = "PASS"
    if artifact and artifact["status"] == "fail":
        final_status = "FAIL"
    if test_result and test_result["status"] == "fail":
        final_status = "FAIL"
    if artifact and artifact["status"] == "partial" and final_status != "FAIL":
        final_status = "PARTIAL"
    if claim_report and claim_report.get("status") != "pass" and final_status != "FAIL":
        final_status = "BLOCKED"

    lines.append(f"## Final Status: {final_status}")
    lines.append("")
    return "\n".join(lines)
