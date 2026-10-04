from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import json


@dataclass(frozen=True)
class Phase3ClosurePaths:
    real_agent: str = "reports/real-agent-e2e/summary.json"
    comparative: str = "reports/comparative_ground_truth_benchmark.json"
    attestation: str = "reports/phase3/run_attestation.json"
    reliability_economics: str = "reports/phase3/reliability_economics.json"
    soak: str = "reports/phase3/soak.json"
    jev_ab: str = "reports/phase3/jev_ab.json"
    evidence_summary: str = "reports/phase3/evidence_summary.json"


REQUIRED_EVIDENCE_FLAGS = (
    "contract_v2_enforced",
    "canonical_evidence_ledger_valid",
    "claim_firewall_enforced",
    "mutation_gate_enforced",
    "outcome_verification_passed",
    "intentional_failure_rollback_verified",
    "evidence_guided_repair_verified",
    "lease_conflict_blocked",
    "attestation_verified",
    "unsupported_claims_zero",
    "false_completions_zero",
    "wrong_changes_zero",
)


def _resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, "missing"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, f"invalid_json:{type(exc).__name__}"
    if not isinstance(data, dict):
        return None, "not_object"
    return data, None


def _status_pass(report: dict[str, Any] | None) -> bool:
    return bool(report and str(report.get("status") or "").lower() == "pass")


def _real_agent_pass(report: dict[str, Any] | None) -> bool:
    if not _status_pass(report):
        return False
    executed = int(report.get("executed_count", 0) or 0)
    passed = int(report.get("passed_count", 0) or 0)
    return executed > 0 and passed == executed


def _comparative_pass(report: dict[str, Any] | None) -> bool:
    if not _status_pass(report):
        return False
    if report.get("real_provider_execution") is not True:
        return False
    if int(report.get("repeats", 0) or 0) < 3:
        return False
    return bool(str(report.get("provider") or "").strip() and str(report.get("model") or "").strip())


def _attestation_pass(report: dict[str, Any] | None) -> bool:
    """Accept only the canonical verifier result, not a caller-supplied boolean."""
    if not _status_pass(report):
        return False
    if str(report.get("reason") or "") != "attestation_verified":
        return False
    return bool(str(report.get("attestation_hash") or "").strip())


def _economics_pass(report: dict[str, Any] | None) -> bool:
    """Validate the canonical reliability-economics report schema."""
    if not report or str(report.get("status") or "").lower() != "ok":
        return False
    if str(report.get("reason") or "") != "canonical_evidence_metrics_computed":
        return False
    ledger = report.get("ledger")
    if not isinstance(ledger, dict) or str(ledger.get("status") or "").lower() != "pass":
        return False
    metrics = report.get("metrics")
    if not isinstance(metrics, dict):
        return False
    return metrics.get("verified_success_rate") is not None and metrics.get("tokens_per_verified_success") is not None


def _soak_pass(report: dict[str, Any] | None) -> bool:
    if not _status_pass(report):
        return False
    summary = report.get("summary")
    if not isinstance(summary, dict):
        return False
    iterations = int(summary.get("iterations", 0) or 0)
    critical = summary.get("critical_defects")
    if not isinstance(critical, dict):
        return False
    return iterations >= 10 and all(int(value or 0) == 0 for value in critical.values())


def _jev_ab_pass(report: dict[str, Any] | None) -> bool:
    """Validate the canonical P3.14 Jev OFF/ON evaluator output."""
    if not _status_pass(report):
        return False
    if str(report.get("method") or "") != "same-provider-model_repeated_jev_off_on_v1":
        return False
    modes = report.get("modes")
    if not isinstance(modes, list) or set(str(mode) for mode in modes) != {"jev_off", "jev_on"}:
        return False
    thresholds = report.get("thresholds")
    if not isinstance(thresholds, dict):
        return False
    try:
        min_repeats = int(thresholds.get("min_repeats", 0) or 0)
    except (TypeError, ValueError):
        return False
    if min_repeats < 3:
        return False
    summaries = report.get("summaries")
    if not isinstance(summaries, dict) or not {"jev_off", "jev_on"}.issubset(summaries):
        return False
    for mode in ("jev_off", "jev_on"):
        summary = summaries.get(mode)
        if not isinstance(summary, dict):
            return False
        try:
            runs = int(summary.get("runs", 0) or 0)
        except (TypeError, ValueError):
            return False
        if runs < min_repeats:
            return False
    checks = report.get("checks")
    if not isinstance(checks, dict) or not checks or not all(value is True for value in checks.values()):
        return False
    observations = report.get("observations")
    return isinstance(observations, list) and len(observations) >= (2 * min_repeats)


def _evidence_summary_pass(report: dict[str, Any] | None) -> tuple[bool, list[str]]:
    if not report:
        return False, list(REQUIRED_EVIDENCE_FLAGS)
    missing = [flag for flag in REQUIRED_EVIDENCE_FLAGS if report.get(flag) is not True]
    return not missing, missing


def evaluate_phase3_closure(
    repo_root: Path,
    *,
    paths: Phase3ClosurePaths | None = None,
) -> dict[str, Any]:
    """Strict Phase-3 closure evaluator.

    The evaluator never fabricates evidence and never executes workloads. It only
    validates already-produced deterministic/real-run reports. Missing or malformed
    mandatory evidence is a hard closure failure.
    """
    root = Path(repo_root).resolve()
    paths = paths or Phase3ClosurePaths()
    reports: dict[str, dict[str, Any] | None] = {}
    load_errors: dict[str, str] = {}

    for name, relative in asdict(paths).items():
        report, error = _read_json(_resolve(root, str(relative)))
        reports[name] = report
        if error is not None:
            load_errors[name] = error

    evidence_ok, missing_flags = _evidence_summary_pass(reports["evidence_summary"])
    checks = {
        "real_agent_e2e": _real_agent_pass(reports["real_agent"]),
        "real_comparative_benchmark": _comparative_pass(reports["comparative"]),
        "run_attestation": _attestation_pass(reports["attestation"]),
        "reliability_economics": _economics_pass(reports["reliability_economics"]),
        "sustained_reliability_soak": _soak_pass(reports["soak"]),
        "jev_off_on_comparison": _jev_ab_pass(reports["jev_ab"]),
        "phase3_evidence_summary": evidence_ok,
    }

    blockers = [f"missing_or_invalid_report:{name}:{reason}" for name, reason in sorted(load_errors.items())]
    blockers.extend(f"required_evidence_flag_not_true:{flag}" for flag in missing_flags)
    blockers.extend(f"closure_check_failed:{name}" for name, ok in checks.items() if not ok)
    blockers = sorted(set(blockers))

    status = "pass" if not blockers and all(checks.values()) else "fail"
    return {
        "status": status,
        "method": "phase3_strict_evidence_closure_v1",
        "checks": checks,
        "blockers": blockers,
        "required_evidence_flags": list(REQUIRED_EVIDENCE_FLAGS),
        "paths": asdict(paths),
        "claim": "Phase 3 closes only when real-agent execution, real comparative evidence, canonically verified attestation, evidence-ledger reliability economics, sustained soak, repeated Jev OFF/ON comparison, and all required safety evidence flags are present and passing.",
    }
