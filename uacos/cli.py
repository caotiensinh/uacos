import argparse
import json
import sys
import os
import traceback
from pathlib import Path


def emit(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))


def resolve_repo(repo):
    return Path(repo).resolve()


def safe_call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        payload = {
            "status": "error",
            "error_type": type(e).__name__,
            "error": str(e),
            "next_step": "rerun with UACOS_DEBUG=1 for traceback, or run uacos health --repo .",
        }
        if os.environ.get("UACOS_DEBUG") == "1":
            payload["traceback"] = traceback.format_exc()[-4000:]
        return payload


def cmd_bootstrap(a):
    from uacos.ops.packaging import bootstrap
    emit(safe_call(bootstrap, resolve_repo(a.repo)))


def cmd_health(a):
    from uacos.ops.packaging import health_check
    emit(safe_call(health_check, resolve_repo(a.repo)))


def cmd_graph_build(a):
    from uacos.graph.builder import build_graph
    emit(safe_call(build_graph, resolve_repo(a.repo)))


def cmd_impact(a):
    from uacos.impact.analyzer import impact_by_task
    emit(safe_call(impact_by_task, resolve_repo(a.repo), a.task))


def cmd_compress_cache(a):
    from uacos.compression.engine import build_summary_cache
    emit(safe_call(build_summary_cache, resolve_repo(a.repo)))


def cmd_context_compressed(a):
    from uacos.compression.engine import compressed_context
    result = safe_call(compressed_context, resolve_repo(a.repo), a.task, max_tokens=a.max_tokens, max_files=a.max_files)
    if isinstance(result, dict) and "content" in result and not a.show_content:
        result = {k: v for k, v in result.items() if k != "content"}
    emit(result)


def cmd_tx_list(a):
    from uacos.transaction.engine import list_transactions
    emit(safe_call(list_transactions, resolve_repo(a.repo)))


def cmd_runtime_init(a):
    from uacos.runtime.agent_runtime import init_runtime
    emit(safe_call(init_runtime, resolve_repo(a.repo)))


def cmd_runtime_status(a):
    from uacos.runtime.agent_runtime import runtime_status
    emit(safe_call(runtime_status, resolve_repo(a.repo)))


def cmd_job_create(a):
    from uacos.runtime.agent_runtime import create_job
    emit(safe_call(create_job, resolve_repo(a.repo), a.task, backend=a.backend, allowed_files=a.allowed_file or [], allowed_dirs=a.allowed_dir or [], tests=a.test or [], auto_apply=a.auto_apply))


def cmd_job_run_once(a):
    from uacos.runtime.agent_runtime import run_job_once
    emit(safe_call(run_job_once, resolve_repo(a.repo), job_id=a.job_id, real=a.real))


def cmd_job_list(a):
    from uacos.runtime.agent_runtime import list_jobs
    emit(safe_call(list_jobs, resolve_repo(a.repo)))


def cmd_phase30_validate(a):
    from uacos.validation.realrun import phase30_full_validation
    emit(safe_call(phase30_full_validation, resolve_repo(a.repo), include_mock_runtime=not a.no_runtime))


def cmd_mcp_self_test(a):
    from uacos.mcp.server import mcp_self_test
    emit(safe_call(mcp_self_test, resolve_repo(a.repo)))


def cmd_mcp_serve(a):
    from uacos.mcp.server import serve_mcp
    serve_mcp(resolve_repo(a.repo), host=a.host, port=a.port)


def cmd_dashboard(a):
    from uacos.dashboard.server import run_dashboard
    run_dashboard(resolve_repo(a.repo), host=a.host, port=a.port)


def cmd_vscode_init(a):
    from uacos.ide.vscode import write_vscode_files
    emit(safe_call(write_vscode_files, resolve_repo(a.repo), dashboard_port=a.dashboard_port, overwrite=a.overwrite))


def cmd_vscode_extension(a):
    from uacos.ide.vscode import write_extension_skeleton
    from uacos.ide.vscode_pro import write_vscode_pro_extension
    output = Path(a.output).resolve()
    builder = write_vscode_pro_extension if a.pro else write_extension_skeleton
    emit(safe_call(builder, output, overwrite=a.overwrite))


def cmd_scan(a):
    from uacos.storage import init_storage
    from uacos.scanner.file_scanner import scan_repo
    repo = resolve_repo(a.repo)
    def _run():
        init_storage(repo)
        return scan_repo(repo)
    emit(safe_call(_run))


