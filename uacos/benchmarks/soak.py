from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import mean
from typing import Any


CRITICAL_BOOL_FIELDS = (
    "false_completion",
    "unsupported_claim",
    "bad_commit",
    "rollback_failed",
    "leaked_process",
    "stale_state",
    "corrupted_evidence",
    "lease_conflict_unblocked",
)


@dataclass(frozen=True)
class SoakThresholds:
    min_iterations: int = 10
    min_verified_success_rate: float = 0.95
    max_token_drift_ratio: float = 0.20
    max_latency_drift_ratio: float = 0.30


def _ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator <= 0:
        return None
    return float(numerator) / float(denominator)


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


def _drift(first: float | None, last: float | None) -> float | None:
    if first is None or last is None or first <= 0:
        return None
    return round((last - first) / first, 6)


def evaluate_sustained_reliability(
    observations: list[dict[str, Any]],
    *,
    thresholds: SoakThresholds | None = None,
) -> dict[str, Any]:
    """Evaluate repeated-run reliability observations without executing workloads.

    This evaluator is intentionally deterministic. It does not fabricate workload
    evidence or declare runtime success on its own; callers must supply observations
    collected from real/replay test runs. Any critical safety defect fails the soak.
    """
    thresholds = thresholds or SoakThresholds()
    if thresholds.min_iterations <= 0:
        raise ValueError("min_iterations_must_be_positive")
    if not 0 <= thresholds.min_verified_success_rate <= 1:
        raise ValueError("min_verified_success_rate_out_of_range")
    if thresholds.max_token_drift_ratio < 0 or thresholds.max_latency_drift_ratio < 0:
        raise ValueError("drift_threshold_must_be_nonnegative")
    if not isinstance(observations, list) or not observations:
        raise ValueError("soak_observations_required")

    normalized: list[dict[str, Any]] = []
    findings: list[str] = []
    seen_iterations: set[int] = set()
    for index, row in enumerate(observations, start=1):
        if not isinstance(row, dict):
            findings.append(f"invalid_observation:{index}")
            continue
        try:
            iteration = int(row.get("iteration", index))
        except (TypeError, ValueError):
            findings.append(f"invalid_iteration:{index}")
            continue
        if iteration <= 0:
            findings.append(f"invalid_iteration:{iteration}")
            continue
        if iteration in seen_iterations:
            findings.append(f"duplicate_iteration:{iteration}")
        seen_iterations.add(iteration)

        status = str(row.get("status") or "").strip().lower()
        if status not in {"pass", "fail", "blocked"}:
            findings.append(f"invalid_status:{iteration}:{status or 'missing'}")
        normalized_row = {**row, "iteration": iteration, "status": status}
        normalized.append(normalized_row)

    normalized.sort(key=lambda row: int(row["iteration"]))
    if len(normalized) < thresholds.min_iterations:
        findings.append(f"insufficient_iterations:{len(normalized)}:{thresholds.min_iterations}")

    verified_successes = sum(1 for row in normalized if row.get("status") == "pass")
    verified_failures = sum(1 for row in normalized if row.get("status") == "fail")
    blocked = sum(1 for row in normalized if row.get("status") == "blocked")
    success_rate = _ratio(verified_successes, len(normalized))

    critical_counts: dict[str, int] = {}
    for field in CRITICAL_BOOL_FIELDS:
        count = sum(1 for row in normalized if bool(row.get(field)))
        critical_counts[field] = count
        if count:
            findings.append(f"critical_defect:{field}:{count}")

    midpoint = max(1, len(normalized) // 2)
    first_half = normalized[:midpoint]
    second_half = normalized[midpoint:] or normalized[:midpoint]
    first_tokens = _avg(first_half, "total_tokens")
    last_tokens = _avg(second_half, "total_tokens")
    first_latency = _avg(first_half, "latency_ms")
    last_latency = _avg(second_half, "latency_ms")
    token_drift = _drift(first_tokens, last_tokens)
    latency_drift = _drift(first_latency, last_latency)

    checks = {
        "minimum_iterations": len(normalized) >= thresholds.min_iterations,
        "verified_success_rate": success_rate is not None and success_rate >= thresholds.min_verified_success_rate,
        "zero_critical_defects": all(count == 0 for count in critical_counts.values()),
        "token_drift_bounded": token_drift is None or token_drift <= thresholds.max_token_drift_ratio,
        "latency_drift_bounded": latency_drift is None or latency_drift <= thresholds.max_latency_drift_ratio,
    }
    if success_rate is None or success_rate < thresholds.min_verified_success_rate:
        findings.append("verified_success_rate_below_threshold")
    if token_drift is not None and token_drift > thresholds.max_token_drift_ratio:
        findings.append("token_drift_above_threshold")
    if latency_drift is not None and latency_drift > thresholds.max_latency_drift_ratio:
        findings.append("latency_drift_above_threshold")

    unavailable: dict[str, str] = {}
    if first_tokens is None or last_tokens is None:
        unavailable["token_drift_ratio"] = "observations missing total_tokens"
    if first_latency is None or last_latency is None:
        unavailable["latency_drift_ratio"] = "observations missing latency_ms"

    status = "pass" if normalized and not findings and all(checks.values()) else "fail"
    return {
        "status": status,
        "method": "repeated_observation_sustained_reliability_v1",
        "thresholds": asdict(thresholds),
        "summary": {
            "iterations": len(normalized),
            "verified_successes": verified_successes,
            "verified_failures": verified_failures,
            "blocked": blocked,
            "verified_success_rate": None if success_rate is None else round(success_rate, 6),
            "critical_defects": critical_counts,
            "first_half_avg_tokens": first_tokens,
            "second_half_avg_tokens": last_tokens,
            "token_drift_ratio": token_drift,
            "first_half_avg_latency_ms": first_latency,
            "second_half_avg_latency_ms": last_latency,
            "latency_drift_ratio": latency_drift,
        },
        "checks": checks,
        "findings": sorted(set(findings)),
        "unavailable_metrics": unavailable,
        "observations": normalized,
        "claim": "PASS requires the minimum repeated observations, required verified-success rate, zero critical safety defects, and bounded token/latency drift when those measurements are present.",
    }
