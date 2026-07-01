from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import time
import traceback

from uacos.config import uacos_dir


DEFAULT_TASK = "maintain repo quality and keep UACOS context ready"
WATCH_EXTS = {".py", ".md", ".js", ".jsx", ".ts", ".tsx", ".json", ".toml", ".yaml", ".yml"}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def auto_dir(repo_root: Path) -> Path:
    path = uacos_dir(repo_root) / "auto"
    path.mkdir(parents=True, exist_ok=True)
    return path


def state_path(repo_root: Path) -> Path:
    return auto_dir(repo_root) / "auto_state.json"


def report_path(repo_root: Path) -> Path:
    path = repo_root / "reports"
    path.mkdir(parents=True, exist_ok=True)
    return path / "uacos_auto_report.json"


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _compact_value(value, max_string: int = 1200):
    if isinstance(value, dict):
        compact = {}
        for key, item in value.items():
            if key in {"content", "prompt", "response", "raw"}:
                compact[f"{key}_omitted"] = True
                compact[f"{key}_chars"] = len(str(item or ""))
                continue
            compact[key] = _compact_value(item, max_string=max_string)
        return compact
    if isinstance(value, list):
        return [_compact_value(item, max_string=max_string) for item in value[:20]]
    if isinstance(value, str) and len(value) > max_string:
        return value[:max_string] + f"... <omitted {len(value) - max_string} chars>"
    return value


def summarize_auto_report(report: dict) -> dict:
    steps = report.get("steps", [])
    perf = next((s.get("result", {}) for s in steps if s.get("name") == "performance_probe"), {})
    context = next((s.get("result", {}) for s in steps if s.get("name") == "task_context_ready"), {})
    return {
        "status": report.get("status"),
        "mode": report.get("mode"),
        "repo": report.get("repo"),
        "task": report.get("task"),
        "step_count": len(steps),
        "failed_steps": [s.get("name") for s in steps if not s.get("ok")],
        "selected_file_count": context.get("selected_file_count"),
        "compressed_tokens_est": context.get("compressed_tokens_est"),
        "tokens_saved_est": perf.get("tokens_saved_est"),
        "savings_percent": perf.get("savings_percent"),
        "report_file": str(report_path(Path(report.get("repo", ".")))) if report.get("repo") else None,
        "next_best_action": report.get("next_best_action"),
    }


def _step(name: str, fn, *args, **kwargs) -> dict:
    started = time.perf_counter()
    try:
        result = fn(*args, **kwargs)
        status = result.get("status") if isinstance(result, dict) else "ok"
        ok = status not in {"error", "fail", "blocked"}
        return {
            "name": name,
            "status": status or "ok",
            "ok": ok,
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
            "result": _compact_value(result),
        }
    except Exception as exc:
        return {
            "name": name,
            "status": "error",
            "ok": False,
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
            "error_type": type(exc).__name__,
            "error": str(exc),
            "traceback": traceback.format_exc()[-4000:],
        }


def _snapshot(repo_root: Path) -> dict:
    files = []
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        parts = set(path.parts)
        if ".git" in parts or ".uacos" in parts or "__pycache__" in parts or ".venv" in parts:
            continue
        if path.suffix.lower() not in WATCH_EXTS:
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
        files.append({"path": rel, "mtime_ns": stat.st_mtime_ns, "size": stat.st_size})
    files.sort(key=lambda x: x["path"])
    return {"file_count": len(files), "files": files}


def _changed(before: dict | None, after: dict) -> bool:
    if not before:
        return True
    return before.get("files") != after.get("files")



def _clip_text(text: str, limit: int = 1600) -> str:
    text = str(text or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit] + f"... <omitted {len(text) - limit} chars>"


