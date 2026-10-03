from __future__ import annotations

from copy import deepcopy
import hashlib
import json

MAX_SAFE_ITERATIONS = 10
DEFAULT_ITERATIONS = 3
MAX_SAFE_TOOL_CALLS = 500
MAX_SAFE_TOKENS = 2_000_000

CORE_PILLARS = [
    {
        "id": "token_prompt_optimization",
        "name": "Token and prompt optimization",
        "description": "Select relevant files, compress context, reuse memory/skills, and keep prompts bounded before any agent run.",
    },
    {
        "id": "safe_code_change",
        "name": "Safe code change and upgrade",
        "description": "Validate scope, scan secrets, checkpoint files, run tests, and roll back failed changes.",
    },
    {
        "id": "agent_code_coordination",
        "name": "Agent-code coordination layer",
        "description": "Coordinate external agents and codebase operations without becoming a general-purpose agent itself.",
    },
    {
        "id": "spec_driven_devops_loop",
        "name": "Spec-driven DevOps loop",
        "description": "Repeat plan -> code -> test -> record -> improve only within explicit bounds until the user spec passes or the loop is exhausted.",
    },
]

LOOP_STEPS = [
    {
        "id": "read_spec",
        "purpose": "Capture the user-desired product spec, acceptance checks, and non-goals.",
        "writes_code": False,
        "evidence": ["spec_summary", "acceptance_criteria"],
    },
    {
        "id": "prepare_context",
        "purpose": "Build impact ranking and compressed context before delegating work.",
        "writes_code": False,
        "evidence": ["selected_files", "compressed_tokens_est", "token_savings_est"],
    },
    {
        "id": "delegate_agent",
        "purpose": "Give a bounded task/context package to an external agent or manual workflow.",
        "writes_code": False,
        "evidence": ["agent_name", "prompt_file_or_context_id"],
    },
    {
        "id": "validate_patch",
        "purpose": "Reject unsafe or out-of-scope patches before touching the working tree.",
        "writes_code": False,
        "evidence": ["patch_gate_status", "secret_scan_status", "impact_alignment_status"],
    },
    {
        "id": "apply_and_test",
        "purpose": "Apply only validated patches, run tests, and roll back automatically on failure.",
        "writes_code": True,
        "evidence": ["transaction_id", "test_results", "rollback_status_if_failed"],
    },
    {
        "id": "record_result",
        "purpose": "Record what changed, what passed, what failed, and what should be improved next.",
        "writes_code": False,
        "evidence": ["iteration_report", "lessons_learned", "remaining_gap"],
    },
    {
        "id": "stop_or_improve",
        "purpose": "Stop if the spec is satisfied; otherwise continue only while the iteration budget remains.",
        "writes_code": False,
        "evidence": ["spec_satisfied", "iterations_remaining", "next_action"],
    },
]

SAFETY_INVARIANTS = [
    "No unbounded loop is allowed; every loop must have max_iterations.",
    "No patch application without explicit scope and validation.",
    "No claim of done without tests or explicit validation evidence.",
    "No network exposure beyond localhost for MCP by default.",
    "No rewrite of stable UACOS core engines unless a failing test proves it is necessary.",
    "If the loop exhausts max_iterations without satisfying the spec, stop and return a decision report instead of continuing silently.",
]

STOP_CONDITIONS = [
    "acceptance_criteria_passed",
    "release_gate_passed_when_required",
    "max_iterations_exhausted",
    "scope_expansion_required",
    "unsafe_patch_blocked",
    "human_decision_required",
]


def _bounded_iterations(value) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError):
        n = DEFAULT_ITERATIONS
    if n < 1:
        return DEFAULT_ITERATIONS
    return min(n, MAX_SAFE_ITERATIONS)


def _bounded_nonnegative(value, maximum: int, default: int | None = None) -> int | None:
    if value is None:
        return default
    try:
        n = int(value)
    except (TypeError, ValueError):
        return default
    if n < 0:
        return default
    return min(n, maximum)


def _clean_strings(values: list[str] | None) -> list[str]:
    return [str(v).strip() for v in (values or []) if str(v).strip()]


