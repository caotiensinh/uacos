from uacos.flow_cli import build_parser, run_orchestrate, workflow_reference


def test_workflow_reference_lists_product_modes():
    ref = workflow_reference()
    names = [mode["name"] for mode in ref["modes"]]

    assert ref["status"] == "ok"
    assert ref["command"] == "uacos-flow"
    assert names == ["prepare", "assist", "guard", "apply-safe", "orchestrate", "benchmark"]
    assert "Existing uacos commands are preserved" in ref["backward_compatibility"]


def test_flow_parser_accepts_list_mode():
    parser = build_parser()
    args = parser.parse_args(["list"])

    assert args.mode == "list"
    assert args.handler(args)["status"] == "ok"


def test_flow_parser_accepts_assist_mode():
    parser = build_parser()
    args = parser.parse_args(["assist", "--task", "fix mcp docs", "--max-tokens", "3000", "--max-files", "4"])

    assert args.mode == "assist"
    assert args.task == "fix mcp docs"
    assert args.max_tokens == 3000
    assert args.max_files == 4


def test_flow_parser_accepts_apply_safe_mode():
    parser = build_parser()
    args = parser.parse_args([
        "apply-safe",
        "--patch",
        "change.diff",
        "--allowed-file",
        "app.py",
        "--test",
        "pytest -q",
        "--yes",
    ])

    assert args.mode == "apply-safe"
    assert args.patch == "change.diff"
    assert args.allowed_file == ["app.py"]
    assert args.test == ["pytest -q"]
    assert args.yes is True


def test_orchestrate_mode_creates_finite_plan():
    result = run_orchestrate(
        "upgrade safely until tests pass",
        agents=["goose", "codex"],
        tests=["pytest -q"],
        max_iterations=99,
    )

    assert result["status"] == "ok"
    assert result["max_iterations"] == 10
    assert result["role"] == "orchestrate_agents_and_code_do_not_act_as_general_agent"
    assert "tests_passed_or_explicit_validation_evidence" in result["done_requires"]
