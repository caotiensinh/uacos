from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import os
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "uacos_performance_report.json"

DEFAULT_TASKS = [
    "fix MCP SSE endpoint and docs cleanup",
    "analyze cache similarity and ttl correctness",
    "prepare release gate evidence for review",
]

EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    "reports",
    "dist",
    "build",
    "out",
    "test_out",
    "_uacos",
}

EXCLUDED_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".pyc",
    ".pyo",
    ".so",
    ".dll",
    ".exe",
}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _setup_import_path() -> None:
    root = str(ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    os.environ["PYTHONPATH"] = root + os.pathsep + os.environ.get("PYTHONPATH", "")


def _estimate(text: str) -> int:
    from uacos.llm.hardened import estimate_tokens

    return int(estimate_tokens(text or ""))


def _read_file(repo_root: Path, rel: str, limit: int = 500000) -> str:
    path = repo_root / rel
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")[:limit]


def _is_benchmark_candidate(path: Path, repo_root: Path) -> bool:
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        return False
    if any(part in EXCLUDED_DIRS for part in rel.parts):
        return False
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    if not path.is_file():
        return False
    return True


def estimate_repo_inventory(repo_root: Path, max_repo_files: int = 500, per_file_limit: int = 120000) -> dict:
    """Estimate full-repo text tokens for an upper-bound input-context reduction baseline.

    This intentionally excludes binary/generated/cache directories. The metric is still an
    estimate, not a provider billing record. It is useful for answering: "How much less
    context did UACOS send compared with pasting the relevant text repository snapshot?"
    """

    files = []
    total_tokens = 0
    truncated = False
    for path in sorted(repo_root.rglob("*")):
        if not _is_benchmark_candidate(path, repo_root):
            continue
        if len(files) >= max_repo_files:
            truncated = True
            break
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        try:
            text = path.read_text(encoding="utf-8", errors="replace")[:per_file_limit]
        except OSError:
            continue
        tokens = _estimate(text)
        total_tokens += tokens
        files.append({"file": rel, "tokens_est": tokens})
    return {
        "status": "ok",
        "repo": str(repo_root),
        "file_count": len(files),
        "max_repo_files": max_repo_files,
        "truncated": truncated,
        "tokens_est": total_tokens,
        "top_files_by_tokens": sorted(files, key=lambda item: item["tokens_est"], reverse=True)[:20],
        "note": "Full-repo baseline excludes binary/generated/cache files and is an input-context estimate, not provider billing.",
    }


def classify_input_context_reduction(percent: float) -> dict:
    """Classify full-repo input-context reduction without overclaiming total workflow savings."""

    if percent >= 99.0:
        tier = "research_target_met_input_context_only"
        public_claim = "Only claim 99% for full-repo input-context reduction, and only with pass-rate evidence. Do not claim 99% total token savings."
    elif percent >= 95.0:
        tier = "strong_input_context_reduction"
        public_claim = "Can describe as strong input-context reduction if task quality evidence is present."
    elif percent >= 80.0:
        tier = "moderate_input_context_reduction"
        public_claim = "Can describe as moderate input-context reduction; do not generalize beyond the benchmark."
    else:
        tier = "needs_better_context_selection_or_task_scope"
        public_claim = "Do not use this result for token-saving marketing claims."
    return {
        "tier": tier,
        "full_repo_input_context_reduction_percent": round(percent, 2),
        "target_99_input_context_reduction_met": percent >= 99.0,
        "warning": "This is input-context reduction versus a full-repo text baseline, not total AI workflow token savings and not provider billing.",
        "public_claim_guidance": public_claim,
    }


def _baseline_prompt(repo_root: Path, task: str, selected_files: list[dict]) -> tuple[str, list[dict]]:
    rows = [
        "# Manual LLM Session Without UACOS",
        "",
        f"Task: {task}",
        "",
        "The user manually pasted full impacted files and asked the model to reason over them.",
        "",
    ]
    files = []
    for item in selected_files:
        rel = item.get("file")
        text = _read_file(repo_root, rel)
        tokens = _estimate(text)
        files.append({"file": rel, "raw_tokens_est": tokens})
        rows.append(f"## {rel}")
        rows.append("```text")
        rows.append(text)
        rows.append("```")
        rows.append("")
    return "\n".join(rows), files


def measure_task(repo_root: Path, task: str, max_tokens: int, max_files: int, repo_inventory: dict | None = None) -> dict:
    from uacos.compression.engine import compressed_context

    started = time.perf_counter()
    ctx = compressed_context(repo_root, task, max_tokens=max_tokens, max_files=max_files)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)

    selected = ctx.get("selected_files", [])
    baseline_prompt, baseline_files = _baseline_prompt(repo_root, task, selected)
    task_local_baseline_tokens = _estimate(baseline_prompt)
    uacos_context_tokens = int(ctx.get("compressed_tokens_est") or _estimate(ctx.get("content", "")))

    saved_tokens = max(0, task_local_baseline_tokens - uacos_context_tokens)
    savings_ratio = round(saved_tokens / task_local_baseline_tokens, 4) if task_local_baseline_tokens else 0.0

    repo_tokens = int((repo_inventory or {}).get("tokens_est") or 0)
    full_repo_saved = max(0, repo_tokens - uacos_context_tokens)
    full_repo_reduction = round((full_repo_saved / repo_tokens) * 100, 2) if repo_tokens else 0.0
    claim = classify_input_context_reduction(full_repo_reduction)

    return {
        "task": task,
        "status": "ok",
        "elapsed_ms": elapsed_ms,
        "selected_file_count": len(selected),
        "baseline_without_uacos_tokens_est": task_local_baseline_tokens,
        "task_local_baseline_tokens_est": task_local_baseline_tokens,
        "full_repo_baseline_tokens_est": repo_tokens,
        "uacos_context_tokens_est": uacos_context_tokens,
        "tokens_saved_est": saved_tokens,
        "task_local_savings_ratio": savings_ratio,
        "task_local_savings_percent": round(savings_ratio * 100, 2),
        "savings_ratio": savings_ratio,
        "savings_percent": round(savings_ratio * 100, 2),
        "full_repo_input_context_tokens_saved_est": full_repo_saved,
        "full_repo_input_context_reduction_percent": full_repo_reduction,
        "claim_classification": claim,
        "baseline_files": baseline_files,
        "uacos_selected_files": selected,
        "context_file": ctx.get("context_file"),
    }