def _stable_plan_id(payload: dict) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return "ORCH-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def _stable_contract_id(payload: dict) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "CONTRACT-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def get_orchestration_contract(section: str | None = None) -> dict:
    contract = {
        "status": "ok",
        "role": "coordination_layer_not_agent",
        "core_pillars": deepcopy(CORE_PILLARS),
        "loop_steps": deepcopy(LOOP_STEPS),
        "safety_invariants": list(SAFETY_INVARIANTS),
        "stop_conditions": list(STOP_CONDITIONS),
        "defaults": {
            "default_iterations": DEFAULT_ITERATIONS,
            "max_safe_iterations": MAX_SAFE_ITERATIONS,
            "requires_tests_for_done": True,
            "requires_recorded_evidence": True,
        },
        "phase3_contract_v2": {
            "machine_readable_done": True,
            "required_sections": [
                "scope",
                "success_conditions",
                "required_evidence",
                "budgets",
                "approval",
            ],
            "done_states": ["done", "not_done", "unknown"],
            "fail_closed_on_missing_required_evidence": True,
        },
    }
    if section is None:
        return contract
    if section not in contract:
        return {
            "status": "error",
            "reason": "unknown_section",
            "section": section,
            "available_sections": sorted(contract.keys()),
        }
    return {"status": "ok", section: contract[section]}


def build_orchestration_plan(spec: str, agents: list[str] | None = None, tests: list[str] | None = None, max_iterations: int | None = None) -> dict:
    spec = (spec or "").strip()
    if not spec:
        return {"status": "error", "reason": "spec_required"}

    bounded_iterations = _bounded_iterations(max_iterations)
    tests = _clean_strings(tests)
    agents = _clean_strings(agents)

    warnings = []
    if not tests:
        warnings.append("tests_missing_done_will_be_blocked")
    if not agents:
        agents = ["manual_or_configured_agent"]

    payload = {
        "spec": spec,
        "agents": agents,
        "tests": tests,
        "max_iterations": bounded_iterations,
    }
    plan_id = _stable_plan_id(payload)

    return {
        "status": "ok",
        "plan_id": plan_id,
        "spec": spec,
        "role": "orchestrate_agents_and_code_do_not_act_as_general_agent",
        "agents": agents,
        "tests": tests,
        "max_iterations": bounded_iterations,
        "warnings": warnings,
        "loop": [
            {
                "iteration": i,
                "steps": [step["id"] for step in LOOP_STEPS],
                "must_record": ["context_report", "patch_report", "test_report", "decision_report"],
            }
            for i in range(1, bounded_iterations + 1)
        ],
        "stop_conditions": list(STOP_CONDITIONS),
        "done_requires": [
            "acceptance_criteria_passed",
            "tests_passed_or_explicit_validation_evidence",
            "result_recorded",
        ],
    }


def build_task_contract_v2(
    spec: str,
    *,
    allowed_files: list[str] | None = None,
    allowed_dirs: list[str] | None = None,
    forbidden_side_effects: list[str] | None = None,
    required_tests: list[str] | None = None,
    required_evidence: list[str] | None = None,
    runtime_checks: list[str] | None = None,
    outcome_checks: list[str] | None = None,
    max_iterations: int | None = None,
    max_tokens: int | None = None,
    max_tool_calls: int | None = None,
    human_approval_conditions: list[str] | None = None,
) -> dict:
    """Build an additive Phase-3 task contract without changing legacy orchestration APIs.

    The contract is declarative. It does not execute tests, mutate the repository, or trust
    an agent's completion claim. Final completion must be computed by evaluate_done_predicate().
    """
    spec = (spec or "").strip()
    if not spec:
        return {"status": "error", "reason": "spec_required"}

    tests = _clean_strings(required_tests)
    evidence = _clean_strings(required_evidence)
    runtime = _clean_strings(runtime_checks)
    outcomes = _clean_strings(outcome_checks)
    scope_files = _clean_strings(allowed_files)
    scope_dirs = _clean_strings(allowed_dirs)
    forbidden = _clean_strings(forbidden_side_effects)
    approvals = _clean_strings(human_approval_conditions)

    success_conditions = {
        "tests": tests,
        "runtime": runtime,
        "outcome": outcomes,
        "forbidden_side_effects_absent": forbidden,
        "result_recorded": True,
        "unsupported_claims_absent": True,
    }
    payload = {
        "spec": spec,
        "scope": {"allowed_files": scope_files, "allowed_dirs": scope_dirs},
        "forbidden_side_effects": forbidden,
        "success_conditions": success_conditions,
        "required_evidence": evidence,
        "budgets": {
            "max_iterations": _bounded_iterations(max_iterations),
            "max_tokens": _bounded_nonnegative(max_tokens, MAX_SAFE_TOKENS),
            "max_tool_calls": _bounded_nonnegative(max_tool_calls, MAX_SAFE_TOOL_CALLS),
        },
        "approval": {"human_approval_conditions": approvals},
    }
    warnings = []
    if not tests and not runtime and not outcomes:
        warnings.append("no_verification_conditions_done_will_be_unknown")
    if not evidence:
        warnings.append("required_evidence_missing_done_will_be_blocked")
    if not scope_files and not scope_dirs:
        warnings.append("mutation_scope_empty")

    return {
        "status": "ok",
        "version": 2,
        "contract_id": _stable_contract_id(payload),
        **payload,
        "done_predicate": {
            "all_success_conditions_must_pass": True,
            "all_required_evidence_must_exist": True,
            "no_unsupported_claims": True,
            "unknown_is_not_pass": True,
        },
        "warnings": warnings,
    }


