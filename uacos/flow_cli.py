from __future__ import annotations

from pathlib import Path
import argparse
import json


def emit(data: dict) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def resolve_repo(repo: str) -> Path:
    return Path(repo).resolve()


def workflow_reference() -> dict:
    return {
        "status": "ok",
        "command": "uacos-flow",
        "purpose": "Simplified product workflow wrapper around existing UACOS commands.",
        "backward_compatibility": "Existing uacos commands are preserved; uacos-flow only groups them by product mode.",
        "modes": [
            {
                "name": "setup",
                "intent": "One-command local setup for new users: bootstrap, graph, cache, scripts, and actionable doctor.",
                "equivalent_commands": ["uacos bootstrap --repo .", "uacos graph-build --repo .", "uacos compress-cache --repo .", "uacos-flow doctor --repo ."],
            },
            {
                "name": "doctor",
                "intent": "Show user-actionable readiness status and next commands.",
                "equivalent_commands": ["uacos health --repo .", "uacos-flow setup --repo . --refresh"],
            },
            {
                "name": "status",
                "intent": "Show compact terminal readiness and evidence summary.",
                "equivalent_commands": ["uacos-flow doctor --repo .", "ls reports .uacos"],
            },
            {
                "name": "prepare",
                "intent": "Build repo state before any AI edit.",
                "equivalent_commands": ["uacos bootstrap --repo .", "uacos health --repo .", "uacos graph-build --repo .", "uacos compress-cache --repo .", "uacos auto --repo . --summary"],
            },
            {
                "name": "assist",
                "intent": "Create bounded task context, explain selected files/symbols, surface route/API relationships, suggest tests, and flag config/deployment risk for an external AI agent.",
                "equivalent_commands": ["uacos impact --repo . --task '<task>'", "uacos context-compressed --repo . --task '<task>' --max-tokens 6000"],
            },
            {
                "name": "guard",
                "intent": "Validate patch scope, task alignment, and risk before applying changes elsewhere.",
                "equivalent_commands": ["uacos patch-check --repo . --patch change.diff --allowed-file path/to/file.py", "uacos impact-alignment-check --repo . --task '<task>' --patch change.diff"],
            },
            {
                "name": "apply-safe",
                "intent": "Apply a reviewed patch through checkpoint, tests, auto-rollback, and last-run evidence.",
                "equivalent_commands": ["uacos-flow guard --patch change.diff --test 'pytest -q'", "uacos transaction-run ..."],
            },
            {
                "name": "orchestrate",
                "intent": "Create a finite spec-driven DevOps loop plan without executing agents or applying patches.",
                "equivalent_commands": ["MCP tool: orchestration_contract", "MCP tool: plan_orchestration_loop", "MCP tool: loop_decision"],
            },
            {
                "name": "benchmark",
                "intent": "Run repeatable token/context benchmark evidence.",
                "equivalent_commands": ["python scripts/uacos_benchmark_suite.py --repo . --manifest evals/benchmark_suite.json --summary"],
            },
        ],
    }


def run_setup(repo_root: Path, task: str = "prepare repo for AI-assisted work", refresh: bool = False, dashboard_port: int = 8765) -> dict:
    from uacos.onboarding import setup_project
    return setup_project(repo_root, task=task, refresh=refresh, dashboard_port=dashboard_port)


def run_doctor(repo_root: Path) -> dict:
    from uacos.onboarding import actionable_doctor
    return actionable_doctor(repo_root)


def run_status(repo_root: Path) -> dict:
    from uacos.onboarding import terminal_status
    return terminal_status(repo_root)


def run_prepare(repo_root: Path, summary: bool = False, skip_performance: bool = False) -> dict:
    from uacos.ops.packaging import bootstrap, health_check
    from uacos.graph.builder import build_graph
    from uacos.compression.engine import build_summary_cache
    from uacos.auto.engine import run_auto_once, summarize_auto_report

    bootstrap_result = bootstrap(repo_root)
    health = health_check(repo_root)
    graph = build_graph(repo_root)
    cache = build_summary_cache(repo_root)
    auto = run_auto_once(repo_root, task="prepare repo for AI-assisted work", performance=not skip_performance, mcp_check=False)
    if summary:
        auto = summarize_auto_report(auto)
    status = "pass" if all(isinstance(x, dict) and x.get("status") in {"ok", "pass"} for x in [bootstrap_result, health, graph, cache]) and isinstance(auto, dict) and auto.get("status") in {"ok", "pass"} else "fail"
    return {"status": status, "mode": "prepare", "repo": str(repo_root), "bootstrap": bootstrap_result, "health": health, "graph": graph, "cache": cache, "auto": auto, "next_step": "run uacos-flow assist --task '<task>' to generate bounded agent context"}


