from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any


MODES = ("jev_off", "jev_on")


def _avg(rows: list[dict[str, Any]], key: str) -> float | None:
    values: list[float] = []
    for row in rows:
        raw = row.get(key)
        if raw is None:
            continue
        try:
            values.append(float(raw))
        except (TypeError, ValueError):
            continue
    return round(mean(values), 6) if values else None


def _rate(rows: list[dict[str, Any]], predicate) -> float | None:
    if not rows:
        return None
    return round(sum(1 for row in rows if predicate(row)) / len(rows), 6)


def evaluate_jev_ab(
    observations: list[dict[str, Any]],
    *,
    min_repeats: int = 3,
    max_verified_success_regression: float = 0.0,
    max_token_increase_ratio: float = 0.10,
    max_latency_increase_ratio: float = 0.50,
) -> dict[str, Any]:
    """Evaluate Jev OFF vs ON observations without running a provider.

    Every task must use the same provider/model in both modes and include repeated
    observations. The evaluator never upgrades model output into verification; it
    consumes externally produced deterministic outcome fields only.
    """
    if min_repeats <= 0:
        raise ValueError("min_repeats_must_be_positive")
    if max_verified_success_regression < 0:
        raise ValueError("max_verified_success_regression_must_be_nonnegative")
    if max_token_increase_ratio < 0 or max_latency_increase_ratio < 0:
        raise ValueError("increase_threshold_must_be_nonnegative")
    if not isinstance(observations, list) or not observations:
        raise ValueError("jev_ab_observations_required")

    findings: list[str] = []
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    provider_models: dict[str, set[tuple[str, str]]] = defaultdict(set)
    seen: set[tuple[str, str, int]] = set()

    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(observations, start=1):
        if not isinstance(raw, dict):
            findings.append(f"invalid_observation:{index}")
            continue
        task_id = str(raw.get("task_id") or "").strip()
        mode = str(raw.get("mode") or "").strip()
        provider = str(raw.get("provider") or "").strip()
        model = str(raw.get("model") or "").strip()
        if not task_id:
            findings.append(f"missing_task_id:{index}")
            continue
        if mode not in MODES:
            findings.append(f"unknown_mode:{task_id}:{mode or 'missing'}")
            continue
        try:
            repeat = int(raw.get("repeat", 0))
        except (TypeError, ValueError):
            findings.append(f"invalid_repeat:{task_id}:{mode}")
            continue
        if repeat <= 0:
            findings.append(f"invalid_repeat:{task_id}:{mode}:{repeat}")
            continue
        key = (task_id, mode, repeat)
        if key in seen:
            findings.append(f"duplicate_repeat:{task_id}:{mode}:{repeat}")
        seen.add(key)
        row = dict(raw)
        row.update({"task_id": task_id, "mode": mode, "provider": provider, "model": model, "repeat": repeat})
        normalized.append(row)
        groups[(task_id, mode)].append(row)
        provider_models[task_id].add((provider, model))

    task_ids = sorted({task_id for task_id, _ in groups})
    for task_id in task_ids:
        if len(provider_models[task_id]) != 1:
            findings.append(f"provider_or_model_mismatch:{task_id}")
        for mode in MODES:
            count = len(groups.get((task_id, mode), []))
            if count < min_repeats:
                findings.append(f"insufficient_repeats:{task_id}:{mode}:{count}")

    summaries: dict[str, dict[str, Any]] = {}
    for mode in MODES:
        rows = [row for row in normalized if row["mode"] == mode]
        summaries[mode] = {
            "runs": len(rows),
            "verified_success_rate": _rate(rows, lambda row: str(row.get("verified_status") or "").lower() == "pass"),
            "fallback_rate": _rate(rows, lambda row: bool(row.get("fallback_used"))),
            "avg_total_tokens": _avg(rows, "total_tokens"),
            "avg_latency_ms": _avg(rows, "latency_ms"),
            "avg_ranking_quality": _avg(rows, "ranking_quality"),
        }

    off = summaries["jev_off"]
    on = summaries["jev_on"]

    checks: dict[str, bool] = {}
    off_success = off["verified_success_rate"]
    on_success = on["verified_success_rate"]
    if off_success is None or on_success is None:
        checks["verified_success_not_regressed"] = False
        findings.append("verified_success_rate_unavailable")
    else:
        checks["verified_success_not_regressed"] = on_success + max_verified_success_regression >= off_success
        if not checks["verified_success_not_regressed"]:
            findings.append("verified_success_regressed")

    off_tokens = off["avg_total_tokens"]
    on_tokens = on["avg_total_tokens"]
    if off_tokens is None or on_tokens is None or off_tokens <= 0:
        checks["token_cost_bounded"] = False
        findings.append("token_cost_unavailable")
        token_delta_ratio = None
    else:
        token_delta_ratio = round((on_tokens - off_tokens) / off_tokens, 6)
        checks["token_cost_bounded"] = token_delta_ratio <= max_token_increase_ratio
        if not checks["token_cost_bounded"]:
            findings.append("token_cost_increase_above_threshold")

    off_latency = off["avg_latency_ms"]
    on_latency = on["avg_latency_ms"]
    if off_latency is None or on_latency is None or off_latency <= 0:
        checks["latency_cost_bounded"] = False
        findings.append("latency_unavailable")
        latency_delta_ratio = None
    else:
        latency_delta_ratio = round((on_latency - off_latency) / off_latency, 6)
        checks["latency_cost_bounded"] = latency_delta_ratio <= max_latency_increase_ratio
        if not checks["latency_cost_bounded"]:
            findings.append("latency_increase_above_threshold")

    off_quality = off["avg_ranking_quality"]
    on_quality = on["avg_ranking_quality"]
    if off_quality is None or on_quality is None:
        checks["ranking_quality_not_regressed"] = False
        findings.append("ranking_quality_unavailable")
    else:
        checks["ranking_quality_not_regressed"] = on_quality >= off_quality
        if not checks["ranking_quality_not_regressed"]:
            findings.append("ranking_quality_regressed")

    status = "pass" if normalized and not findings and all(checks.values()) else "fail"
    return {
        "status": status,
        "method": "same-provider-model_repeated_jev_off_on_v1",
        "modes": list(MODES),
        "thresholds": {
            "min_repeats": min_repeats,
            "max_verified_success_regression": max_verified_success_regression,
            "max_token_increase_ratio": max_token_increase_ratio,
            "max_latency_increase_ratio": max_latency_increase_ratio,
        },
        "summaries": summaries,
        "deltas": {
            "token_delta_ratio": token_delta_ratio,
            "latency_delta_ratio": latency_delta_ratio,
        },
        "checks": checks,
        "findings": sorted(set(findings)),
        "observations": normalized,
        "claim": "PASS requires same provider/model, repeated Jev OFF/ON observations, no verified-success regression beyond threshold, bounded token/latency cost, and no ranking-quality regression.",
    }