def evaluate_done_predicate(contract: dict, observed: dict) -> dict:
    """Evaluate task completion from observed evidence/state, never from agent prose.

    observed accepts: passed_tests/runtime_checks/outcome_checks/evidence as iterables,
    forbidden_side_effects as observed violations, result_recorded bool, and
    unsupported_claims as a list. Missing observations are treated as incomplete.
    """
    if contract.get("status") != "ok" or contract.get("version") != 2:
        return {"status": "error", "reason": "task_contract_v2_required"}

    success = contract.get("success_conditions") or {}
    required = set(contract.get("required_evidence") or [])
    observed_evidence = set(observed.get("evidence") or [])

    checks = {
        "tests": set(success.get("tests") or []).issubset(set(observed.get("passed_tests") or [])),
        "runtime": set(success.get("runtime") or []).issubset(set(observed.get("runtime_checks") or [])),
        "outcome": set(success.get("outcome") or []).issubset(set(observed.get("outcome_checks") or [])),
        "required_evidence": required.issubset(observed_evidence),
        "forbidden_side_effects_absent": not bool(observed.get("forbidden_side_effects") or []),
        "result_recorded": observed.get("result_recorded") is True,
        "unsupported_claims_absent": not bool(observed.get("unsupported_claims") or []),
    }

    has_verification_conditions = bool(success.get("tests") or success.get("runtime") or success.get("outcome"))
    missing_evidence = sorted(required - observed_evidence)
    failed_checks = sorted(name for name, ok in checks.items() if not ok)

    if not has_verification_conditions:
        state = "unknown"
        reason = "no_verification_conditions"
    elif failed_checks:
        state = "not_done"
        reason = "done_predicate_failed"
    else:
        state = "done"
        reason = "all_required_conditions_verified"

    return {
        "status": "ok",
        "state": state,
        "reason": reason,
        "checks": checks,
        "missing_evidence": missing_evidence,
        "failed_checks": failed_checks,
        "contract_id": contract.get("contract_id"),
    }


def next_loop_decision(iteration: int, max_iterations: int, spec_satisfied: bool, tests_passed: bool, unsafe_blocked: bool = False) -> dict:
    iteration = max(0, int(iteration))
    max_iterations = _bounded_iterations(max_iterations)

    if unsafe_blocked:
        return {
            "status": "stop",
            "reason": "unsafe_patch_blocked",
            "next_action": "record_blocker_and_request_human_decision",
        }
    if spec_satisfied and tests_passed:
        return {
            "status": "done",
            "reason": "acceptance_criteria_passed",
            "next_action": "record_final_report",
        }
    if iteration >= max_iterations:
        return {
            "status": "exhausted",
            "reason": "max_iterations_exhausted",
            "next_action": "record_gap_report_and_request_scope_or_spec_decision",
        }
    return {
        "status": "continue",
        "reason": "spec_or_tests_not_satisfied_yet",
        "next_iteration": iteration + 1,
        "next_action": "record_result_then_prepare_improvement_context",
    }
