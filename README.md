# UACOS

![CI](https://github.com/caotiensinh/uacos/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/github/license/caotiensinh/uacos)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)

UACOS is a local-first reliability, context, and safety runtime for AI coding agents.

UACOS is **not a Goose clone or general chat/coding agent**. External agents propose changes. UACOS prepares bounded context, validates semantic scope/risk, enforces policy and approval, applies changes through guarded transactions, runs verification, retries bounded failures, and records durable evidence.

## Start here

- [Documentation Index](docs/README.md)
- [Current Status](docs/CURRENT_STATUS.md)
- [Production Improvement Checklist](docs/PRODUCTION_IMPROVEMENT_CHECKLIST.md)
- [Strategic Status](docs/STRATEGIC_STATUS.md)
- [Language Policy](docs/LANGUAGE_POLICY.md)

## Requirements

- Python 3.9+
- Optional: Ollama for local real-model evaluation
- Optional: Codex CLI, Claude Code, or Goose for real-provider E2E; availability is never assumed

## Three-step workflow

### 1. Initialize and inspect

```bash
python -m pip install -e .
uacos-flow setup --repo . --task "fix login bug safely"
uacos-flow doctor --repo .
```

### 2. Build bounded context

```bash
uacos-flow assist --repo . --task "fix login bug safely" --max-tokens 6000
```

### 3. Guard and apply verified changes

```bash
uacos-flow guard \
  --repo . \
  --patch change.diff \
  --task "fix login bug safely" \
  --allowed-file app/auth.py \
  --test "pytest -q"

uacos-flow apply-safe \
  --repo . \
  --patch change.diff \
  --allowed-file app/auth.py \
  --test "pytest -q" \
  --yes
```

Existing `uacos ...` commands remain available for lower-level and backward-compatible workflows.

## Core capabilities

- Multi-language semantic graph: Python, JavaScript/TypeScript, Rust, Go, Java, C, and C++.
- Canonical symbols, cross-file imports, calls, inheritance/interfaces, route/service/data relationships, and test/source relationships.
- Evidence-weighted context selection with symbol/subgraph slicing and dynamic budgets.
- Durable agent runtime with resume, retry policy, no-progress detection, cancellation/deadlines, and replay.
- Semantic diff risk, stale-patch preconditions, YAML policy, patch-bound human approval, guarded apply/test/rollback, and rollback verification.
- Real HTTP JSON-RPC MCP client with timeout/payload bounds, pagination guards, request-id validation, and localhost network E2E.
- Evidence-first real-agent E2E runner for Codex CLI, Claude Code, and Goose when explicitly installed/configured.
- Comparative ground-truth benchmark evaluator for `full_repo` vs `grep` vs `uacos`.

## Useful commands

```bash
uacos-flow list
uacos-flow status --repo .
uacos-flow prepare --repo . --summary
uacos-flow orchestrate --spec "upgrade safely until tests pass" --agent goose --test "pytest -q" --max-iterations 3
uacos-flow benchmark --repo . --manifest evals/benchmark_suite.json
```

## Evidence and claims

The repository separates **implementation tests** from **real-world evidence**.

A fixture, mock, binary probe, or localhost contract test must not be presented as a successful real-provider run. Real Agent E2E is complete only when an installed/configured provider actually executes and its archived evidence reports `status=passed`.

Comparative benchmark claims require real observations using the same provider/model for all comparison modes, at least three repeats per task/mode, and explicit ground truth.

Safe baseline claim:

> UACOS reduces unnecessary repository context sent to AI coding agents by selecting task-relevant files and validates candidate changes through local reliability and safety gates.

Do **not** claim 80-90% or 99% token savings unless an archived benchmark directly supports the exact statement.

## Evidence outputs

Depending on the workflow, UACOS writes evidence including:

- `reports/uacos_performance_report.json`
- `reports/uacos_benchmark_suite_report.json`
- `reports/release_gate_report.json`
- `reports/real-agent-e2e/summary.json`
- `.uacos/real_agent_e2e/`
- `.uacos/run_state/`
- `.uacos/replay/`
- `.uacos/patch_lifecycle/latest_patch_lifecycle_report.json`

## Product proof package

Use these before publishing claims or customer-facing material:

- [Claim Wording Guide](docs/CLAIM_WORDING_GUIDE.md)
- [Public Benchmark Report Template](docs/PUBLIC_BENCHMARK_REPORT_TEMPLATE.md)
- [Case Study Template](docs/CASE_STUDY_TEMPLATE.md)
- [Agent Comparison Matrix](docs/AGENT_COMPARISON_MATRIX.md)

## Community listing

UACOS is listed in [awesome-cli-coding-agents](https://github.com/bradAGI/awesome-cli-coding-agents) under **Agent infrastructure**. This is a community-maintained project listing, not a certification or vendor endorsement.

## Documentation

Use [docs/README.md](docs/README.md) as the main documentation index.