def _experience_recall(repo_root: Path, task: str) -> dict:
    from uacos.memory.store import memory_summary_for_task
    from uacos.skill.store import skill_summary_for_task, suggest_skills
    from uacos import skill35

    memory_summary = memory_summary_for_task(repo_root, task, limit=8)
    skill_summary = skill_summary_for_task(repo_root, task, limit=5)
    matched_skills = suggest_skills(repo_root, task, limit=5, min_score=1.0)
    compat = []
    all_compat = []
    for skill in skill35.list_skills(str(repo_root)):
        score = skill35.score(skill, task)
        item = {k: skill.get(k) for k in ("id", "task", "tags", "source")}
        item["score"] = round(score, 4)
        all_compat.append(item)
        if score >= 0.15:
            compat.append(item)
    compat.sort(key=lambda item: item["score"], reverse=True)
    if not compat and all_compat:
        all_compat.sort(key=lambda item: item["score"], reverse=True)
        compat = all_compat[:3]
    return {
        "status": "ok",
        "matched_skill_count": len(matched_skills),
        "matched_skill35_count": len(compat),
        "memory_summary": _clip_text(memory_summary, 1200),
        "skill_summary": _clip_text(skill_summary, 1200),
        "skill35_matches": compat[:5],
    }


def _task_with_experience(task: str, recall: dict | None) -> str:
    if not isinstance(recall, dict) or recall.get("status") != "ok":
        return task
    parts = [task]
    for key in ("memory_summary", "skill_summary"):
        value = str(recall.get(key) or "").strip()
        if value and not value.startswith("No "):
            parts.append(value)
    return _clip_text("\n\n".join(parts), 2200)


def _experience_record(repo_root: Path, task: str, status: str, steps: list[dict]) -> dict:
    from uacos.memory.store import add_memory, read_memories
    from uacos import skill35

    failed = [s.get("name") for s in steps if not s.get("ok")]
    perf = next((s.get("result", {}) for s in steps if s.get("name") == "performance_probe"), {})
    savings = perf.get("savings_percent")
    value = (
        "UACOS dogfood auto mode should run with --summary after every upgrade; "
        f"last_status={status}; failed_steps={failed}; "
        f"savings_percent={savings}; report=reports/uacos_auto_report.json."
    )
    existing = [m for m in read_memories(repo_root) if m.get("key") == "uacos_dogfood_after_upgrade"]
    memory = None
    if not existing or existing[-1].get("value") != value:
        memory = add_memory(
            repo_root,
            kind="decision",
            key="uacos_dogfood_after_upgrade",
            value=value,
            source="uacos.auto.engine",
            confidence=0.85,
            tags=["dogfood", "auto_mode", "token_savings", "after_upgrade"],
            applies_to=["uacos/auto/engine.py", "scripts/release_gate.py"],
        )
    skill_id = skill35.save(
        str(repo_root),
        "dogfood UACOS after each upgrade with summary auto mode and token benchmark",
        value + " Commands: python -m uacos.cli auto --repo . --summary; python scripts/uacos_performance_benchmark.py --repo . --summary; python scripts/release_gate.py",
        tags=["dogfood", "auto_mode", "token_savings"],
        source="uacos.auto.engine",
    )
    return {"status": "ok", "memory_id": memory.get("id") if memory else None, "skill35_id": skill_id}

def _small_performance_probe(repo_root: Path, task: str) -> dict:
    from uacos.compression.engine import compressed_context
    from uacos.llm.hardened import estimate_tokens

    ctx = compressed_context(repo_root, task, max_tokens=4000, max_files=4)
    baseline = 0
    for item in ctx.get("selected_files", []):
        baseline += int(item.get("raw_tokens") or 0)
    uacos_tokens = int(ctx.get("compressed_tokens_est") or estimate_tokens(ctx.get("content", "")))
    saved = max(0, baseline - uacos_tokens)
    return {
        "status": "pass",
        "task": task,
        "baseline_without_uacos_tokens_est": baseline,
        "uacos_context_tokens_est": uacos_tokens,
        "tokens_saved_est": saved,
        "savings_percent": round(saved / baseline * 100, 2) if baseline else 0.0,
        "selected_file_count": len(ctx.get("selected_files", [])),
    }


