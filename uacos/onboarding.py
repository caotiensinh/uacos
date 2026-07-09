from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone

from uacos.ops.packaging import bootstrap, health_check, write_run_scripts
from uacos.graph.builder import build_graph
from uacos.compression.engine import build_summary_cache
from uacos.config import uacos_dir


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _check_actions(checks: list[dict]) -> list[dict]:
    actions = []
    for check in checks:
        name = check.get("name")
        if check.get("ok"):
            continue
        if name == "repo_exists":
            actions.append({"check": name, "action": "run from an existing repository directory or pass --repo <path>", "command": "uacos-flow doctor --repo <path>"})
        elif name in {"uacos_dir_exists", "db_exists", "agents_config_exists", "adapters_config_exists"}:
            actions.append({"check": name, "action": "initialize UACOS metadata", "command": "uacos-flow setup --repo ."})
        elif name == "ops_summary_ok":
            actions.append({"check": name, "action": "rebuild repo scan, graph, and summary cache", "command": "uacos-flow setup --repo . --refresh"})
        else:
            actions.append({"check": name, "action": "inspect this failed check", "command": "uacos-flow doctor --repo . --json"})
    return actions


def actionable_doctor(repo_root: Path) -> dict:
    """Return a user-facing doctor report with next actions, not just raw checks."""

    health = health_check(repo_root)
    failed = [check for check in health.get("checks", []) if not check.get("ok")]
    warnings = []
    udir = uacos_dir(repo_root)
    if not (udir / "graph" / "dependency_graph.json").exists():
        warnings.append({"name": "graph_missing", "detail": str(udir / "graph" / "dependency_graph.json"), "command": "uacos-flow setup --repo . --refresh"})
    if not (udir / "compression" / "summary_cache.json").exists():
        warnings.append({"name": "summary_cache_missing", "detail": str(udir / "compression" / "summary_cache.json"), "command": "uacos-flow setup --repo . --refresh"})

    actions = _check_actions(health.get("checks", []))
    if not failed and warnings:
        actions.extend({"check": warning["name"], "action": "build optional readiness artifact", "command": warning["command"]} for warning in warnings)
    status = "pass" if not failed else "fail"
    if status == "pass" and warnings:
        status = "warn"
    return {
        "status": status,
        "mode": "doctor",
        "repo": str(repo_root),
        "failed_count": len(failed),
        "warning_count": len(warnings),
        "summary": "ready" if status == "pass" else "ready but optional artifacts are missing" if status == "warn" else "not ready",
        "failed_checks": failed,
        "warnings": warnings,
        "recommended_actions": actions,
        "next_step": "run uacos-flow setup --repo . --refresh" if actions else "run uacos-flow assist --repo . --task '<your task>'",
        "created_at": utcnow(),
    }


def setup_project(repo_root: Path, *, refresh: bool = False, task: str = "prepare repo for AI-assisted work", dashboard_port: int = 8765) -> dict:
    """One-command project setup for real users.

    This runs the safe local preparation steps and writes convenience scripts.
    It does not call external LLM providers and does not apply patches.
    """

    steps = []
    boot = bootstrap(repo_root, scan=True)
    steps.append({"name": "bootstrap", "status": boot.get("status"), "result": boot})

    graph = build_graph(repo_root)
    steps.append({"name": "graph_build", "status": graph.get("status"), "result": graph})

    cache = build_summary_cache(repo_root)
    steps.append({"name": "summary_cache", "status": cache.get("status"), "result": cache})

    scripts_dir = uacos_dir(repo_root) / "scripts"
    scripts = write_run_scripts(repo_root, scripts_dir, port=dashboard_port)
    steps.append({"name": "run_scripts", "status": scripts.get("status"), "result": scripts})

    doctor = actionable_doctor(repo_root)
    ok = all(step.get("status") in {"ok", "pass"} for step in steps) and doctor.get("status") in {"pass", "warn"}
    return {
        "status": "pass" if ok else "fail",
        "mode": "setup",
        "repo": str(repo_root),
        "task": task,
        "refresh": refresh,
        "steps": steps,
        "doctor": doctor,
        "quick_commands": [
            "uacos-flow doctor --repo .",
            f"uacos-flow assist --repo . --task \"{task}\" --max-tokens 6000",
            "uacos-flow guard --repo . --patch change.diff --allowed-file <path> --test \"pytest -q\"",
            "uacos-flow apply-safe --repo . --patch change.diff --allowed-file <path> --test \"pytest -q\" --yes",
        ],
        "claim": "Setup prepares local metadata only. It does not prove the project is production-ready and does not apply code changes.",
        "created_at": utcnow(),
    }
