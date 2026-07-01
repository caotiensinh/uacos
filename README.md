# UACOS

![CI](https://github.com/caotiensinh/uacos/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/github/license/caotiensinh/uacos)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)

UACOS is a local-first code intelligence, context-compression, and release-gate toolkit that makes AI-assisted changes to a repository safer and cheaper — typed project memory, patch-scope safety gates, secret scanning, transaction rollback, an LLM cache/budget layer, and a built-in MCP server, all running locally with no cloud dependency.

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

## What you get

- `reports/uacos_performance_report.json` with token savings: 4,702 saved tokens (74.02%)
- `reports/uacos_auto_report.json` for Auto Mode summary
- `reports/release_gate_report.json` for release readiness checks
- `uacos/` package and CLI entrypoint installed via `uacos`
- `docs/` and `CHANGELOG.md` for published project onboarding

## Links

- [User Guide](docs/USER_GUIDE.md)
- [Auto Mode](docs/AUTO_MODE.md)
- [Autopilot Mode](docs/AUTOPILOT_MODE.md)
- [Installation](docs/INSTALLATION.md)
- [Security Model](docs/SECURITY_MODEL.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