def run_assist(repo_root: Path, task: str, max_tokens: int = 6000, max_files: int = 8, show_content: bool = False) -> dict:
    from uacos.impact.analyzer import impact_by_task
    from uacos.compression.engine import compressed_context
    from uacos.impact.explainer import explain_selected_files
    from uacos.impact.api_graph import build_api_graph
    from uacos.impact.test_map import suggest_tests_for_selected_files
    from uacos.impact.config_risk import build_config_risk_map
    from uacos.impact.symbol_context import build_symbol_context

    impact = impact_by_task(repo_root, task)
    context = compressed_context(repo_root, task, max_tokens=max_tokens, max_files=max_files)
    selected_files = context.get("selected_files", [])
    explanations = explain_selected_files(repo_root, task, selected_files, impact=impact)
    symbol_context = build_symbol_context(repo_root, task=task, selected_files=selected_files)
    api_graph = build_api_graph(repo_root, task=task, selected_files=selected_files)
    test_map = suggest_tests_for_selected_files(repo_root, selected_files)
    config_risk = build_config_risk_map(repo_root, selected_files=selected_files)
    if isinstance(context, dict) and "content" in context and not show_content:
        context = {k: v for k, v in context.items() if k != "content"}
    status = "pass" if isinstance(context, dict) and context.get("status") in {"ok", "pass"} else "fail"
    return {"status": status, "mode": "assist", "repo": str(repo_root), "task": task, "impact": impact, "context": context, "selection_explanations": explanations, "symbol_context": symbol_context, "api_graph": api_graph, "test_map": test_map, "config_risk": config_risk, "next_step": "review selection_explanations, symbol_context, api_graph, test_map, and config_risk; then give the context to your AI agent and validate its patch with uacos-flow guard/apply-safe"}


def run_guard(repo_root: Path, patch: str, task: str | None = None, allowed_files: list[str] | None = None, allowed_dirs: list[str] | None = None, tests: list[str] | None = None) -> dict:
    from uacos.security.patch_gate import validate_patch_file
    from uacos.security.patch_review import review_patch_file
    from uacos.impact.analyzer import impact_alignment_check

    patch_path = Path(patch).resolve()
    validation = validate_patch_file(patch_path, allowed_files=allowed_files or [], allowed_dirs=allowed_dirs or [])
    risk_review = review_patch_file(patch_path, allowed_files=allowed_files or [], allowed_dirs=allowed_dirs or [], tests=tests or [])
    alignment = impact_alignment_check(repo_root, task, patch_path) if task else None
    validation_ok = isinstance(validation, dict) and validation.get("status") in {"ok", "pass", "warn"}
    review_ok = isinstance(risk_review, dict) and risk_review.get("status") in {"ok", "pass", "warn"}
    alignment_ok = alignment is None or (isinstance(alignment, dict) and alignment.get("status") in {"ok", "pass", "warn"})
    return {"status": "pass" if validation_ok and review_ok and alignment_ok else "fail", "mode": "guard", "repo": str(repo_root), "patch": str(patch_path), "validation": validation, "risk_review": risk_review, "impact_alignment": alignment, "writes_code": False, "next_step": "only apply through uacos-flow apply-safe after validation, explicit scope, tests, risk review, and confirmation"}


def run_apply_safe(repo_root: Path, patch: str, title: str = "Safe patch apply", objective: str = "Apply patch through UACOS guarded lifecycle", allowed_files: list[str] | None = None, allowed_dirs: list[str] | None = None, tests: list[str] | None = None, yes: bool = False, allow_high_risk: bool = False) -> dict:
    from uacos.security.patch_lifecycle import safe_apply_patch_file
    return safe_apply_patch_file(repo_root, Path(patch).resolve(), title=title, objective=objective, allowed_files=allowed_files or [], allowed_dirs=allowed_dirs or [], tests=tests or [], yes=yes, allow_high_risk=allow_high_risk)


def run_orchestrate(spec: str, agents: list[str] | None = None, tests: list[str] | None = None, max_iterations: int = 3) -> dict:
    from uacos.orchestrator.contract import build_orchestration_plan
    return build_orchestration_plan(spec, agents=agents or [], tests=tests or [], max_iterations=max_iterations)