def run_auto_once(
    repo_root: Path | str,
    task: str = DEFAULT_TASK,
    performance: bool = True,
    mcp_check: bool = False,
) -> dict:
    repo_root = Path(repo_root).resolve()

    from uacos.ops.packaging import bootstrap, health_check
    from uacos.graph.builder import build_graph
    from uacos.compression.engine import build_summary_cache, compressed_context, compression_report
    from uacos.cache.llm_cache import cache_status
    from uacos.token.budget_guard import load_budget
    from uacos import skill35

    steps = []
    recall_step = _step("experience_recall", _experience_recall, repo_root, task)
    recall = recall_step.get("result") if recall_step.get("ok") else {}
    effective_task = _task_with_experience(task, recall)
    steps.append(recall_step)
    steps.append(_step("bootstrap", bootstrap, repo_root))
    steps.append(_step("health_check", health_check, repo_root))
    steps.append(_step("graph_build", build_graph, repo_root))
    steps.append(_step("compression_cache", build_summary_cache, repo_root))
    steps.append(_step("task_context_ready", compressed_context, repo_root, effective_task, 4000, 6))
    steps.append(_step("compression_report", compression_report, repo_root))
    steps.append(_step("cache_status", cache_status, repo_root))
    steps.append(_step("skill35_status", skill35.stats, str(repo_root)))
    steps.append(_step("budget_status", load_budget, repo_root))

    if mcp_check:
        from uacos.mcp.server import mcp_self_test

        steps.append(_step("mcp_self_test", mcp_self_test, repo_root))

    if performance:
        steps.append(_step("performance_probe", _small_performance_probe, repo_root, effective_task))

    status = "pass" if all(step["ok"] for step in steps) else "fail"
    steps.append(_step("experience_record", _experience_record, repo_root, task, status, steps))
    status = "pass" if all(step["ok"] for step in steps) else "fail"
    snapshot = _snapshot(repo_root)
    report = {
        "status": status,
        "mode": "auto_once",
        "repo": str(repo_root),
        "task": task,
        "created_at": utcnow(),
        "steps": steps,
        "snapshot": {"file_count": snapshot["file_count"]},
        "next_best_action": "ready_for_user_task" if status == "pass" else "inspect_failed_steps",
    }
    _write_json(report_path(repo_root), report)
    _write_json(state_path(repo_root), {"updated_at": utcnow(), "last_report": str(report_path(repo_root)), "snapshot": snapshot})
    return report


def run_auto_watch(
    repo_root: Path | str,
    task: str = DEFAULT_TASK,
    interval: int = 10,
    cycles: int | None = None,
    performance: bool = False,
) -> dict:
    repo_root = Path(repo_root).resolve()
    state = {}
    if state_path(repo_root).exists():
        try:
            state = json.loads(state_path(repo_root).read_text(encoding="utf-8"))
        except Exception:
            state = {}

    previous = state.get("snapshot")
    runs = []
    cycle = 0
    while True:
        current = _snapshot(repo_root)
        if _changed(previous, current):
            report = run_auto_once(repo_root, task=task, performance=performance)
            runs.append({"created_at": utcnow(), "status": report.get("status"), "reason": "repo_changed"})
            previous = current
        else:
            _write_json(state_path(repo_root), {
                "updated_at": utcnow(),
                "mode": "watch",
                "last_report": str(report_path(repo_root)),
                "snapshot": current,
                "last_poll": utcnow(),
            })
        cycle += 1
        if cycles is not None and cycle >= cycles:
            break
        time.sleep(max(1, int(interval)))

    result = {"status": "pass", "mode": "auto_watch", "cycles": cycle, "runs": runs, "repo": str(repo_root)}
    _write_json(report_path(repo_root), result)
    return result


def install_auto_launcher(repo_root: Path | str) -> dict:
    repo_root = Path(repo_root).resolve()
    launcher = repo_root / "UACOS_AUTO_START.py"
    launcher.write_text(
        """from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from uacos.auto.engine import run_auto_once, summarize_auto_report

if __name__ == "__main__":
    report = run_auto_once(ROOT)
    print(json.dumps(summarize_auto_report(report), ensure_ascii=False, indent=2))
    raise SystemExit(0 if report.get("status") == "pass" else 1)
""",
        encoding="utf-8",
    )
    readme = auto_dir(repo_root) / "README_AUTO_MODE.md"
    readme.write_text(
        """# UACOS Auto Mode

Run `UACOS_AUTO_START.py` from the project root to let UACOS prepare itself automatically.

Auto Mode runs experience recall, bootstrap, health checks, graph build, compression cache, task context preparation, cache status, skill status, budget status, experience recording, and a lightweight performance probe.

Advanced users can still use every CLI command directly.
""",
        encoding="utf-8",
    )
    return {"status": "ok", "launcher": str(launcher), "readme": str(readme)}