def cmd_context(a):
    from uacos.retrieval.context_pack import build_context_pack
    result = safe_call(build_context_pack, resolve_repo(a.repo), a.task, max_tokens=a.max_tokens, search_limit=a.search_limit)
    if isinstance(result, dict) and "content" in result and not a.show_content:
        result = {k: v for k, v in result.items() if k != "content"}
    emit(result)


def cmd_skill_suggest(a):
    from uacos.skill.store import suggest_skills
    emit(safe_call(suggest_skills, resolve_repo(a.repo), a.task, limit=a.limit))


def cmd_patch_check(a):
    from uacos.security.patch_gate import validate_patch_file
    emit(safe_call(validate_patch_file, Path(a.patch).resolve(), allowed_files=a.allowed_file, allowed_dirs=a.allowed_dir))


def cmd_patch20_validate(a):
    from uacos.patching.engine import validate_patch
    patch_text = Path(a.patch).read_text(encoding="utf-8", errors="replace")
    emit(safe_call(validate_patch, resolve_repo(a.repo), patch_text, allowed_files=a.allowed_file, allowed_dirs=a.allowed_dir))


def cmd_semantic_index(a):
    from uacos.semantic.search import build_semantic_index
    emit(safe_call(build_semantic_index, resolve_repo(a.repo)))


def cmd_context_budget(a):
    from uacos.budget.optimizer import build_budgeted_context
    result = safe_call(build_budgeted_context, resolve_repo(a.repo), a.task, profile=a.profile, max_tokens=a.max_tokens)
    if isinstance(result, dict) and "content" in result and not a.show_content:
        result = {k: v for k, v in result.items() if k != "content"}
    emit(result)


def cmd_feedback_recommend(a):
    from uacos.learning.feedback import recommend_skills
    emit(safe_call(recommend_skills, resolve_repo(a.repo), a.task, limit=a.limit))


def cmd_autopilot_plan(a):
    from uacos.autopilot.orchestrator import autopilot_plan
    emit(safe_call(autopilot_plan, resolve_repo(a.repo), a.title, a.objective, allowed_files=a.allowed_file, allowed_dirs=a.allowed_dir, tests=a.test))


def cmd_autopilot_status(a):
    from uacos.autopilot.orchestrator import list_autopilot_runs
    emit(safe_call(list_autopilot_runs, resolve_repo(a.repo)))


def cmd_autopilot_run(a):
    if a.apply and not a.yes:
        emit({"status": "blocked", "reason": "confirmation_required", "hint": "applying patches requires --apply --yes together"})
        return
    from uacos.autopilot.orchestrator import autopilot_run
    emit(safe_call(
        autopilot_run,
        resolve_repo(a.repo),
        Path(a.task_file).resolve(),
        adapter=a.adapter,
        agent_output=Path(a.agent_output).resolve() if a.agent_output else None,
        patch_file=Path(a.patch).resolve() if a.patch else None,
        apply_changes=a.apply,
    ))


def cmd_autopilot_loop(a):
    if not a.yes:
        emit({"status": "blocked", "reason": "confirmation_required", "hint": "autopilot-loop applies patches automatically across iterations; re-run with --yes to confirm"})
        return
    from uacos.autopilot.orchestrator import autopilot_loop
    emit(safe_call(
        autopilot_loop,
        resolve_repo(a.repo),
        a.title,
        a.objective,
        max_iterations=a.max_iterations,
        adapter=a.adapter,
        allowed_files=a.allowed_file,
        allowed_dirs=a.allowed_dir,
        tests=a.test,
        risk_level=a.risk_level,
    ))


def cmd_js_ts_scan(a):
    from uacos.ast_engine.js_parser import parse_repo_js_ts
    result = safe_call(parse_repo_js_ts, resolve_repo(a.repo))
    if isinstance(result, dict) and result.get("status") == "error":
        emit(result)
    else:
        emit({"status": "ok", "files": result})


def cmd_fullstack_index(a):
    from uacos.fullstack.impact import build_fullstack_index
    emit(safe_call(build_fullstack_index, resolve_repo(a.repo)))


def cmd_fullstack_impact(a):
    from uacos.fullstack.impact import fullstack_impact
    emit(safe_call(fullstack_impact, resolve_repo(a.repo), a.task, limit=a.limit))


