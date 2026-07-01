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


def measure_task(repo_root: Path, task: str, max_tokens: int, max_files: int) -> dict:
    from uacos.compression.engine import compressed_context

    started = time.perf_counter()
    ctx = compressed_context(repo_root, task, max_tokens=max_tokens, max_files=max_files)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)

    selected = ctx.get("selected_files", [])
    baseline_prompt, baseline_files = _baseline_prompt(repo_root, task, selected)
    baseline_tokens = _estimate(baseline_prompt)
    uacos_context_tokens = int(ctx.get("compressed_tokens_est") or _estimate(ctx.get("content", "")))

    saved_tokens = max(0, baseline_tokens - uacos_context_tokens)
    savings_ratio = round(saved_tokens / baseline_tokens, 4) if baseline_tokens else 0.0

    return {
        "task": task,
        "status": "ok",
        "elapsed_ms": elapsed_ms,
        "selected_file_count": len(selected),
        "baseline_without_uacos_tokens_est": baseline_tokens,
        "uacos_context_tokens_est": uacos_context_tokens,
        "tokens_saved_est": saved_tokens,
        "savings_ratio": savings_ratio,
        "savings_percent": round(savings_ratio * 100, 2),
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


def run_benchmark(repo_root: Path, tasks: list[str], max_tokens: int, max_files: int, size: str, skip_cache_probe: bool = False) -> dict:
    from uacos.ops.packaging import bootstrap
    from uacos.compression.engine import build_summary_cache
    from uacos.cache.llm_cache import cache_status

    bootstrap(repo_root)
    cache_before = cache_status(repo_root)
    cache_build = build_summary_cache(repo_root)

    task_reports = [measure_task(repo_root, task, max_tokens=max_tokens, max_files=max_files) for task in tasks]
    cache_probe = {"status": "skipped", "reason": "disabled_for_fast_gate"} if skip_cache_probe else (cache_session_probe(repo_root, tasks[0], size=size) if tasks else {"status": "skipped"})

    total_baseline = sum(x["baseline_without_uacos_tokens_est"] for x in task_reports)
    total_uacos = sum(x["uacos_context_tokens_est"] for x in task_reports)
    total_saved = max(0, total_baseline - total_uacos)
    cache_saved = int(cache_probe.get("cache_saved_tokens_est") or 0)

    report = {
        "status": "pass" if all(x["status"] == "ok" for x in task_reports) and cache_probe.get("status") in {"ok", "skipped"} else "fail",
        "created_at": utcnow(),
        "repo": str(repo_root),
        "method": {
            "baseline_without_uacos": "estimated tokens for task prompt plus full raw impacted files selected by UACOS impact/compression",
            "with_uacos": "estimated tokens for UACOS compressed task context generated on the same repo",
            "token_estimator": "uacos.llm.hardened.estimate_tokens",
            "note": "Values are estimates for review and trend tracking, not provider billing records.",
        },
        "summary": {
            "task_count": len(task_reports),
            "baseline_without_uacos_tokens_est": total_baseline,
            "uacos_context_tokens_est": total_uacos,
            "tokens_saved_est": total_saved,
            "savings_percent": round((total_saved / total_baseline) * 100, 2) if total_baseline else 0.0,
            "cache_saved_tokens_est_on_repeated_session": cache_saved,
            "total_saved_including_cache_repeat_est": total_saved + cache_saved,
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
    parser.add_argument("--size", default="small")
    parser.add_argument("--report", default=str(REPORT))
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--skip-cache-probe", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    tasks = args.task or DEFAULT_TASKS
    report = run_benchmark(repo_root, tasks, max_tokens=args.max_tokens, max_files=args.max_files, size=args.size, skip_cache_probe=args.skip_cache_probe)
    out = Path(args.report)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summarize_report(report, out) if args.summary else report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
