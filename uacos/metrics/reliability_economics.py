from __future__ import annotations

from pathlib import Path
from typing import Any

from uacos.execution.evidence_ledger import read_evidence_ledger, verify_evidence_ledger


def _ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator <= 0:
        return None
    return round(float(numerator) / float(denominator), 6)


def _row_tokens(row: dict[str, Any]) -> int:
    usage = row.get("token_usage") or {}
    try:
        value = int(usage.get("total_tokens", 0))
    except (TypeError, ValueError):
        return 0
    return max(0, value)


def collect_reliability_economics(repo_root: Path) -> dict[str, Any]:
    """Compute Phase-3 reliability economics from the canonical evidence ledger.

    Metrics are intentionally evidence-derived. Missing denominators are reported as
    None instead of optimistic zeroes, and a corrupt ledger fails the report closed.
    """
    root = Path(repo_root)
    integrity = verify_evidence_ledger(root)
    if integrity.get("status") != "pass":
        return {
            "status": "fail",
            "reason": "evidence_ledger_invalid",
            "ledger": integrity,
            "metrics": None,
        }

    rows = read_evidence_ledger(root)

    latest_verdict_by_run: dict[str, dict[str, Any]] = {}
    token_rows: list[dict[str, Any]] = []
    recovery_rows: list[dict[str, Any]] = []
    for row in rows:
        event_type = str(row.get("event_type") or "")
        run_id = str(row.get("run_id") or "").strip()
        if event_type == "outcome_verdict" and run_id:
            latest_verdict_by_run[run_id] = row
        elif event_type == "token_usage_settled":
            token_rows.append(row)
        elif event_type == "recovery_decision":
            recovery_rows.append(row)

    verdicts = list(latest_verdict_by_run.values())
    pass_runs = sum(1 for row in verdicts if str(row.get("status") or "").lower() == "pass")
    fail_runs = sum(1 for row in verdicts if str(row.get("status") or "").lower() == "fail")
    other_verdict_runs = len(verdicts) - pass_runs - fail_runs

    total_tokens = sum(_row_tokens(row) for row in token_rows)
    retry_tokens = sum(
        _row_tokens(row)
        for row in token_rows
        if int((row.get("data") or {}).get("repair_attempt", 0) or 0) > 0
        or bool((row.get("data") or {}).get("retry", False))
    )

    recovery_actions: dict[str, int] = {}
    mutation_failures = 0
    rollback_verified = 0
    repeated_failures = 0
    repair_decisions = 0
    for row in recovery_rows:
        data = row.get("data") or {}
        decision = data.get("decision") or {}
        action = str(decision.get("action") or row.get("status") or "UNKNOWN").upper()
        recovery_actions[action] = recovery_actions.get(action, 0) + 1
        if action == "REPAIR":
            repair_decisions += 1
        if bool(data.get("repeated_failure")):
            repeated_failures += 1
        if bool(data.get("real_failure_observed")) and bool(data.get("mutation_applied")):
            mutation_failures += 1
            if bool(data.get("rollback_verified")):
                rollback_verified += 1

    metrics = {
        "verified_runs": len(verdicts),
        "verified_successes": pass_runs,
        "verified_failures": fail_runs,
        "other_verdict_runs": other_verdict_runs,
        "verified_success_rate": _ratio(pass_runs, len(verdicts)),
        "total_settled_tokens": total_tokens,
        "token_settlement_events": len(token_rows),
        "tokens_per_verified_run": _ratio(total_tokens, len(verdicts)),
        "tokens_per_verified_success": _ratio(total_tokens, pass_runs),
        "retry_tokens": retry_tokens,
        "retry_token_ratio": _ratio(retry_tokens, total_tokens),
        "recovery_decisions": len(recovery_rows),
        "recovery_actions": dict(sorted(recovery_actions.items())),
        "repair_decisions": repair_decisions,
        "repeated_failures": repeated_failures,
        "mutation_failures_requiring_rollback": mutation_failures,
        "verified_rollbacks": rollback_verified,
        "rollback_success_rate": _ratio(rollback_verified, mutation_failures),
    }

    unavailable = {
        "false_completion_rate": "requires canonical claim-to-outcome correlation events",
        "unsupported_claim_rate": "requires canonical claim-firewall event accounting",
        "wrong_change_rate": "requires canonical accepted-change correctness labels",
        "human_intervention_rate": "requires canonical human-intervention events",
        "cost_per_verified_success": "requires canonical cost events, not estimates from unrelated stores",
    }

    return {
        "status": "ok",
        "reason": "canonical_evidence_metrics_computed",
        "ledger": integrity,
        "metrics": metrics,
        "unavailable_metrics": unavailable,
    }
