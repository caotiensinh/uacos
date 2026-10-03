from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any
import json
import re
import shutil
import tempfile
import time

from uacos.agent.provider_profiles import create_provider_adapter
from uacos.agent.safe_execution import run_safe_agent_execution
from uacos.benchmarks.comparative import BenchmarkThresholds, evaluate_comparative_benchmark
from uacos.graph.builder import build_graph, load_graph
from uacos.graph.roles import classify_source_path
from uacos.impact.analyzer import smart_context
from uacos.llm.hardened import estimate_tokens


MODES = ("full_repo", "grep", "uacos")
TEXT_SUFFIXES = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".rs", ".go", ".java",
    ".c", ".h", ".cc", ".cpp", ".cxx", ".hh", ".hpp", ".hxx",
    ".json", ".yaml", ".yml", ".toml", ".md", ".txt",
}


class ContextOverrideAdapter:
    """Delegate to a provider adapter while replacing only the context payload.

    The harness still owns task, scope, tests, retries, patch validation, and evidence.
    This wrapper changes only what repository context the provider receives, which is
    the variable under test in the comparative benchmark.
    """

    def __init__(self, inner: Any, context: str, *, mode: str) -> None:
        self.inner = inner
        self.context = context
        self.mode = mode
        self.name = getattr(inner, "name", type(inner).__name__)
        self.version = getattr(inner, "version", None)
        self.capabilities = getattr(inner, "capabilities", None)

    def run(self, request):
        metadata = dict(request.metadata or {})
        metadata["benchmark_context_mode"] = self.mode
        metadata["benchmark_context_chars"] = len(self.context)
        return self.inner.run(replace(request, context=self.context, metadata=metadata))


def _safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""


def _iter_text_files(root: Path) -> list[str]:
    """Return repository text files for baseline modes, not only graph-parsed code.

    Full-repo and grep are baselines for repository context, so limiting them to the
    semantic graph would silently omit docs/config files that an ordinary agent could
    inspect. Generated, vendor, ignored, and symlinked paths stay out to match the
    source policy and avoid reading outside the benchmark workspace.
    """
    rows: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        rel = path.relative_to(root).as_posix()
        if classify_source_path(rel) != "source":
            continue
        rows.append(rel)
    return sorted(rows)