def run_benchmark(repo_root: Path, manifest: str, summary: bool = True) -> dict:
    from scripts.uacos_benchmark_suite import run_benchmark_suite, summarize_report
    manifest_path = Path(manifest).resolve()
    report = run_benchmark_suite(repo_root, manifest_path)
    if summary:
        return summarize_report(report, repo_root / "reports" / "uacos_benchmark_suite_report.json")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="uacos-flow", description="Simplified UACOS product workflows: setup, doctor, status, prepare, assist, guard, apply-safe, orchestrate, benchmark.")
    sub = parser.add_subparsers(dest="mode")

    sub.add_parser("list", help="List simplified workflow modes.").set_defaults(handler=lambda args: workflow_reference())

    p = sub.add_parser("setup", help="One-command local setup for new users.")
    p.add_argument("--repo", default=".")
    p.add_argument("--task", default="prepare repo for AI-assisted work")
    p.add_argument("--refresh", action="store_true")
    p.add_argument("--dashboard-port", type=int, default=8765)
    p.set_defaults(handler=lambda args: run_setup(resolve_repo(args.repo), task=args.task, refresh=args.refresh, dashboard_port=args.dashboard_port))

    p = sub.add_parser("doctor", help="Show actionable readiness status and next commands.")
    p.add_argument("--repo", default=".")
    p.set_defaults(handler=lambda args: run_doctor(resolve_repo(args.repo)))

    p = sub.add_parser("status", help="Show compact terminal readiness and evidence summary.")
    p.add_argument("--repo", default=".")
    p.set_defaults(handler=lambda args: run_status(resolve_repo(args.repo)))

    p = sub.add_parser("prepare", help="Build repo state before AI edits.")
    p.add_argument("--repo", default=".")
    p.add_argument("--summary", action="store_true")
    p.add_argument("--skip-performance", action="store_true")
    p.set_defaults(handler=lambda args: run_prepare(resolve_repo(args.repo), summary=args.summary, skip_performance=args.skip_performance))

    p = sub.add_parser("assist", help="Create bounded context for an external AI agent.")
    p.add_argument("--repo", default=".")
    p.add_argument("--task", required=True)
    p.add_argument("--max-tokens", type=int, default=6000)
    p.add_argument("--max-files", type=int, default=8)
    p.add_argument("--show-content", action="store_true")
    p.set_defaults(handler=lambda args: run_assist(resolve_repo(args.repo), args.task, max_tokens=args.max_tokens, max_files=args.max_files, show_content=args.show_content))

    p = sub.add_parser("guard", help="Validate a patch without applying it.")
    p.add_argument("--repo", default=".")
    p.add_argument("--patch", required=True)
    p.add_argument("--task", default=None)
    p.add_argument("--allowed-file", action="append")
    p.add_argument("--allowed-dir", action="append")
    p.add_argument("--test", action="append")
    p.set_defaults(handler=lambda args: run_guard(resolve_repo(args.repo), args.patch, task=args.task, allowed_files=args.allowed_file, allowed_dirs=args.allowed_dir, tests=args.test))

    p = sub.add_parser("apply-safe", help="Apply a patch through checkpoint, tests, rollback, and evidence report.")
    p.add_argument("--repo", default=".")
    p.add_argument("--patch", required=True)
    p.add_argument("--title", default="Safe patch apply")
    p.add_argument("--objective", default="Apply patch through UACOS guarded lifecycle")
    p.add_argument("--allowed-file", action="append")
    p.add_argument("--allowed-dir", action="append")
    p.add_argument("--test", action="append")
    p.add_argument("--yes", action="store_true")
    p.add_argument("--allow-high-risk", action="store_true")
    p.set_defaults(handler=lambda args: run_apply_safe(resolve_repo(args.repo), args.patch, title=args.title, objective=args.objective, allowed_files=args.allowed_file, allowed_dirs=args.allowed_dir, tests=args.test, yes=args.yes, allow_high_risk=args.allow_high_risk))

    p = sub.add_parser("orchestrate", help="Create a finite spec-driven loop plan.")
    p.add_argument("--spec", required=True)
    p.add_argument("--agent", action="append")
    p.add_argument("--test", action="append")
    p.add_argument("--max-iterations", type=int, default=3)
    p.set_defaults(handler=lambda args: run_orchestrate(args.spec, agents=args.agent or [], tests=args.test or [], max_iterations=args.max_iterations))

    p = sub.add_parser("benchmark", help="Run repeatable token/context benchmark evidence.")
    p.add_argument("--repo", default=".")
    p.add_argument("--manifest", default="evals/benchmark_suite.json")
    p.add_argument("--full", action="store_true")
    p.set_defaults(handler=lambda args: run_benchmark(resolve_repo(args.repo), args.manifest, summary=not args.full))

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "handler"):
        emit(workflow_reference())
        return
    emit(args.handler(args))


if __name__ == "__main__":
    main()
