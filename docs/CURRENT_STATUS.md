# UACOS Current Status

Last updated: 2026-07-09

## Product definition

UACOS is a local-first repo brain, context-compression layer, orchestration planner, and patch safety/evidence gate for AI coding workflows.

UACOS is not a Goose clone and is not a general-purpose AI agent. The AI agent writes or proposes code. UACOS prepares bounded context, validates patch scope/risk, runs guarded apply flows, records evidence, and prevents unsupported product claims.

## Current maturity

| Area | Status |
|---|---|
| Product positioning | Strong |
| Context compression and context review | Strong foundation |
| Patch safety lifecycle | Strong foundation |
| External-agent coordination | Mock MCP flow complete; real Goose/MCP client evidence pending |
| Benchmark evidence | Self/CI benchmark foundation complete; real multi-repo mounted benchmark pending |
| Onboarding/usability | One-command setup, doctor, status, recipes, and example report complete |
| Product proof package | Claim guide, benchmark template, case study template, and comparison matrix complete |

## Completed implementation phases

| Phase | Scope | Status | Evidence |
|---|---|---|---|
| Phase 1 | Evidence-grade token benchmark | Complete | CI `29003442656` passed Python 3.9/3.11/3.13 |
| Phase 2 | Multi-repo benchmark foundation | Foundation complete | CI-covered manifest/profile support; real mounted repo runs pending |
| Phase 3 | External-agent MCP/mock flow | Mock complete | CI-covered local MCP contract test; real client pending |
| Phase 4 | Patch lifecycle hardening | Complete | CI `29007172964` passed Python 3.9/3.11/3.13 |
| Phase 5 | Context intelligence | Complete | CI `29023056924` passed Python 3.9/3.11/3.13 |
| Phase 6 | Usability/onboarding | Complete | CI `29024138897` passed Python 3.9/3.11/3.13 |
| Phase 7 | Product proof package | Complete | CI `29024685290` passed Python 3.9/3.11/3.13 |

## Main user workflows

### Setup and readiness

```bash
uacos-flow setup --repo . --task "fix login bug safely"
uacos-flow doctor --repo .
uacos-flow status --repo .
```

### Context for AI agent

```bash
uacos-flow assist --repo . --task "fix login bug safely" --max-tokens 6000
```

Assist returns:

- selected context
- selected-file explanations
- symbol context
- route/API graph
- test-to-source map
- config/deployment risk map

### Patch review and safe apply

```bash
uacos-flow guard --repo . --patch change.diff --allowed-file app/auth.py --test "pytest -q"
uacos-flow apply-safe --repo . --patch change.diff --allowed-file app/auth.py --test "pytest -q" --yes
```

### Bounded orchestration plan

```bash
uacos-flow orchestrate --spec "fix failing auth test" --agent goose --test "pytest -q" --max-iterations 3
```

## What is safe to claim now

Allowed:

> UACOS reduces unnecessary repository context sent to AI coding agents by selecting task-relevant files, compressing context, and validating changes through local safety gates.

Allowed with benchmark report only:

> UACOS achieved X% input-context reduction on Y benchmark tasks across Z repositories, while preserving test pass rate of N%.

Forbidden without direct evidence:

- UACOS saves 99% token.
- UACOS always saves 80-90% token.
- UACOS makes AI coding safe automatically.
- UACOS replaces Goose, Codex, Claude Code, Cline, Aider, or OpenClaw.

## Remaining evidence gaps

These are not blockers for internal use, but they matter before public/commercial claims:

1. Run multi-repo benchmarks against the real mounted project repositories.
2. Verify the same MCP flow with a real Goose or MCP-capable client, not only the mock client.
3. Collect real failed-task examples and retry counts from actual agent runs.
4. Archive generated reports for any public benchmark or case study.

## Recommended next work

1. Run `evals/multi_repo_benchmark.example.json` with real repos mounted.
2. Fill `docs/PUBLIC_BENCHMARK_REPORT_TEMPLATE.md` with actual evidence.
3. Run real Goose/MCP integration and archive the report.
4. Merge PR only after final CI and human review.