def cmd_fullstack_context(a):
    from uacos.fullstack.impact import fullstack_context
    result = safe_call(fullstack_context, resolve_repo(a.repo), a.task, max_tokens=a.max_tokens, limit=a.limit)
    if isinstance(result, dict) and "content" in result and not a.show_content:
        result = {k: v for k, v in result.items() if k != "content"}
    emit(result)


def cmd_llm33_init(a):
    from uacos.llm.real_providers import init_real_llm
    emit(safe_call(init_real_llm, resolve_repo(a.repo), ollama_lan=a.ollama_lan))


def cmd_llm33_allow_real(a):
    from uacos.llm.real_providers import set_allowed_real_run
    if not a.yes:
        emit({"status": "blocked", "reason": "explicit --yes required"})
        return
    emit(safe_call(set_allowed_real_run, resolve_repo(a.repo), True))


def cmd_llm33_disallow_real(a):
    from uacos.llm.real_providers import set_allowed_real_run
    emit(safe_call(set_allowed_real_run, resolve_repo(a.repo), False))


def cmd_llm33_provider(a):
    from uacos.llm.real_providers import set_provider
    enabled = True if a.enable else False if a.disable else None
    emit(safe_call(set_provider, resolve_repo(a.repo), a.provider, enabled=enabled, base_url=a.base_url, api_key_env=a.api_key_env))


def cmd_llm33_probe(a):
    from uacos.llm.real_providers import provider_probe
    emit(safe_call(provider_probe, resolve_repo(a.repo), a.provider))


def cmd_llm_run_real(a):
    from uacos.runtime.llm33_runner import llm_run_real
    emit(safe_call(llm_run_real, resolve_repo(a.repo), a.task, size=a.size, real=a.real, max_context_tokens=a.max_context_tokens))


def cmd_llm33_status(a):
    from uacos.runtime.llm33_runner import llm33_status
    emit(safe_call(llm33_status, resolve_repo(a.repo)))


def cmd_budget33_set(a):
    from uacos.token.budget_guard import set_budget
    emit(safe_call(set_budget, resolve_repo(a.repo), max_cloud_tokens=a.max_cloud_tokens, max_total_tokens=a.max_total_tokens, enabled=not a.disable, cloud_only=not a.count_local))


def cmd_budget33_status(a):
    from uacos.token.budget_guard import load_budget
    emit(safe_call(load_budget, resolve_repo(a.repo)))


def cmd_budget33_reset(a):
    from uacos.token.budget_guard import reset_budget
    emit(safe_call(reset_budget, resolve_repo(a.repo)))


def cmd_cache34_benchmark(a):
    from uacos.runtime.llm33_runner import llm_run_real
    repo = resolve_repo(a.repo)
    first = safe_call(llm_run_real, repo, a.task, size=a.size, real=False)
    second = safe_call(llm_run_real, repo, a.task, size=a.size, real=False)
    emit({"status": "ok", "first_status": first.get("status"), "second_status": second.get("status"), "first": {k: v for k, v in first.items() if k != "response"}, "second": {k: v for k, v in second.items() if k != "response"}})


def cmd_cache_status(a):
    from uacos import cache34
    emit(safe_call(cache34.status, "."))


def cmd_cache_clear(a):
    from uacos import cache34
    emit({"status": "ok", "deleted": safe_call(cache34.clear, ".")})


def cmd_skill_list(a):
    from uacos import skill35
    emit(safe_call(skill35.list_skills, "."))


def cmd_skill_stats(a):
    from uacos import skill35
    emit(safe_call(skill35.stats, "."))


def cmd_skill_doctor(a):
    from uacos import skill35
    emit(safe_call(skill35.doctor, "."))


def cmd_skill_prune(a):
    from uacos import skill35
    emit({"status": "ok", "deleted": safe_call(skill35.prune, ".")})


def cmd_skill_dedupe(a):
    from uacos import skill35
    emit({"status": "ok", "deleted": safe_call(skill35.dedupe, ".")})


def cmd_skill_clear(a):
    from uacos import skill35
    emit({"status": "ok", "deleted": safe_call(skill35.clear, ".")})


def cmd_skill_export(a):
    from uacos import skill35
    emit(safe_call(skill35.export_skills, ".", a.file))


def cmd_skill_import(a):
    from uacos import skill35
    emit(safe_call(skill35.import_skills, ".", a.file))


def cmd_skill_publish(a):
    from uacos import skill35
    emit(safe_call(skill35.publish_to_hub, "."))


def cmd_skill_pull(a):
    from uacos import skill35
    emit(safe_call(skill35.pull_from_hub, "."))


