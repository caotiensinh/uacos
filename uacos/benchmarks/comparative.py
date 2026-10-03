from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from statistics import mean
from typing import Any


BASELINE_MODES = ("full_repo", "grep", "uacos")


@dataclass(frozen=True)
class BenchmarkThresholds:
    min_required_symbol_recall: float = 0.95
    max_noise_rate: float = 0.20
    min_repeats: int = 3


def _ratio(numerator: int, denominator: int, *, empty_value: float = 1.0) -> float:
    if denominator <= 0:
        return empty_value
    return numerator / denominator


def _set(values: Any) -> set[str]:
    if values is None:
        return set()
    if not isinstance(values, list):
        raise ValueError("benchmark_list_expected")
    return {str(value) for value in values}


def _avg(rows: list[dict], key: str) -> float:
    values = [float(row.get(key, 0) or 0) for row in rows]
    return round(mean(values), 4) if values else 0.0


def validate_inputs(manifest: dict, observations: list[dict]) -> None:
    if int(manifest.get("version", 0)) != 1:
        raise ValueError("unsupported_benchmark_manifest_version")
    tasks = manifest.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("benchmark_tasks_required")
    ids = [str(task.get("id") or "") for task in tasks]
    if any(not task_id for task_id in ids) or len(ids) != len(set(ids)):
        raise ValueError("benchmark_task_ids_invalid")
    if not isinstance(observations, list) or not observations:
        raise ValueError("benchmark_observations_required")


def score_observation(task: dict, row: dict) -> dict:
    required_symbols = _set(task.get("required_symbols"))
    required_relations = _set(task.get("required_relations"))
    selected_symbols = _set(row.get("selected_symbols"))
    selected_relations = _set(row.get("selected_relations"))

    required_symbol_hits = required_symbols & selected_symbols
    required_relation_hits = required_relations & selected_relations
    noise_symbols = selected_symbols - required_symbols

    return {
        **row,
        "required_symbol_recall": round(_ratio(len(required_symbol_hits), len(required_symbols)), 4),
        "required_relation_recall": round(_ratio(len(required_relation_hits), len(required_relations)), 4),
        "noise_rate": round(_ratio(len(noise_symbols), len(selected_symbols), empty_value=0.0), 4),
        "missing_required_symbols": sorted(required_symbols - selected_symbols),
        "missing_required_relations": sorted(required_relations - selected_relations),
    }


def _mode_summary(rows: list[dict]) -> dict:
    passed = [row for row in rows if bool(row.get("passed"))]
    first_pass = [row for row in rows if bool(row.get("passed")) and int(row.get("retries", 0) or 0) == 0]
    return {
        "runs": len(rows),
        "pass_rate": round(_ratio(len(passed), len(rows), empty_value=0.0), 4),
        "first_pass_rate": round(_ratio(len(first_pass), len(rows), empty_value=0.0), 4),
        "avg_retries": _avg(rows, "retries"),
        "avg_tool_calls": _avg(rows, "tool_calls"),
        "avg_input_tokens": _avg(rows, "input_tokens"),
        "avg_total_tokens": _avg(rows, "total_tokens"),
        "avg_latency_ms": _avg(rows, "latency_ms"),
        "avg_index_overhead_ms": _avg(rows, "index_overhead_ms"),
        "required_symbol_recall": _avg(rows, "required_symbol_recall"),
        "required_relation_recall": _avg(rows, "required_relation_recall"),
        "noise_rate": _avg(rows, "noise_rate"),
    }


def evaluate_comparative_benchmark(
    manifest: dict,
    observations: list[dict],
    *,
    thresholds: BenchmarkThresholds | None = None,
) -> dict:
    validate_inputs(manifest, observations)
    thresholds = thresholds or BenchmarkThresholds()
    tasks = {str(task["id"]): task for task in manifest["tasks"]}

    scored: list[dict] = []
    findings: list[str] = []
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)

    for row in observations:
        task_id = str(row.get("task_id") or "")
        mode = str(row.get("mode") or "")
        if task_id not in tasks:
            findings.append(f"unknown_task:{task_id}")
            continue
        if mode not in BASELINE_MODES:
            findings.append(f"unknown_mode:{mode}")
            continue
        scored_row = score_observation(tasks[task_id], row)
        scored.append(scored_row)
        groups[(task_id, mode)].append(scored_row)

    providers_by_task: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for row in scored:
        providers_by_task[str(row["task_id"])].add((str(row.get("provider") or ""), str(row.get("model") or "")))

    for task_id, providers in providers_by_task.items():
        if len(providers) != 1:
            findings.append(f"provider_or_model_mismatch:{task_id}")

    for task_id in tasks:
        for mode in BASELINE_MODES:
            rows = groups.get((task_id, mode), [])
            if len(rows) < thresholds.min_repeats:
                findings.append(f"insufficient_repeats:{task_id}:{mode}:{len(rows)}")
            repeats = [int(row.get("repeat", 0) or 0) for row in rows]
            if repeats and len(repeats) != len(set(repeats)):
                findings.append(f"duplicate_repeat:{task_id}:{mode}")

    mode_rows: dict[str, list[dict]] = {mode: [] for mode in BASELINE_MODES}
    for row in scored:
        mode_rows[str(row["mode"])].append(row)
    summaries = {mode: _mode_summary(mode_rows[mode]) for mode in BASELINE_MODES}

    uacos = summaries["uacos"]
    full_repo = summaries["full_repo"]
    target_checks = {
        "required_symbol_recall": uacos["required_symbol_recall"] >= thresholds.min_required_symbol_recall,
        "noise_rate": uacos["noise_rate"] <= thresholds.max_noise_rate,
        "pass_rate_not_below_full_repo": uacos["pass_rate"] >= full_repo["pass_rate"],
        "input_tokens_below_full_repo": uacos["avg_input_tokens"] < full_repo["avg_input_tokens"],
    }

    status = "pass" if not findings and all(target_checks.values()) else "fail"
    return {
        "status": status,
        "method": "same-provider-model_repeated_ground_truth_v1",
        "modes": list(BASELINE_MODES),
        "thresholds": {
            "min_required_symbol_recall": thresholds.min_required_symbol_recall,
            "max_noise_rate": thresholds.max_noise_rate,
            "min_repeats": thresholds.min_repeats,
        },
        "findings": sorted(set(findings)),
        "target_checks": target_checks,
        "summaries": summaries,
        "observations": scored,
        "claim": "A PASS requires the same provider/model across modes, at least three repeats per task/mode, preserved required-symbol recall, bounded noise, no pass-rate regression versus full-repo, and lower input tokens than full-repo.",
    }
