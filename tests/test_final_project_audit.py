from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def parse_project_scripts(pyproject_text: str) -> dict[str, str]:
    scripts: dict[str, str] = {}
    in_scripts = False
    for raw_line in pyproject_text.splitlines():
        line = raw_line.strip()
        if line == "[project.scripts]":
            in_scripts = True
            continue
        if in_scripts and line.startswith("["):
            break
        if in_scripts and "=" in line:
            key, value = line.split("=", 1)
            scripts[key.strip()] = value.strip().strip('"')
    return scripts


def test_final_project_docs_surface_is_complete():
    required_paths = [
        "README.md",
        "docs/README.md",
        "docs/CURRENT_STATUS.md",
        "docs/LANGUAGE_POLICY.md",
        "docs/MCP_SERVER.md",
        "docs/PRODUCT_WORKFLOWS.md",
        "docs/PRODUCTION_IMPROVEMENT_CHECKLIST.md",
        "docs/CONTEXT_INTELLIGENCE.md",
        "docs/PATCH_LIFECYCLE.md",
        "docs/EXTERNAL_AGENT_INTEGRATION.md",
        "docs/CLAIM_WORDING_GUIDE.md",
        "docs/PUBLIC_BENCHMARK_REPORT_TEMPLATE.md",
        "docs/CASE_STUDY_TEMPLATE.md",
        "docs/AGENT_COMPARISON_MATRIX.md",
        "docs/ONBOARDING.md",
        "docs/WORKFLOW_RECIPES.md",
    ]

    missing = [path for path in required_paths if not (ROOT / path).exists()]

    assert missing == []


def test_final_project_cli_entrypoints_are_registered():
    scripts = parse_project_scripts(read("pyproject.toml"))

    assert scripts["uacos"] == "uacos.cli:main"
    assert scripts["uacos-flow"] == "uacos.flow_cli:main"


def test_final_project_release_gate_contains_required_checks():
    release_gate = read("scripts/release_gate.py")

    required_checks = [
        "compileall",
        "pytest",
        "english_language_check",
        "uacos_self_check",
        "community_readiness_check",
        "uacos_auto_check",
        "uacos_flow_list",
        "uacos_performance_benchmark",
        "uacos_benchmark_suite",
        "eval_dry_run",
    ]

    missing = [check for check in required_checks if check not in release_gate]

    assert missing == []


def test_final_project_language_policy_is_connected_to_readme_and_docs_index():
    root_readme = read("README.md")
    docs_index = read("docs/README.md")
    language_policy = read("docs/LANGUAGE_POLICY.md")

    assert "docs/LANGUAGE_POLICY.md" in root_readme
    assert "LANGUAGE_POLICY.md" in docs_index
    assert "scripts/check_english_docs.py" in language_policy
    assert "english_language_check" in language_policy


def test_final_project_product_claims_are_conservative():
    root_readme = read("README.md")
    current_status = read("docs/CURRENT_STATUS.md")
    claim_guide = read("docs/CLAIM_WORDING_GUIDE.md")

    assert "Do **not** claim 80-90% or 99% token savings unless" in root_readme
    assert "Forbidden without direct evidence" in current_status
    assert "## Forbidden claims" in claim_guide
    assert "UACOS guarantees correct patches." in claim_guide

    unsupported_root_claims = [
        "UACOS saves 99% token.",
        "UACOS always saves 80-90% token.",
        "UACOS guarantees correct patches.",
    ]

    for claim in unsupported_root_claims:
        assert claim not in root_readme
