from uacos.product.workflows import get_product_contract, get_session_plan, get_workflow_modes
from uacos.mcp.server import tool_specs


def test_product_contract_positions_uacos_as_repo_brain_not_agent_clone():
    contract = get_product_contract()

    assert contract["status"] == "ok"
    assert contract["positioning"]["category"] == "repo_brain_and_safety_gate"
    assert "a Goose clone" in contract["positioning"]["is_not"]
    assert "Goose" in contract["positioning"]["integrates_with"]


def test_workflow_modes_are_finite_and_simple():
    modes = get_workflow_modes()
    names = [m["name"] for m in modes]

    assert names == ["prepare", "assist", "guard"]
    assert modes[0]["writes_code"] is False
    assert modes[1]["writes_code"] is False
    assert modes[2]["writes_code"] is True
    assert modes[2]["release_gate_required"] is True


def test_upgrade_plan_is_bounded_to_four_sessions():
    plan = get_session_plan()

    assert len(plan) == 4
    assert [row["session"] for row in plan] == [1, 2, 3, 4]
    assert any("MCP" in row["title"] for row in plan)
    assert all(row["scope"] for row in plan)
    assert all(row["out_of_scope"] for row in plan)
    assert all(row["evidence_required"] for row in plan)


def test_mcp_exposes_product_contract_tool():
    names = [tool["name"] for tool in tool_specs()]

    assert "product_contract" in names
    assert names.index("product_contract") < names.index("status")
