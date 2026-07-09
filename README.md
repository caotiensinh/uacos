# UACOS

![CI](https://github.com/caotiensinh/uacos/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/github/license/caotiensinh/uacos)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)

UACOS is a local-first code intelligence, context-compression, orchestration, and release-gate toolkit that makes AI-assisted changes to a repository safer and cheaper — typed project memory, dependency-graph impact analysis that scopes changes before they're made, prompt/context optimization, patch-scope safety gates, secret scanning, transaction rollback, an LLM cache/budget layer, and a built-in MCP server, all running locally with no cloud dependency.

UACOS is **not a Goose clone or general chat agent**. Its product role is to act as the repo brain, agent-code coordination layer, and safety gate underneath AI coding agents such as Goose, Claude Code, Codex, OpenClaw, Aider, Cline, or manual chat workflows.

See [Strategic Status](docs/STRATEGIC_STATUS.md) for the current goal alignment, Goose comparison, maturity estimate, and remaining production gaps. See [Production Improvement Checklist](docs/PRODUCTION_IMPROVEMENT_CHECKLIST.md) for the finite upgrade plan.

## Requirements

- Python 3.9+
- Optional: Ollama for local real-model evaluation

## Quick Start

```bash
python -m pip install -e .
python -m uacos.cli init --repo .
python -m uacos.cli auto --repo . --summary
```

Expected output:

```bash
$ python -m uacos.cli init --repo .
UACOS initialized in .
$ python -m uacos.cli auto --repo . --summary
{
  "status": "pass",
  "mode": "auto_once",
  "selected_file_count": 4,
  "compressed_tokens_est": 1650,
  "tokens_saved_est": 4702,
  "savings_percent": 74.02
}
```

## Simplified Workflow CLI

Use `uacos-flow` when you do not want to remember the lower-level command surface:

```bash
uacos-flow list
uacos-flow prepare --repo . --summary
uacos-flow assist --repo . --task "fix MCP docs" --max-tokens 6000
uacos-flow guard --repo . --patch change.diff --task "fix MCP docs" --allowed-file docs/PRODUCT_WORKFLOWS.md
uacos-flow orchestrate --spec "upgrade safely until tests pass" --agent goose --test "pytest -q" --max-iterations 3
uacos-flow benchmark --repo . --manifest evals/benchmark_suite.json
```

`uacos-flow` is only a wrapper. Existing `uacos ...` commands remain available and backward compatible.

## Product Workflows

UACOS has four supported product workflows:

1. **Prepare Mode** — build repo graph, cache, memory, health reports, and compressed readiness evidence before AI edits.
2. **Assist Mode** — give external AI agents bounded task context instead of letting them read the whole repository.
3. **Guard Mode** — validate/apply patches through scope gates, secret scans, tests, checkpoints, and rollback.
4. **Orchestrate Mode** — coordinate bounded `spec -> context -> delegate -> patch -> test -> record -> improve` loops without becoming the agent or applying patches outside Guard Mode.

See [Product Workflows](docs/PRODUCT_WORKFLOWS.md) for the finite upgrade plan and MCP product/orchestration contracts.

## Benchmark Evidence

Run the repeatable benchmark suite before making public savings claims:

```bash
python scripts/uacos_benchmark_suite.py --repo . --manifest evals/benchmark_suite.json --summary
```

The suite records token estimates, savings percent, context quality signals, and a claim policy. Token savings are estimates for trend tracking, not provider billing records.

## What you get

- `reports/uacos_performance_report.json` with token savings: 4,702 saved tokens (74.02%)
- `reports/uacos_benchmark_suite_report.json` with repeatable suite-level benchmark evidence
- `reports/uacos_auto_report.json` for Auto Mode summary
- `reports/release_gate_report.json` for release readiness checks
- `uacos/` package and CLI entrypoint installed via `uacos`
- `uacos-flow` simplified product workflow command
- `docs/` and `CHANGELOG.md` for published project onboarding

## Links

- [Production Improvement Checklist](docs/PRODUCTION_IMPROVEMENT_CHECKLIST.md)
- [Strategic Status](docs/STRATEGIC_STATUS.md)
- [Product Workflows](docs/PRODUCT_WORKFLOWS.md)
- [User Guide](docs/USER_GUIDE.md)
- [Auto Mode](docs/AUTO_MODE.md)
- [Autopilot Mode](docs/AUTOPILOT_MODE.md)
- [Installation](docs/INSTALLATION.md)
- [Security Model](docs/SECURITY_MODEL.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