def cmd_skill35_benchmark(a):
    from uacos.runner import run
    from uacos import skill35, cache34
    skill35.clear(".")
    cache34.clear(".")
    first = run(".", a.task)
    second = run(".", a.task)
    third = run(".", a.task)
    emit({"status": "ok", "first": first, "second": second, "third": third, "stats": skill35.stats(".")})


def cmd_skill35_status(a):
    from uacos import skill35
    emit(safe_call(skill35.stats, "."))




def cmd_init(a):
    from uacos.auto.engine import install_auto_launcher, run_auto_once
    repo = resolve_repo(a.repo)
    install = safe_call(install_auto_launcher, repo)
    auto = safe_call(run_auto_once, repo, task=a.task, performance=not a.skip_performance, mcp_check=a.mcp_check)
    status = "pass" if install.get("status") == "ok" and auto.get("status") == "pass" else "fail"
    if a.summary and isinstance(auto, dict):
        from uacos.auto.engine import summarize_auto_report
        auto = summarize_auto_report(auto)
    emit({"status": status, "install": install, "auto": auto, "next_step": "run python UACOS_AUTO_START.py from the project root"})


def cmd_auto(a):
    from uacos.auto.engine import run_auto_once, run_auto_watch, summarize_auto_report
    repo = resolve_repo(a.repo)
    if a.watch:
        result = safe_call(run_auto_watch, repo, task=a.task, interval=a.interval, cycles=a.cycles, performance=not a.skip_performance)
    else:
        result = safe_call(run_auto_once, repo, task=a.task, performance=not a.skip_performance, mcp_check=a.mcp_check)
    emit(summarize_auto_report(result) if a.summary and isinstance(result, dict) else result)


def cmd_auto_install(a):
    from uacos.auto.engine import install_auto_launcher
    emit(safe_call(install_auto_launcher, resolve_repo(a.repo)))



def cmd_learn_summary(a):
    from uacos.learning.auto import learn_summary
    from uacos import skill35
    repo = resolve_repo(a.repo)
    result = safe_call(learn_summary, repo)
    if isinstance(result, dict):
        result["skill35"] = safe_call(skill35.stats, str(repo))
    emit(result)


def cmd_learn_review(a):
    from uacos.learning.auto import learn_review
    emit(safe_call(learn_review, resolve_repo(a.repo)))


def cmd_learn_text(a):
    from uacos.learning.auto import learn_from_text, learn_from_file
    repo = resolve_repo(a.repo)
    if a.file:
        result = safe_call(learn_from_file, repo, Path(a.file), title=a.title, auto_approve=a.approve)
    else:
        result = safe_call(learn_from_text, repo, a.text or "", title=a.title, source="cli", auto_approve=a.approve)
    emit(result)


def cmd_experience_recall(a):
    from uacos.auto.engine import _experience_recall
    emit(safe_call(_experience_recall, resolve_repo(a.repo), a.task))

def cmd_task(a):
    from uacos.runner import run
    emit(run(".", " ".join(a.task)))


KNOWN_COMMANDS = {
    "init", "bootstrap", "health", "graph-build", "auto", "auto-install", "impact", "compress-cache", "context-compressed", "tx-list", "runtime-init", "runtime-status", "job-create", "job-run-once", "job-list", "phase30-validate", "mcp-self-test", "mcp-serve", "dashboard", "vscode-init", "vscode-extension", "scan", "context", "skill-suggest", "patch-check", "patch20-validate", "semantic-index", "context-budget", "feedback-recommend", "autopilot-plan", "autopilot-status", "autopilot-run", "autopilot-loop", "js-ts-scan", "fullstack-index", "fullstack-impact", "fullstack-context", "llm33-init", "llm33-allow-real", "llm33-disallow-real", "llm33-provider", "llm33-probe", "llm-run-real", "llm33-status", "budget33-set", "budget33-status", "budget33-reset", "cache34-benchmark", "cache-status", "cache-clear", "skill-list", "skill-stats", "skill-doctor", "skill-prune", "skill-dedupe", "skill-clear", "skill-export", "skill-import", "skill-publish", "skill-pull", "skill35-benchmark", "skill35-status", "learn-summary", "learn-review", "learn-text", "experience-recall", "-h", "--help",
}


