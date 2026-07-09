from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "evals" / "benchmark_suite.json"
DEFAULT_REPORT = ROOT / "reports" / "uacos_benchmark_suite_report.json"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _setup_import_path() -> None:
    root = str(ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    os.environ["PYTHONPATH"] = root + os.pathsep + os.environ.get("PYTHONPATH", "")


def load_manifest(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_manifest(data)
    return data


def validate_manifest(data: dict) -> None:
    if not isinstance(data, dict):
        raise ValueError("manifest_must_be_object")
    if int(data.get("version", 0)) != 1:
        raise ValueError("unsupported_manifest_version")
    suites = data.get("suites")
    if not isinstance(suites, list) or not suites:
        raise ValueError("suites_required")
    for suite in suites:
        if not suite.get("id"):
            raise ValueError("suite_id_required")
        tasks = suite.get("tasks")
        if not isinstance(tasks, list) or not tasks:
            raise ValueError(f"suite_tasks_required:{suite.get('id')}")
        if int(suite.get("max_tokens", 0)) < 500:
            raise ValueError(f"suite_max_tokens_too_low:{suite.get('id')}")
        if int(suite.get("max_files", 0)) < 1:
            raise ValueError(f"suite_max_files_too_low:{suite.get('id')}")
    thresholds = data.get("pass_thresholds") or {}
    for key in ["min_task_success_rate", "min_context_quality_pass_rate", "min_average_savings_percent"]:
        value = float(thresholds.get(key, 0.0))
        if value < 0:
            raise ValueError(f"negative_threshold:{key}")


def _contains_any(text: str, keywords: list[str]) -> bool:
    low = (text or "").lower()
    return any(str(word).lower() in low for word in keywords)


def _contains_none(text: str, words: list[str]) -> bool:
    low = (text or "").lower()
    return all(str(word).lower() not in low for word in words)


def run_context_quality_checks(repo_root: Path, checks: list[dict], max_tokens: int, max_files: int) -> dict:
    from uacos.compression.engine import compressed_context

    rows = []
    for check in checks or []:
        task = check.get("task", "")
        ctx = compressed_context(repo_root, task, max_tokens=max_tokens, max_files=max_files)
        content = ctx.get("content", "")
        has_expected = _contains_any(content, check.get("expected_keywords") or [])
        has_no_banned = _contains_none(content, check.get("must_not_contain") or [])
        ok = bool(has_expected and has_no_banned)
        rows.append({
            "task": task,
            "status": "pass" if ok else "fail",
            "expected_keywords": check.get("expected_keywords") or [],
            "must_not_contain": check.get("must_not_contain") or [],
            "has_expected_keyword": has_expected,
            "has_no_banned_words": has_no_banned,
            "selected_file_count": ctx.get("selected_file_count"),
            "compressed_tokens_est": ctx.get("compressed_tokens_est"),
        })
    passed = len([row for row in rows if row["status"] == "pass"])
    pass_rate = round(passed / max(1, len(rows)), 4)
    return {"status": "pass" if pass_rate >= 0.5 else "fail", "pass_rate": pass_rate, "checks": rows}


def run_suite(root_repo: Path, suite: dict) -> dict:
    from scripts.uacos_performance_benchmark import run_benchmark

    repo_root = (root_repo / suite.get("repo", ".")).resolve()
    tasks = [str(t) for t in suite.get("tasks", [])]
    max_tokens = int(suite.get("max_tokens", 3000))
    max_files = int(suite.get("max_files", 4))
    skip_cache_probe = bool(suite.get("skip_cache_probe", True))

    perf = run_benchmark(
        repo_root,
        tasks,
        max_tokens=max_tokens,
        max_files=max_files,
        size=str(suite.get("size", "small")),
        skip_cache_probe=skip_cache_probe,
    )
    quality = run_context_quality_checks(repo_root, suite.get("quality_checks") or [], max_tokens=max_tokens, max_files=max_files)
    return {
        "id": suite["id"],
        "status": "pass" if perf.get("status") == "pass" and quality.get("status") == "pass" else "fail",
        "repo": str(repo_root),
        "max_tokens": max_tokens,
        "max_files": max_files,
        "performance": perf,
        "context_quality": quality,
    }


def summarize_suites(suites: list[dict], thresholds: dict | None = None) -> dict:
    thresholds = thresholds or {}
    task_reports = []
    quality_rates = []
    for suite in suites:
        perf = suite.get("performance") or {}
        task_reports.extend(perf.get("tasks") or [])
        quality_rates.append(float((suite.get("context_quality") or {}).get("pass_rate") or 0.0))

    task_success_rate = round(len([t for t in task_reports if t.get("status") == "ok"]) / max(1, len(task_reports)), 4)
    avg_savings = round(sum(float(t.get("savings_percent") or 0.0) for t in task_reports) / max(1, len(task_reports)), 2)
    avg_quality = round(sum(quality_rates) / max(1, len(quality_rates)), 4)

    min_task_success = float(thresholds.get("min_task_success_rate", 1.0))
    min_quality = float(thresholds.get("min_context_quality_pass_rate", 0.5))
    min_savings = float(thresholds.get("min_average_savings_percent", 0.0))

    status = "pass" if task_success_rate >= min_task_success and avg_quality >= min_quality and avg_savings >= min_savings else "fail"
    return {
        "status": status,
        "suite_count": len(suites),
        "task_count": len(task_reports),
        "task_success_rate": task_success_rate,
        "average_context_quality_pass_rate": avg_quality,
        "average_savings_percent": avg_savings,
        "thresholds": {
            "min_task_success_rate": min_task_success,
            "min_context_quality_pass_rate": min_quality,
            "min_average_savings_percent": min_savings,
        },
    }


def run_benchmark_suite(root_repo: Path, manifest_path: Path) -> dict:
    manifest = load_manifest(manifest_path)
    suites = [run_suite(root_repo, suite) for suite in manifest["suites"]]
    summary = summarize_suites(suites, manifest.get("pass_thresholds") or {})
    return {
        "status": summary["status"],
        "created_at": utcnow(),
        "manifest": str(manifest_path),
        "method": {
            "mode": "dry_local_repeatable",
            "requires_cloud_llm": False,
            "token_values": "estimates_not_provider_billing_records",
            "quality_signal": "keyword and banned-word checks over compressed context",
            "claim_policy": "do not claim 80-90 percent savings without real benchmark evidence",
        },
        "summary": summary,
        "method_notes": manifest.get("method_notes") or [],
        "suites": suites,
    }


def summarize_report(report: dict, report_file: Path) -> dict:
    return {
        "status": report.get("status"),
        "summary": report.get("summary", {}),
        "manifest": report.get("manifest"),
        "report_file": str(report_file),
    }


def main() -> int:
    _setup_import_path()
    parser = argparse.ArgumentParser(description="Run repeatable UACOS benchmark suites from a manifest.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    root_repo = Path(args.repo).resolve()
    manifest_path = Path(args.manifest).resolve()
    report = run_benchmark_suite(root_repo, manifest_path)
    out = Path(args.report).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summarize_report(report, out) if args.summary else report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
