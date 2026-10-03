from uacos.orchestrator.contract import (
    MAX_SAFE_ITERATIONS,
    build_orchestration_plan,
    build_task_contract_v2,
    evaluate_done_predicate,
    get_orchestration_contract,
    next_loop_decision,
)


def test_orchestration_contract_keeps_uacos_as_coordination_layer():
    contract = get_orchestration_contract()

    assert contract["status"] == "ok"
    assert contract["role"] == "coordination_layer_not_agent"
    pillar_ids = [p["id"] for p in contract["core_pillars"]]
    assert pillar_ids == [
        "token_prompt_optimization",
        "safe_code_change",
        "agent_code_coordination",
        "spec_driven_devops_loop",
    ]
    assert any("No unbounded loop" in rule for rule in contract["safety_invariants"])
    assert contract["phase3_contract_v2"]["machine_readable_done"] is True


def test_orchestration_plan_is_finite_and_does_not_execute():
    plan = build_orchestration_plan(
        "upgrade login safely until tests pass",
        agents=["goose", "codex"],
        tests=["pytest -q"],
        max_iterations=99,
    )

    assert plan["status"] == "ok"
    assert plan["role"] == "orchestrate_agents_and_code_do_not_act_as_general_agent"
    assert plan["max_iterations"] == MAX_SAFE_ITERATIONS
    assert len(plan["loop"]) == MAX_SAFE_ITERATIONS
    assert plan["warnings"] == []
    assert "tests_passed_or_explicit_validation_evidence" in plan["done_requires"]


def test_orchestration_plan_warns_when_tests_are_missing():
    plan = build_orchestration_plan("improve API handling", tests=[], max_iterations=2)

    assert plan["status"] == "ok"
    assert plan["max_iterations"] == 2
    assert "tests_missing_done_will_be_blocked" in plan["warnings"]


def test_orchestration_plan_rejects_empty_spec():
    plan = build_orchestration_plan("   ")

    assert plan["status"] == "error"
    assert plan["reason"] == "spec_required"


def test_loop_decision_stops_on_done_exhausted_or_unsafe():
    assert next_loop_decision(1, 3, spec_satisfied=True, tests_passed=True)["status"] == "done"
    assert next_loop_decision(3, 3, spec_satisfied=False, tests_passed=False)["status"] == "exhausted"
    assert next_loop_decision(1, 3, spec_satisfied=False, tests_passed=False, unsafe_blocked=True)["status"] == "stop"
    cont = next_loop_decision(1, 3, spec_satisfied=False, tests_passed=False)
    assert cont["status"] == "continue"
    assert cont["next_iteration"] == 2


def test_task_contract_v2_is_stable_bounded_and_declarative():
    kwargs = dict(
        allowed_files=["uacos/api.py"],
        allowed_dirs=["tests"],
        forbidden_side_effects=["auth_changed"],
        required_tests=["pytest -q tests/test_api.py"],
        required_evidence=["patch", "test_run"],
        runtime_checks=["health_200"],
        outcome_checks=["scan_job_created"],
        max_iterations=99,
        max_tokens=9_999_999,
        max_tool_calls=9_999,
        human_approval_conditions=["scope_expansion"],
    )
    first = build_task_contract_v2("fix scan workflow", **kwargs)
    second = build_task_contract_v2("fix scan workflow", **kwargs)

    assert first["status"] == "ok"
    assert first["version"] == 2
    assert first["contract_id"] == second["contract_id"]
    assert first["budgets"]["max_iterations"] == MAX_SAFE_ITERATIONS
    assert first["budgets"]["max_tokens"] == 2_000_000
    assert first["budgets"]["max_tool_calls"] == 500
    assert first["done_predicate"]["unknown_is_not_pass"] is True
    assert first["success_conditions"]["unsupported_claims_absent"] is True


def test_task_contract_v2_done_is_computed_from_evidence_not_agent_claim():
    contract = build_task_contract_v2(
        "fix scan workflow",
        allowed_files=["uacos/api.py"],
        required_tests=["pytest -q tests/test_api.py"],
        required_evidence=["patch", "test_run", "runtime_trace"],
        runtime_checks=["health_200"],
        outcome_checks=["scan_job_created"],
    )

    observed = {
        "passed_tests": ["pytest -q tests/test_api.py"],
        "runtime_checks": ["health_200"],
        "outcome_checks": ["scan_job_created"],
        "evidence": ["patch", "test_run", "runtime_trace"],
        "forbidden_side_effects": [],
        "result_recorded": True,
        "unsupported_claims": [],
        "agent_claim": "I am done",
    }
    result = evaluate_done_predicate(contract, observed)

    assert result["state"] == "done"
    assert result["failed_checks"] == []


def test_task_contract_v2_fails_closed_on_missing_evidence_or_unsupported_claims():
    contract = build_task_contract_v2(
        "fix scan workflow",
        allowed_dirs=["uacos"],
        required_tests=["pytest -q"],
        required_evidence=["patch", "test_run"],
    )
    result = evaluate_done_predicate(
        contract,
        {
            "passed_tests": ["pytest -q"],
            "evidence": ["patch"],
            "result_recorded": True,
            "unsupported_claims": ["production_ready"],
        },
    )

    assert result["state"] == "not_done"
    assert result["missing_evidence"] == ["test_run"]
    assert "required_evidence" in result["failed_checks"]
    assert "unsupported_claims_absent" in result["failed_checks"]


def test_task_contract_v2_returns_unknown_without_verification_conditions():
    contract = build_task_contract_v2(
        "document-only investigation",
        required_evidence=["report"],
    )
    result = evaluate_done_predicate(
        contract,
        {"evidence": ["report"], "result_recorded": True},
    )

    assert result["state"] == "unknown"
    assert result["reason"] == "no_verification_conditions"
