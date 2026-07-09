# UACOS

![CI](https://github.com/caotiensinh/uacos/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/github/license/caotiensinh/uacos)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)

UACOS is a local-first code intelligence, context-compression, and release-gate toolkit that makes AI-assisted changes to a repository safer and cheaper — typed project memory, dependency-graph impact analysis that scopes changes before they're made, patch-scope safety gates, secret scanning, transaction rollback, an LLM cache/budget layer, and a built-in MCP server, all running locally with no cloud dependency.

UACOS is **not a Goose clone or general chat agent**. Its product role is to act as the repo brain and safety gate underneath AI coding agents such as Goose, Claude Code, Codex, OpenClaw, Aider, Cline, or manual chat workflows.

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

## Product Workflows

UACOS has three supported product workflows:

1. **Prepare Mode** — build repo graph, cache, memory, health reports, and compressed readiness evidence before AI edits.
2. **Assist Mode** — give external AI agents bounded task context instead of letting them read the whole repository.
3. **Guard Mode** — validate/apply patches through scope gates, secret scans, tests, checkpoints, and rollback.

See [Product Workflows](docs/PRODUCT_WORKFLOWS.md) for the finite upgrade plan and MCP product contract.

## What you get

- `reports/uacos_performance_report.json` with token savings: 4,702 saved tokens (74.02%)
- `reports/uacos_auto_report.json` for Auto Mode summary
- `reports/release_gate_report.json` for release readiness checks
- `uacos/` package and CLI entrypoint installed via `uacos`
- `docs/` and `CHANGELOG.md` for published project onboarding

## Links

- [Product Workflows](docs/PRODUCT_WORKFLOWS.md)
- [User Guide](docs/USER_GUIDE.md)
- [Auto Mode](docs/AUTO_MODE.md)
- [Autopilot Mode](docs/AUTOPILOT_MODE.md)
- [Installation](docs/INSTALLATION.md)
- [Security Model](docs/SECURITY_MODEL.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
