from uacos.orchestrator.contract import (
    MAX_SAFE_ITERATIONS,
    build_orchestration_plan,
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