def build_parser():
    p = argparse.ArgumentParser(prog="uacos", description="UACOS V4 Real CLI Dispatcher")
    sub = p.add_subparsers(dest="cmd")

    def add(name, fn, repo=True):
        s = sub.add_parser(name)
        if repo:
            s.add_argument("--repo", default=".")
        s.set_defaults(func=fn)
        return s

    s = add("init", cmd_init)
    s.add_argument("--task", default="maintain repo quality and keep UACOS context ready")
    s.add_argument("--skip-performance", action="store_true")
    s.add_argument("--mcp-check", action="store_true")
    s.add_argument("--summary", action="store_true")
    add("bootstrap", cmd_bootstrap)
    add("health", cmd_health)
    s = add("auto", cmd_auto)
    s.add_argument("--task", default="maintain repo quality and keep UACOS context ready")
    s.add_argument("--watch", action="store_true")
    s.add_argument("--interval", type=int, default=10)
    s.add_argument("--cycles", type=int, default=None)
    s.add_argument("--skip-performance", action="store_true")
    s.add_argument("--mcp-check", action="store_true")
    s.add_argument("--summary", action="store_true")
    add("auto-install", cmd_auto_install)
    add("graph-build", cmd_graph_build)

    s = add("impact", cmd_impact); s.add_argument("--task", required=True)
    add("compress-cache", cmd_compress_cache)

    s = add("context-compressed", cmd_context_compressed)
    s.add_argument("--task", required=True); s.add_argument("--max-tokens", type=int, default=6000); s.add_argument("--max-files", type=int, default=8); s.add_argument("--show-content", action="store_true")

    add("tx-list", cmd_tx_list)
    add("runtime-init", cmd_runtime_init)
    add("runtime-status", cmd_runtime_status)

    s = add("job-create", cmd_job_create)
    s.add_argument("--task", required=True); s.add_argument("--backend", default="manual"); s.add_argument("--allowed-file", action="append"); s.add_argument("--allowed-dir", action="append"); s.add_argument("--test", action="append"); s.add_argument("--auto-apply", action="store_true")

    s = add("job-run-once", cmd_job_run_once); s.add_argument("--job-id", default=None); s.add_argument("--real", action="store_true")
    add("job-list", cmd_job_list)

    s = add("phase30-validate", cmd_phase30_validate); s.add_argument("--no-runtime", action="store_true")
    add("mcp-self-test", cmd_mcp_self_test)
    s = add("mcp-serve", cmd_mcp_serve); s.add_argument("--host", default="127.0.0.1"); s.add_argument("--port", type=int, default=8769)
    s = add("dashboard", cmd_dashboard); s.add_argument("--host", default="127.0.0.1"); s.add_argument("--port", type=int, default=8765)
    s = add("vscode-init", cmd_vscode_init); s.add_argument("--dashboard-port", type=int, default=8765); s.add_argument("--overwrite", action="store_true")
    s = add("vscode-extension", cmd_vscode_extension, repo=False); s.add_argument("--output", default="./vscode-uacos"); s.add_argument("--pro", action="store_true"); s.add_argument("--overwrite", action="store_true")

    add("scan", cmd_scan)
    s = add("context", cmd_context); s.add_argument("--task", required=True); s.add_argument("--max-tokens", type=int, default=3500); s.add_argument("--search-limit", type=int, default=8); s.add_argument("--show-content", action="store_true")
    s = add("skill-suggest", cmd_skill_suggest); s.add_argument("--task", required=True); s.add_argument("--limit", type=int, default=5)
    s = add("patch-check", cmd_patch_check); s.add_argument("--patch", required=True); s.add_argument("--allowed-file", action="append"); s.add_argument("--allowed-dir", action="append")
    s = add("patch20-validate", cmd_patch20_validate); s.add_argument("--patch", required=True); s.add_argument("--allowed-file", action="append"); s.add_argument("--allowed-dir", action="append")
    add("semantic-index", cmd_semantic_index)
    s = add("context-budget", cmd_context_budget); s.add_argument("--task", required=True); s.add_argument("--profile", default=None); s.add_argument("--max-tokens", type=int, default=None); s.add_argument("--show-content", action="store_true")
    s = add("feedback-recommend", cmd_feedback_recommend); s.add_argument("--task", required=True); s.add_argument("--limit", type=int, default=5)
    s = add("autopilot-plan", cmd_autopilot_plan); s.add_argument("--title", required=True); s.add_argument("--objective", required=True); s.add_argument("--allowed-file", action="append"); s.add_argument("--allowed-dir", action="append"); s.add_argument("--test", action="append")
    add("autopilot-status", cmd_autopilot_status)
    s = add("autopilot-run", cmd_autopilot_run); s.add_argument("--task-file", required=True); s.add_argument("--adapter", default=None); s.add_argument("--agent-output", default=None); s.add_argument("--patch", default=None); s.add_argument("--apply", action="store_true"); s.add_argument("--yes", action="store_true")
    s = add("autopilot-loop", cmd_autopilot_loop); s.add_argument("--title", required=True); s.add_argument("--objective", required=True); s.add_argument("--max-iterations", type=int, default=3); s.add_argument("--adapter", default=None); s.add_argument("--allowed-file", action="append"); s.add_argument("--allowed-dir", action="append"); s.add_argument("--test", action="append"); s.add_argument("--risk-level", default="normal"); s.add_argument("--yes", action="store_true")

    add("js-ts-scan", cmd_js_ts_scan)
    add("fullstack-index", cmd_fullstack_index)
    s = add("fullstack-impact", cmd_fullstack_impact); s.add_argument("--task", required=True); s.add_argument("--limit", type=int, default=12)
    s = add("fullstack-context", cmd_fullstack_context); s.add_argument("--task", required=True); s.add_argument("--max-tokens", type=int, default=8000); s.add_argument("--limit", type=int, default=10); s.add_argument("--show-content", action="store_true")

    s = add("llm33-init", cmd_llm33_init); s.add_argument("--ollama-lan", default="http://192.168.11.127:11434")
    s = add("llm33-allow-real", cmd_llm33_allow_real); s.add_argument("--yes", action="store_true")
    add("llm33-disallow-real", cmd_llm33_disallow_real)
    s = add("llm33-provider", cmd_llm33_provider); s.add_argument("--provider", required=True); s.add_argument("--enable", action="store_true"); s.add_argument("--disable", action="store_true"); s.add_argument("--base-url", default=None); s.add_argument("--api-key-env", default=None)
    s = add("llm33-probe", cmd_llm33_probe); s.add_argument("--provider", default="ollama_lan")
    s = add("llm-run-real", cmd_llm_run_real); s.add_argument("--task", required=True); s.add_argument("--size", default="small"); s.add_argument("--real", action="store_true"); s.add_argument("--max-context-tokens", type=int, default=6000)
    add("llm33-status", cmd_llm33_status)

    s = add("budget33-set", cmd_budget33_set); s.add_argument("--max-cloud-tokens", type=int, default=None); s.add_argument("--max-total-tokens", type=int, default=None); s.add_argument("--disable", action="store_true"); s.add_argument("--count-local", action="store_true")
    add("budget33-status", cmd_budget33_status)
    add("budget33-reset", cmd_budget33_reset)

    s = add("cache34-benchmark", cmd_cache34_benchmark); s.add_argument("--task", required=True); s.add_argument("--size", default="small")
    add("cache-status", cmd_cache_status, repo=False)
    add("cache-clear", cmd_cache_clear, repo=False)

    add("skill-list", cmd_skill_list, repo=False)
    add("skill-stats", cmd_skill_stats, repo=False)
    add("skill-doctor", cmd_skill_doctor, repo=False)
    add("skill-prune", cmd_skill_prune, repo=False)
    add("skill-dedupe", cmd_skill_dedupe, repo=False)
    add("skill-clear", cmd_skill_clear, repo=False)
    s = add("skill-export", cmd_skill_export, repo=False); s.add_argument("file", nargs="?", default="skills_export.json")
    s = add("skill-import", cmd_skill_import, repo=False); s.add_argument("file")
    add("skill-publish", cmd_skill_publish, repo=False)
    add("skill-pull", cmd_skill_pull, repo=False)
    s = add("skill35-benchmark", cmd_skill35_benchmark); s.add_argument("--task", required=True)
    add("skill35-status", cmd_skill35_status)
    add("learn-summary", cmd_learn_summary)
    add("learn-review", cmd_learn_review)
    s = add("learn-text", cmd_learn_text)
    s.add_argument("--title", required=True); s.add_argument("--text", default=""); s.add_argument("--file", default=None); s.add_argument("--approve", action="store_true")
    s = add("experience-recall", cmd_experience_recall)
    s.add_argument("--task", required=True)

    return p


def main():
    parser = build_parser()
    if len(sys.argv) > 1 and sys.argv[1] not in KNOWN_COMMANDS:
        ns = argparse.Namespace(task=sys.argv[1:], func=cmd_task)
        ns.func(ns)
        return
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