def _task_terms(task: str) -> list[str]:
    terms = [token.lower() for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", task or "")]
    stop = {"the", "and", "for", "with", "from", "only", "into", "that", "this", "then", "when", "change"}
    return sorted({term for term in terms if term not in stop})


def _relation_ids(graph: dict, selected_symbols: set[str], selected_files: set[str]) -> list[str]:
    rows: set[str] = set()
    for edge in graph.get("call_edges", []):
        source = edge.get("source_symbol_id")
        target = edge.get("target_symbol_id")
        if source and target and source in selected_symbols and target in selected_symbols:
            rows.add(f"call:{source}->{target}")
    for edge in graph.get("inheritance_edges", []):
        source = edge.get("source_symbol_id")
        target = edge.get("target_symbol_id")
        if source and target and source in selected_symbols and target in selected_symbols:
            relation = str(edge.get("relation") or "inherits")
            rows.add(f"{relation}:{source}->{target}")
    for edge in graph.get("file_edges", []):
        source = str(edge.get("source") or "")
        target = str(edge.get("target") or "")
        if source in selected_files and target in selected_files:
            rows.add(f"import:{source}->{target}")
    for edge in graph.get("architecture_edges", []):
        source = str(edge.get("source_symbol_id") or edge.get("source_file") or "")
        target = str(edge.get("target_symbol_id") or edge.get("target_file") or "")
        source_file = str(edge.get("source_file") or "")
        target_file = str(edge.get("target_file") or "")
        if source_file in selected_files and target_file in selected_files and source and target:
            relation = str(edge.get("relation") or edge.get("kind") or "architecture")
            rows.add(f"{relation}:{source}->{target}")
    for edge in graph.get("test_dependency_edges", []):
        source = str(edge.get("source") or edge.get("source_file") or "")
        target = str(edge.get("target") or edge.get("target_file") or "")
        if source in selected_files and target in selected_files and source and target:
            rows.add(f"test:{source}->{target}")
    return sorted(rows)


def _symbols_for_files(graph: dict, selected_files: set[str]) -> set[str]:
    return {
        str(row["id"])
        for row in graph.get("symbols", [])
        if row.get("id") and str(row.get("file") or "") in selected_files
    }


def _full_repo_context(root: Path, graph: dict, *, max_chars: int) -> dict:
    chunks: list[str] = []
    selected_files: list[str] = []
    used = 0
    truncated = False
    for rel in _iter_text_files(root):
        path = root / rel
        text = _safe_read(path)
        if not text:
            continue
        chunk = f"\n### FILE: {rel}\n{text}\n"
        if used + len(chunk) > max_chars:
            truncated = True
            break
        chunks.append(chunk)
        selected_files.append(rel)
        used += len(chunk)
    files = set(selected_files)
    symbols = _symbols_for_files(graph, files)
    return {
        "mode": "full_repo",
        "content": "".join(chunks),
        "selected_files": selected_files,
        "selected_symbols": sorted(symbols),
        "selected_relations": _relation_ids(graph, symbols, files),
        "truncated": truncated,
    }


def _grep_context(root: Path, graph: dict, task: str, *, max_files: int, max_chars: int) -> dict:
    terms = _task_terms(task)
    candidates: list[tuple[int, str, str]] = []
    for rel in _iter_text_files(root):
        path = root / rel
        text = _safe_read(path)
        if not text:
            continue
        low = text.lower()
        score = sum(low.count(term) for term in terms)
        if score > 0:
            candidates.append((score, rel, text))
    candidates.sort(key=lambda row: (-row[0], row[1]))

    chunks: list[str] = []
    selected_files: list[str] = []
    used = 0
    for _, rel, text in candidates[:max_files]:
        matching_lines = []
        lines = text.splitlines()
        for index, line in enumerate(lines):
            if any(term in line.lower() for term in terms):
                start = max(0, index - 2)
                end = min(len(lines), index + 3)
                matching_lines.extend(f"{i + 1}: {lines[i]}" for i in range(start, end))
        deduped = list(dict.fromkeys(matching_lines))
        chunk = f"\n### GREP FILE: {rel}\n" + "\n".join(deduped) + "\n"
        if used + len(chunk) > max_chars:
            break
        chunks.append(chunk)
        selected_files.append(rel)
        used += len(chunk)

    files = set(selected_files)
    symbols = _symbols_for_files(graph, files)
    return {
        "mode": "grep",
        "content": "".join(chunks),
        "selected_files": selected_files,
        "selected_symbols": sorted(symbols),
        "selected_relations": _relation_ids(graph, symbols, files),
        "truncated": False,
    }


def _uacos_context(root: Path, graph: dict, task: str, *, max_files: int, max_chars: int) -> dict:
    context = smart_context(root, task, max_files=max_files, max_chars=max_chars)
    selected_files = [str(item) for item in context.get("included_files", [])]
    selected_symbols = {
        str(row.get("symbol_id"))
        for row in context.get("included_context", [])
        if row.get("symbol_id")
    }
    if not selected_symbols:
        selected_symbols = _symbols_for_files(graph, set(selected_files))
    return {
        "mode": "uacos",
        "content": str(context.get("content") or ""),
        "selected_files": selected_files,
        "selected_symbols": sorted(selected_symbols),
        "selected_relations": _relation_ids(graph, selected_symbols, set(selected_files)),
        "truncated": False,
        "context_model": context.get("context_model"),
    }


def build_mode_context(
    repo_root: Path,
    task: str,
    mode: str,
    *,
    max_files: int = 8,
    max_chars: int = 18000,
    full_repo_max_chars: int = 500000,
) -> dict:
    root = Path(repo_root).resolve()
    if mode not in MODES:
        raise ValueError(f"unknown_benchmark_mode:{mode}")
    started = time.monotonic()
    build_graph(root)
    graph = load_graph(root, auto_build=False)
    if mode == "full_repo":
        result = _full_repo_context(root, graph, max_chars=full_repo_max_chars)
    elif mode == "grep":
        result = _grep_context(root, graph, task, max_files=max_files, max_chars=max_chars)
    else:
        result = _uacos_context(root, graph, task, max_files=max_files, max_chars=max_chars)
    result["input_tokens_est"] = estimate_tokens(result["content"])
    result["index_overhead_ms"] = max(0, int((time.monotonic() - started) * 1000))
    result["char_count"] = len(result["content"])
    return result


def _copy_repo(source: Path, destination: Path) -> None:
    def ignore(_path: str, names: list[str]):
        ignored = {".git", ".uacos", "__pycache__", ".pytest_cache"}
        return [name for name in names if name in ignored]

    shutil.copytree(source, destination, ignore=ignore)


def run_real_comparative_suite(
    manifest: dict,
    *,
    provider: str,
    argv: list[str],
    model: str,
    output_dir: Path,
    thresholds: BenchmarkThresholds | None = None,
) -> dict:
    if int(manifest.get("version", 0)) != 1:
        raise ValueError("unsupported_real_comparative_manifest_version")
    tasks = manifest.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("real_comparative_tasks_required")
    repeats = int(manifest.get("repeats", 3))
    if repeats < 3:
        raise ValueError("real_comparative_minimum_repeats_is_3")
    if not argv:
        raise ValueError("provider_argv_required")
    if not model.strip():
        raise ValueError("provider_model_required")

    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    observations: list[dict] = []
    evidence_rows: list[dict] = []

    for task in tasks:
        task_id = str(task.get("id") or "")
        source_repo = Path(str(task.get("repo") or "")).resolve()
        task_text = str(task.get("task") or "")
        if not task_id or not source_repo.is_dir() or not task_text:
            raise ValueError(f"invalid_real_comparative_task:{task_id or '<missing>'}")

        for mode in MODES:
            for repeat_number in range(1, repeats + 1):
                with tempfile.TemporaryDirectory(prefix=f"uacos-bench-{task_id}-{mode}-") as temp:
                    workspace = Path(temp) / "repo"
                    _copy_repo(source_repo, workspace)
                    context = build_mode_context(
                        workspace,
                        task_text,
                        mode,
                        max_files=int(task.get("max_files", 8)),
                        max_chars=int(task.get("max_context_chars", 18000)),
                        full_repo_max_chars=int(task.get("full_repo_max_chars", 500000)),
                    )
                    if mode == "full_repo" and context.get("truncated"):
                        raise ValueError(f"full_repo_context_truncated:{task_id}")

                    base_adapter = create_provider_adapter(provider, argv=list(argv), version=model, cwd=workspace)
                    adapter = ContextOverrideAdapter(base_adapter, context["content"], mode=mode)
                    execution = run_safe_agent_execution(
                        workspace,
                        task_text,
                        adapter,
                        allowed_files=list(task.get("allowed_files") or []),
                        allowed_dirs=list(task.get("allowed_dirs") or []),
                        tests=list(task.get("tests") or []),
                        max_iterations=int(task.get("max_iterations", 2)),
                        timeout_seconds=int(task.get("timeout_seconds", 180)),
                        max_files=int(task.get("max_files", 8)),
                        max_context_chars=int(task.get("max_context_chars", 18000)),
                    )
                    harness = execution.get("harness") or {}
                    metrics = harness.get("metrics") or {}
                    attempts = harness.get("attempts") or []
                    winning_result = (attempts[-1].get("adapter_result") if attempts else {}) or {}
                    tokens_in_actual = int(winning_result.get("tokens_in") or 0)
                    tokens_out_actual = int(winning_result.get("tokens_out") or 0)
                    output_text = str(winning_result.get("output") or "")
                    input_tokens = tokens_in_actual or int(context["input_tokens_est"])
                    output_tokens = tokens_out_actual or estimate_tokens(output_text)
                    observation = {
                        "task_id": task_id,
                        "mode": mode,
                        "repeat": repeat_number,
                        "provider": provider,
                        "model": model,
                        "passed": execution.get("status") == "passed",
                        "retries": int(metrics.get("retry_count") or 0),
                        "tool_calls": int(metrics.get("tool_calls") or 0),
                        "input_tokens": input_tokens,
                        "total_tokens": input_tokens + output_tokens,
                        "latency_ms": int(metrics.get("elapsed_ms") or 0),
                        "index_overhead_ms": int(context["index_overhead_ms"]),
                        "selected_symbols": list(context["selected_symbols"]),
                        "selected_relations": list(context["selected_relations"]),
                        "token_source": "provider" if tokens_in_actual else "estimated_prompt_context",
                        "execution_status": execution.get("status"),
                        "execution_reason": execution.get("reason"),
                    }
                    observations.append(observation)
                    evidence_rows.append({
                        "task_id": task_id,
                        "mode": mode,
                        "repeat": repeat_number,
                        "context": {k: v for k, v in context.items() if k != "content"},
                        "execution": execution,
                    })

    evaluator_manifest = {
        "version": 1,
        "tasks": [
            {
                "id": str(task["id"]),
                "required_symbols": list(task.get("required_symbols") or []),
                "required_relations": list(task.get("required_relations") or []),
            }
            for task in tasks
        ],
    }
    report = evaluate_comparative_benchmark(
        evaluator_manifest,
        observations,
        thresholds=thresholds,
    )
    report["real_provider_execution"] = True
    report["provider"] = provider
    report["model"] = model
    report["repeats"] = repeats
    report["token_accounting_note"] = (
        "Uses provider-reported input tokens when available; otherwise records a conservative prompt-context estimate and labels token_source per observation."
    )
    observations_path = output_dir / "real_comparative_observations.json"
    evidence_path = output_dir / "real_comparative_evidence.json"
    report_path = output_dir / "comparative_ground_truth_benchmark.json"
    observations_path.write_text(json.dumps(observations, indent=2, sort_keys=True, default=str), encoding="utf-8")
    evidence_path.write_text(json.dumps(evidence_rows, indent=2, sort_keys=True, default=str), encoding="utf-8")
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True, default=str), encoding="utf-8")
    return {
        "status": report["status"],
        "report": report,
        "report_path": str(report_path),
        "observations_path": str(observations_path),
        "evidence_path": str(evidence_path),
    }
