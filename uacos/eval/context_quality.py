from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import mean
from typing import Iterable

from uacos.graph.builder import build_graph, load_graph
from uacos.graph.query import query_symbol
from uacos.impact.analyzer import impact_by_task


def _norm_path(value: str) -> str:
    return str(value).replace("\\", "/").lstrip("./")


def _ratio(num: int, den: int, empty_value: float = 1.0) -> float:
    return round(num / den, 4) if den else float(empty_value)


@dataclass(frozen=True)
class ContextQualityThresholds:
    min_file_recall: float = 0.95
    min_required_symbol_recall: float = 0.95
    max_noise_ratio: float = 0.20

    def validate(self) -> None:
        for name, value in asdict(self).items():
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


def evaluate_selection(
    selected_files: Iterable[str],
    required_files: Iterable[str],
    *,
    selected_symbol_ids: Iterable[str] | None = None,
    required_symbol_ids: Iterable[str] | None = None,
    allowed_support_files: Iterable[str] | None = None,
    thresholds: ContextQualityThresholds | None = None,
) -> dict:
    thresholds = thresholds or ContextQualityThresholds()
    thresholds.validate()

    selected = {_norm_path(x) for x in selected_files if str(x).strip()}
    required = {_norm_path(x) for x in required_files if str(x).strip()}
    support = {_norm_path(x) for x in (allowed_support_files or []) if str(x).strip()}
    useful = required | support

    selected_symbols = {str(x) for x in (selected_symbol_ids or []) if str(x).strip()}
    required_symbols = {str(x) for x in (required_symbol_ids or []) if str(x).strip()}

    covered_required_files = selected & required
    useful_selected_files = selected & useful
    noisy_files = selected - useful
    covered_required_symbols = selected_symbols & required_symbols

    file_precision = _ratio(len(useful_selected_files), len(selected), empty_value=1.0 if not useful else 0.0)
    file_recall = _ratio(len(covered_required_files), len(required), empty_value=1.0)
    required_symbol_recall = _ratio(
        len(covered_required_symbols),
        len(required_symbols),
        empty_value=1.0,
    )
    noise_ratio = _ratio(len(noisy_files), len(selected), empty_value=0.0)

    gate_reasons = []
    if file_recall < thresholds.min_file_recall:
        gate_reasons.append(
            f"file_recall {file_recall:.4f} < {thresholds.min_file_recall:.4f}"
        )
    if required_symbol_recall < thresholds.min_required_symbol_recall:
        gate_reasons.append(
            "required_symbol_recall "
            f"{required_symbol_recall:.4f} < {thresholds.min_required_symbol_recall:.4f}"
        )
    if noise_ratio > thresholds.max_noise_ratio:
        gate_reasons.append(
            f"noise_ratio {noise_ratio:.4f} > {thresholds.max_noise_ratio:.4f}"
        )

    return {
        "status": "pass" if not gate_reasons else "fail",
        "selected_file_count": len(selected),
        "required_file_count": len(required),
        "allowed_support_file_count": len(support),
        "required_symbol_count": len(required_symbols),
        "metrics": {
            "file_precision": file_precision,
            "file_recall": file_recall,
            "required_symbol_recall": required_symbol_recall,
            "noise_ratio": noise_ratio,
        },
        "selected_files": sorted(selected),
        "required_files": sorted(required),
        "covered_required_files": sorted(covered_required_files),
        "missing_required_files": sorted(required - selected),
        "allowed_support_files": sorted(support),
        "noisy_files": sorted(noisy_files),
        "required_symbol_ids": sorted(required_symbols),
        "covered_required_symbol_ids": sorted(covered_required_symbols),
        "missing_required_symbol_ids": sorted(required_symbols - selected_symbols),
        "thresholds": asdict(thresholds),
        "gate_reasons": gate_reasons,
    }


def _resolve_required_symbols(repo_root: Path, requested: Iterable[str]) -> dict:
    graph = load_graph(repo_root)
    known_ids = {str(row.get("id")) for row in graph.get("symbols", []) if row.get("id")}
    resolved_ids: set[str] = set()
    unresolved = []
    ambiguous = []

    for raw in requested:
        symbol = str(raw).strip()
        if not symbol:
            continue
        if symbol in known_ids:
            resolved_ids.add(symbol)
            continue
        result = query_symbol(repo_root, symbol)
        matches = [m.get("symbol_id") for m in result.get("matches", []) if m.get("symbol_id")]
        matches = sorted(set(matches))
        if len(matches) == 1:
            resolved_ids.add(matches[0])
        elif len(matches) > 1:
            ambiguous.append({"query": symbol, "matches": matches})
        else:
            unresolved.append(symbol)

    return {
        "resolved_ids": sorted(resolved_ids),
        "unresolved": sorted(unresolved),
        "ambiguous": ambiguous,
    }


