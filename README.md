# UACOS

![CI](https://github.com/caotiensinh/uacos/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/github/license/caotiensinh/uacos)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)

UACOS is a local-first repo brain, context-compression layer, orchestration planner, and patch safety/evidence gate for AI coding workflows.

UACOS is **not a Goose clone or general chat agent**. The AI coding agent proposes or writes code. UACOS prepares bounded context, validates patch scope/risk, supports guarded apply/rollback, records evidence, and prevents unsupported product claims.

## Start here

- [Documentation Index](docs/README.md) — organized map of all project documentation.
- [Current Status](docs/CURRENT_STATUS.md) — completed phases, CI evidence, maturity, and remaining evidence gaps.
- [Production Improvement Checklist](docs/PRODUCTION_IMPROVEMENT_CHECKLIST.md) — finite roadmap and completion evidence.
- [Strategic Status](docs/STRATEGIC_STATUS.md) — product positioning, Goose comparison, and maturity estimate.

## Requirements

- Python 3.9+
- Optional: Ollama for local real-model evaluation

## Quick Start

```bash
python -m pip install -e .
uacos-flow setup --repo . --task "fix login bug safely"
uacos-flow doctor --repo .
uacos-flow status --repo .
```

Expected output:

```json
{
  "status": "pass",
  "mode": "setup",
  "quick_commands": [
    "uacos-flow doctor --repo .",
    "uacos-flow assist --repo . --task \"fix login bug safely\" --max-tokens 6000"
  ]
}
```

## Main workflow

```bash
uacos-flow assist --repo . --task "fix MCP docs" --max-tokens 6000
uacos-flow guard --repo . --patch change.diff --task "fix MCP docs" --allowed-file docs/PRODUCT_WORKFLOWS.md --test "pytest -q"
uacos-flow apply-safe --repo . --patch change.diff --allowed-file docs/PRODUCT_WORKFLOWS.md --test "pytest -q" --yes
```

## Other useful commands

```bash
uacos-flow list
uacos-flow prepare --repo . --summary
uacos-flow orchestrate --spec "upgrade safely until tests pass" --agent goose --test "pytest -q" --max-iterations 3
uacos-flow benchmark --repo . --manifest evals/benchmark_suite.json
```

Existing `uacos ...` commands remain available and backward compatible.

## Supported product workflows

1. **Setup Mode** — one-command local setup: bootstrap, graph, cache, scripts, and actionable doctor.
2. **Doctor Mode** — user-actionable readiness status with concrete next commands.
3. **Status Mode** — terminal/dashboard-friendly readiness and evidence summary.
4. **Prepare Mode** — repo graph, cache, memory, health reports, and compressed readiness evidence before AI edits.
5. **Assist Mode** — bounded task context, selected-file explanations, symbol context, route/API graph, test suggestions, and config-risk review.
6. **Guard Mode** — patch scope gates, secret scans, risk review, and optional task alignment without applying code.
7. **Apply-safe Mode** — checkpoint, tests, auto-rollback, and last-run evidence.
8. **Orchestrate Mode** — bounded `spec -> context -> delegate -> patch -> test -> record -> improve` planning without becoming the agent.

## Product proof package

Use these before publishing claims or customer-facing material:

- [Claim Wording Guide](docs/CLAIM_WORDING_GUIDE.md)
- [Public Benchmark Report Template](docs/PUBLIC_BENCHMARK_REPORT_TEMPLATE.md)
- [Case Study Template](docs/CASE_STUDY_TEMPLATE.md)
- [Agent Comparison Matrix](docs/AGENT_COMPARISON_MATRIX.md)

## Evidence and claims

Run the repeatable benchmark suite before making public savings claims:

```bash
python scripts/uacos_benchmark_suite.py --repo . --manifest evals/benchmark_suite.json --summary
```

Safe baseline claim:

> UACOS reduces unnecessary repository context sent to AI coding agents by selecting task-relevant files, compressing context, and validating changes through local safety gates.

Do **not** claim 80-90% or 99% token savings unless a benchmark report directly supports that exact claim.

## What you get

- `reports/uacos_performance_report.json` for token/context estimates
- `reports/uacos_benchmark_suite_report.json` for repeatable benchmark evidence
- `reports/uacos_auto_report.json` for Auto Mode summary
- `reports/release_gate_report.json` for release readiness checks
- `.uacos/patch_lifecycle/latest_patch_lifecycle_report.json` for the latest safe-apply evidence
- `.uacos/scripts/` convenience dashboard launchers from `uacos-flow setup`
- `examples/reports/uacos_flow_status_example.json` for example status output
- `uacos-flow` simplified product workflow command

## Documentation

Use [docs/README.md](docs/README.md) as the main documentation index.