def cache_session_probe(repo_root: Path, task: str, size: str) -> dict:
    from uacos.runtime.llm33_runner import llm_run_real

    first = llm_run_real(repo_root, task, size=size, real=False, use_cache=True)
    second = llm_run_real(repo_root, task, size=size, real=False, use_cache=True)
    first_tokens = int(((first.get("usage") or {}).get("total_tokens")) or 0)
    second_saved = int(((second.get("usage") or {}).get("saved_estimated_tokens")) or 0)
    return {
        "status": "ok" if first.get("status") in {"dry_run", "cache_hit"} and second.get("status") == "cache_hit" else "fail",
        "task": task,
        "size": size,
        "first_status": first.get("status"),
        "second_status": second.get("status"),
        "first_session_tokens_est": first_tokens,
        "second_session_tokens_est": int(((second.get("usage") or {}).get("total_tokens")) or 0),
        "cache_saved_tokens_est": second_saved,
        "provider": first.get("provider") or second.get("provider"),
        "model": first.get("model") or second.get("model"),
    }


def run_benchmark(repo_root: Path, tasks: list[str], max_tokens: int, max_files: int, size: str, skip_cache_probe: bool = False, max_repo_files: int = 500) -> dict:
    from uacos.ops.packaging import bootstrap
    from uacos.compression.engine import build_summary_cache
    from uacos.cache.llm_cache import cache_status

    bootstrap(repo_root)
    cache_before = cache_status(repo_root)
    cache_build = build_summary_cache(repo_root)
    repo_inventory = estimate_repo_inventory(repo_root, max_repo_files=max_repo_files)

    task_reports = [measure_task(repo_root, task, max_tokens=max_tokens, max_files=max_files, repo_inventory=repo_inventory) for task in tasks]
    cache_probe = {"status": "skipped", "reason": "disabled_for_fast_gate"} if skip_cache_probe else (cache_session_probe(repo_root, tasks[0], size=size) if tasks else {"status": "skipped"})

    total_task_local_baseline = sum(x["task_local_baseline_tokens_est"] for x in task_reports)
    total_uacos = sum(x["uacos_context_tokens_est"] for x in task_reports)
    total_saved = max(0, total_task_local_baseline - total_uacos)
    cache_saved = int(cache_probe.get("cache_saved_tokens_est") or 0)
    avg_full_repo_reduction = round(sum(float(x.get("full_repo_input_context_reduction_percent") or 0.0) for x in task_reports) / max(1, len(task_reports)), 2)
    tasks_meeting_99 = len([x for x in task_reports if (x.get("claim_classification") or {}).get("target_99_input_context_reduction_met")])

    report = {
        "status": "pass" if all(x["status"] == "ok" for x in task_reports) and cache_probe.get("status") in {"ok", "skipped"} else "fail",
        "created_at": utcnow(),
        "repo": str(repo_root),
        "method": {
            "task_local_baseline_without_uacos": "estimated tokens for task prompt plus full raw impacted files selected by UACOS impact/compression",
            "full_repo_input_baseline": "estimated tokens for a full text repository snapshot, excluding binary/generated/cache files",
            "with_uacos": "estimated tokens for UACOS compressed task context generated on the same repo",
            "token_estimator": "uacos.llm.hardened.estimate_tokens",
            "note": "Values are estimates for review and trend tracking, not provider billing records.",
            "claim_policy": "99% may only refer to full-repo input-context reduction on measured tasks, never total AI workflow token savings.",
        },
        "repo_inventory": repo_inventory,
        "summary": {
            "task_count": len(task_reports),
            "baseline_without_uacos_tokens_est": total_task_local_baseline,
            "task_local_baseline_tokens_est": total_task_local_baseline,
            "full_repo_baseline_tokens_est": repo_inventory.get("tokens_est"),
            "uacos_context_tokens_est": total_uacos,
            "tokens_saved_est": total_saved,
            "task_local_savings_percent": round((total_saved / total_task_local_baseline) * 100, 2) if total_task_local_baseline else 0.0,
            "savings_percent": round((total_saved / total_task_local_baseline) * 100, 2) if total_task_local_baseline else 0.0,
            "average_full_repo_input_context_reduction_percent": avg_full_repo_reduction,
            "tasks_meeting_99_input_context_reduction": tasks_meeting_99,
            "cache_saved_tokens_est_on_repeated_session": cache_saved,
            "total_saved_including_cache_repeat_est": total_saved + cache_saved,
            "claim_warning": "Average full-repo input-context reduction is not total workflow token savings and must be paired with task pass-rate evidence.",
        },
        "cache_before": cache_before,
        "cache_build": cache_build,
        "tasks": task_reports,
        "cache_session_probe": cache_probe,
    }
    return report


def summarize_report(report: dict, report_file: Path) -> dict:
    return {
        "status": report.get("status"),
        "repo": report.get("repo"),
        "summary": report.get("summary", {}),
        "task_count": len(report.get("tasks", [])),
        "cache_session_probe": report.get("cache_session_probe", {}),
        "report_file": str(report_file),
    }


def main() -> int:
    _setup_import_path()
    parser = argparse.ArgumentParser(description="Measure UACOS token efficiency on this repo.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--task", action="append", help="Task to measure. Can be repeated.")
    parser.add_argument("--max-tokens", type=int, default=6000)
    parser.add_argument("--max-files", type=int, default=8)
    parser.add_argument("--max-repo-files", type=int, default=500)
    parser.add_argument("--size", default="small")
    parser.add_argument("--report", default=str(REPORT))
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--skip-cache-probe", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    tasks = args.task or DEFAULT_TASKS
    report = run_benchmark(repo_root, tasks, max_tokens=args.max_tokens, max_files=args.max_files, size=args.size, skip_cache_probe=args.skip_cache_probe, max_repo_files=args.max_repo_files)
    out = Path(args.report)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summarize_report(report, out) if args.summary else report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