def evaluate_task_context(
    repo_root: Path,
    task: str,
    *,
    required_files: Iterable[str],
    required_symbols: Iterable[str] | None = None,
    allowed_support_files: Iterable[str] | None = None,
    max_files: int = 8,
    depth: int = 2,
    thresholds: ContextQualityThresholds | None = None,
    refresh_graph: bool = True,
) -> dict:
    repo_root = Path(repo_root)
    if refresh_graph:
        build_graph(repo_root)
    graph = load_graph(repo_root)

    impact = impact_by_task(repo_root, task, limit=max_files, depth=depth)
    rows = impact.get("impacted_files", [])
    selected_files = [str(row.get("file")) for row in rows if row.get("file")]

    selected_symbol_ids: set[str] = set()
    file_symbols = graph.get("file_symbols", {})
    for rel in selected_files:
        selected_symbol_ids.update(str(x) for x in file_symbols.get(rel, []) if x)

    resolution = _resolve_required_symbols(repo_root, required_symbols or [])
    quality = evaluate_selection(
        selected_files,
        required_files,
        selected_symbol_ids=selected_symbol_ids,
        required_symbol_ids=resolution["resolved_ids"],
        allowed_support_files=allowed_support_files,
        thresholds=thresholds,
    )

    # Ground-truth definitions must themselves be unambiguous. Do not convert an
    # unresolved benchmark manifest into a false PASS.
    ground_truth_issues = []
    if resolution["unresolved"]:
        ground_truth_issues.append(
            "unresolved_required_symbols=" + ",".join(resolution["unresolved"])
        )
    if resolution["ambiguous"]:
        ground_truth_issues.append("ambiguous_required_symbols")
    if ground_truth_issues:
        quality["status"] = "fail"
        quality["gate_reasons"].extend(ground_truth_issues)

    return {
        "status": quality["status"],
        "task": task,
        "max_files": max_files,
        "depth": depth,
        "selection": rows,
        "selection_provenance": {
            str(row.get("file")): {
                "score": row.get("score"),
                "reasons": list(row.get("reasons", [])),
            }
            for row in rows
            if row.get("file")
        },
        "required_symbol_resolution": resolution,
        "quality": quality,
    }


def evaluate_manifest(repo_root: Path, manifest: dict) -> dict:
    default_thresholds = manifest.get("thresholds", {})
    thresholds = ContextQualityThresholds(
        min_file_recall=float(default_thresholds.get("min_file_recall", 0.95)),
        min_required_symbol_recall=float(
            default_thresholds.get("min_required_symbol_recall", 0.95)
        ),
        max_noise_ratio=float(default_thresholds.get("max_noise_ratio", 0.20)),
    )
    thresholds.validate()

    rows = []
    for item in manifest.get("tasks", []):
        row_thresholds = item.get("thresholds") or {}
        task_thresholds = ContextQualityThresholds(
            min_file_recall=float(row_thresholds.get("min_file_recall", thresholds.min_file_recall)),
            min_required_symbol_recall=float(
                row_thresholds.get(
                    "min_required_symbol_recall",
                    thresholds.min_required_symbol_recall,
                )
            ),
            max_noise_ratio=float(row_thresholds.get("max_noise_ratio", thresholds.max_noise_ratio)),
        )
        rows.append(
            evaluate_task_context(
                Path(repo_root),
                str(item["task"]),
                required_files=item.get("required_files", []),
                required_symbols=item.get("required_symbols", []),
                allowed_support_files=item.get("allowed_support_files", []),
                max_files=int(item.get("max_files", 8)),
                depth=int(item.get("depth", 2)),
                thresholds=task_thresholds,
                refresh_graph=False,
            )
        )

    metric_names = (
        "file_precision",
        "file_recall",
        "required_symbol_recall",
        "noise_ratio",
    )
    aggregate = {}
    for name in metric_names:
        values = [float(row["quality"]["metrics"][name]) for row in rows]
        aggregate[f"average_{name}"] = round(mean(values), 4) if values else 0.0

    passed = sum(1 for row in rows if row["status"] == "pass")
    return {
        "status": "pass" if rows and passed == len(rows) else "fail",
        "task_count": len(rows),
        "passed_task_count": passed,
        "failed_task_count": len(rows) - passed,
        "pass_rate": _ratio(passed, len(rows), empty_value=0.0),
        "thresholds": asdict(thresholds),
        "aggregate": aggregate,
        "tasks": rows,
    }
