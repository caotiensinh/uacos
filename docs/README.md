# UACOS Documentation Index

This index is the recommended reading path for UACOS. It keeps the documentation organized by user intent instead of by implementation history.

## Start here

| Document | Purpose |
|---|---|
| [Current Status](CURRENT_STATUS.md) | Current product maturity, completed phases, CI evidence, and remaining evidence gaps. |
| [Onboarding](ONBOARDING.md) | Shortest path for new users: setup, doctor, status, assist, guard, apply-safe. |
| [Workflow Recipes](WORKFLOW_RECIPES.md) | Copy/paste-safe workflows for setup, AI edits, high-risk changes, orchestration, and benchmark claims. |
| [User Guide](USER_GUIDE.md) | Broader usage guide for existing UACOS commands and modes. |
| [Troubleshooting](TROUBLESHOOTING.md) | Common problems and fixes. |

## Product direction and roadmap

| Document | Purpose |
|---|---|
| [Strategic Status](STRATEGIC_STATUS.md) | Product positioning, Goose comparison, maturity estimate, and non-negotiable rules. |
| [Production Improvement Checklist](PRODUCTION_IMPROVEMENT_CHECKLIST.md) | Finite phase checklist with evidence and remaining gaps. |
| [Product Workflows](PRODUCT_WORKFLOWS.md) | Product workflow contract and supported modes. |

## Core workflows

| Document | Purpose |
|---|---|
| [Auto Mode](AUTO_MODE.md) | Local automatic readiness/report workflow. |
| [Autopilot Mode](AUTOPILOT_MODE.md) | Bounded patch iteration with explicit confirmation and rollback. |
| [Patch Lifecycle](PATCH_LIFECYCLE.md) | Review, risk classify, guarded apply, tests, rollback, and evidence report. |
| [Context Intelligence](CONTEXT_INTELLIGENCE.md) | Selected-file explanation, symbol context, route/API graph, test map, and config risk map. |
| [External Agent Integration](EXTERNAL_AGENT_INTEGRATION.md) | MCP/mock client flow and real Goose/MCP evidence target. |

## Product proof package

Use these before publishing claims or customer-facing material.

| Document | Purpose |
|---|---|
| [Claim Wording Guide](CLAIM_WORDING_GUIDE.md) | Safe, benchmarked, and forbidden claims. |
| [Public Benchmark Report Template](PUBLIC_BENCHMARK_REPORT_TEMPLATE.md) | Required evidence format before public token-saving claims. |
| [Case Study Template](CASE_STUDY_TEMPLATE.md) | Conservative case-study structure. |
| [Agent Comparison Matrix](AGENT_COMPARISON_MATRIX.md) | UACOS + AI agent versus AI agent alone, without claiming replacement. |

## Setup and operations

| Document | Purpose |
|---|---|
| [Installation](INSTALLATION.md) | Installation details. |
| [Security Model](SECURITY_MODEL.md) | Local-first security assumptions and patch safety rules. |
| [Language Policy](LANGUAGE_POLICY.md) | English-only repository content policy and automated language gate. |
| [MCP Server](MCP_SERVER.md) | MCP interface details, if present in the checked-out version. |

## Example artifacts

| Path | Purpose |
|---|---|
| `examples/reports/uacos_flow_status_example.json` | Example output from `uacos-flow status`. |
| `evals/benchmark_suite.json` | Repeatable benchmark suite used by release gate. |
| `evals/multi_repo_benchmark.example.json` | Optional multi-repo benchmark profile for real mounted repos. |

## Recommended reading order

For a new developer:

1. [Current Status](CURRENT_STATUS.md)
2. [Onboarding](ONBOARDING.md)
3. [Workflow Recipes](WORKFLOW_RECIPES.md)
4. [Patch Lifecycle](PATCH_LIFECYCLE.md)
5. [Context Intelligence](CONTEXT_INTELLIGENCE.md)

For product or investor review:

1. [Strategic Status](STRATEGIC_STATUS.md)
2. [Production Improvement Checklist](PRODUCTION_IMPROVEMENT_CHECKLIST.md)
3. [Agent Comparison Matrix](AGENT_COMPARISON_MATRIX.md)
4. [Claim Wording Guide](CLAIM_WORDING_GUIDE.md)
5. [Public Benchmark Report Template](PUBLIC_BENCHMARK_REPORT_TEMPLATE.md)

For repository maintainers:

1. [Language Policy](LANGUAGE_POLICY.md)
2. [Security Model](SECURITY_MODEL.md)
3. [Production Improvement Checklist](PRODUCTION_IMPROVEMENT_CHECKLIST.md)

For public claims:

1. Run the benchmark and release gate.
2. Fill [Public Benchmark Report Template](PUBLIC_BENCHMARK_REPORT_TEMPLATE.md).
3. Check [Claim Wording Guide](CLAIM_WORDING_GUIDE.md).
4. Do not claim 80-90% or 99% token savings unless the evidence directly supports it.

## Documentation rules

- Keep the root README short and product-oriented.
- Put detailed docs in `docs/`.
- Use this index as the main navigation page.
- Keep repository documentation and user-facing text in English; see [Language Policy](LANGUAGE_POLICY.md).
- Do not duplicate large explanations across many files; link to the source document instead.
- Never claim production readiness or 99% token savings without benchmark evidence.
