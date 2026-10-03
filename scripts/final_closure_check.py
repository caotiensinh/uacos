from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_REAL_AGENT = Path("reports/real-agent-e2e/summary.json")
DEFAULT_COMPARATIVE = Path("reports/comparative_ground_truth_benchmark.json")


def _load_json(path: Path) -> tuple[dict | None, str | None]:
    if not path.exists():
        return None, "missing"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, f"invalid_json:{exc.__class__.__name__}"
    if not isinstance(data, dict):
        return None, "not_object"
    return data, None


def _real_comparative_pass(report: dict | None) -> bool:
    if not report or report.get("status") != "pass":
        return False
    if report.get("real_provider_execution") is not True:
        return False
    if not str(report.get("provider") or "").strip():
        return False
    if not str(report.get("model") or "").strip():
        return False
    if int(report.get("repeats", 0) or 0) < 3:
        return False
    return True


def evaluate_closure(
    repo_root: Path,
    *,
    real_agent_report: Path | None = None,
    comparative_report: Path | None = None,
    strict_evidence: bool = False,
) -> dict:
    root = Path(repo_root).resolve()
    real_path = (real_agent_report or DEFAULT_REAL_AGENT)
    comp_path = (comparative_report or DEFAULT_COMPARATIVE)
    if not real_path.is_absolute():
        real_path = root / real_path
    if not comp_path.is_absolute():
        comp_path = root / comp_path

    real, real_error = _load_json(real_path)
    comparative, comp_error = _load_json(comp_path)

    real_pass = bool(
        real
        and real.get("status") == "pass"
        and int(real.get("executed_count", 0) or 0) > 0
        and int(real.get("passed_count", 0) or 0) == int(real.get("executed_count", 0) or 0)
    )
    comparative_pass = _real_comparative_pass(comparative)

    checks = {
        "real_agent_report_present": real_error is None,
        "real_agent_provider_execution_passed": real_pass,
        "comparative_report_present": comp_error is None,
        "comparative_benchmark_passed": comparative_pass,
        "comparative_real_provider_execution": bool(comparative and comparative.get("real_provider_execution") is True),
        "comparative_minimum_repeats": bool(comparative and int(comparative.get("repeats", 0) or 0) >= 3),
    }

    blockers: list[str] = []
    if real_error:
        blockers.append(f"real_agent_report:{real_error}")
    elif not real_pass:
        blockers.append("real_agent_provider_execution_not_passed")
    if comp_error:
        blockers.append(f"comparative_report:{comp_error}")
    elif not comparative_pass:
        blockers.append("real_comparative_benchmark_not_passed")

    implementation_status = "pass"
    evidence_status = "pass" if not blockers else "incomplete"
    status = "pass" if implementation_status == "pass" and (not strict_evidence or evidence_status == "pass") else "fail"

    return {
        "status": status,
        "implementation_status": implementation_status,
        "evidence_status": evidence_status,
        "strict_evidence": strict_evidence,
        "checks": checks,
        "blockers": blockers,
        "real_agent_report": str(real_path),
        "comparative_report": str(comp_path),
        "claim": "Implementation readiness is separate from real-world evidence. Strict closure passes only when real-provider E2E and a provenance-marked repeated real-provider comparative benchmark both pass.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check UACOS final closure evidence without conflating implementation readiness and real-world proof.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--real-agent-report", default=str(DEFAULT_REAL_AGENT))
    parser.add_argument("--comparative-report", default=str(DEFAULT_COMPARATIVE))
    parser.add_argument("--strict-evidence", action="store_true")
    parser.add_argument("--report", default="reports/final_closure_report.json")
    args = parser.parse_args()

    root = Path(args.repo).resolve()
    result = evaluate_closure(
        root,
        real_agent_report=Path(args.real_agent_report),
        comparative_report=Path(args.comparative_report),
        strict_evidence=args.strict_evidence,
    )
    out = Path(args.report)
    if not out.is_absolute():
        out = root / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
