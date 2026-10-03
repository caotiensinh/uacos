# UACOS Current Status

Last updated: 2026-10-04

## Product definition

UACOS is a local-first reliability, context, and safety runtime for AI coding agents.

UACOS is **not** a Goose clone and is not a general-purpose coding/chat agent. External agents such as Codex, Claude Code, Goose, or other MCP/CLI clients produce candidate changes. UACOS selects bounded context, validates semantic scope and risk, enforces policy/approval, applies changes through guarded transactions, runs verification, retries bounded failures, records durable evidence, and supports replay.

## Current maturity

| Area | Status |
|---|---|
| Intelligence Engine V2 | Implemented and CI-covered |
| Context selection/evaluation | Implemented and CI-covered |
| Reliable runtime | Durable state, resume, retry policy, no-progress detection, replay |
| Semantic safety | Stale-patch guards, semantic diff risk, YAML policy, patch-bound approval, verified rollback |
| MCP integration | Real HTTP JSON-RPC MCP client merged; localhost network E2E covered |
| Real coding-agent E2E | Execution/evidence runner merged; real-provider execution still blocked on current self-hosted runner |
| Comparative benchmark | Ground-truth evaluator implemented; real same-provider/model observations still required |
| Product/CI/docs cleanup | Final convergence PR validates benchmark + WS6 together on exact `main` base |

## Implemented core

### Intelligence Engine V2

- Python native AST plus Tree-sitter backends for JavaScript/TypeScript, Rust, Go, Java, C, and C++.
- Canonical symbol identity and cross-file import resolution.
- Caller/callee and inheritance/interface relationships.
- Route -> handler -> service -> DB relationships.
- Test -> production dependencies.
- Changed-lines -> symbols mapping.
- Incremental graph rebuild and generated/vendor policy.
- Symbol/relation recall evaluation support.

### Context selection and evaluation

- Evidence-weighted semantic ranking.
- Symbol/subgraph slicing and dynamic budgets.
- Provenance and uncertainty evidence.
- Context quality metrics and actual-delivery evaluation.

### Reliable runtime

- Durable `run_id` state machine.
- Idempotency, deadline, cancellation, and bounded iterations.
- Resume after interruption without resetting completed iterations.
- Failure-aware retry policy and bounded backoff evidence.
- No-progress detection.
- Durable replay bundles with integrity checks.

### Semantic safety and transactions

- Patch scope validation and semantic diff risk.
- Precondition hashes to block stale patches.
- YAML policy with `allow`, `deny`, and `approval_required` decisions.
- Human approval bound to patch hash and policy hash with expiry checks.
- Guarded apply, tests, rollback, and rollback verification.

### MCP

- Real HTTP JSON-RPC client with bounded timeouts and response sizes.
- JSON-RPC version/request-id/error validation.
- Paginated `tools/list` with cycle/page guards.
- Concurrent request-id isolation.
- Localhost network E2E against the UACOS MCP server.

## Real Agent E2E evidence boundary

UACOS now contains a self-hosted Real Agent E2E runner that:

- probes Codex CLI, Claude Code, and Goose;
- executes only explicitly configured provider argv;
- routes provider output through the normalized safe-execution path;
- archives evidence under `.uacos/real_agent_e2e` and GitHub Actions artifacts;
- never counts an unavailable provider or fixture executable as a real-provider PASS.

The first self-hosted evidence run on `aiserver-uacos` completed successfully as infrastructure validation, but the evidence reported:

- Codex binary: unavailable
- Claude Code binary: unavailable
- Goose binary: unavailable
- configured provider argv: 0
- executed real providers: 0
- status: `incomplete`

Therefore **Real Agent E2E is not complete yet**. Completion requires at least one real provider to be installed/configured, executed, and archived with `status=passed`; broader provider claims require evidence for each named provider.

Provider-readiness diagnostics now distinguish missing binary, missing/invalid argv, and missing detected authentication prerequisites where applicable without writing secret values to reports.

## Comparative benchmark boundary

The comparative evaluator compares three modes:

1. `full_repo`
2. `grep`
3. `uacos`

A valid benchmark requires:

- the same provider/model across all modes for each task;
- at least 3 unique repeats per task/mode;
- hidden/declared ground truth for required symbols and relations;
- pass rate, first-pass rate, retries, tool calls, input/total tokens, latency, and index overhead;
- required-symbol recall and required-relation recall;
- noise measurement.

Initial UACOS target gates are:

- required-symbol recall >= 95%;
- noise <= 20%;
- pass rate not below full-repo baseline;
- input tokens below full-repo baseline.

Fixture tests validate evaluator logic only. They are not benchmark evidence.

## Main user workflow

Use a simple three-stage mental model:

### 1. Initialize and inspect

```bash
uacos-flow setup --repo . --task "fix login bug safely"
uacos-flow doctor --repo .
```

### 2. Build bounded context

```bash
uacos-flow assist --repo . --task "fix login bug safely" --max-tokens 6000
```

### 3. Guard and apply verified changes

```bash
uacos-flow guard --repo . --patch change.diff --task "fix login bug safely" --allowed-file app/auth.py --test "pytest -q"
uacos-flow apply-safe --repo . --patch change.diff --allowed-file app/auth.py --test "pytest -q" --yes
```

Existing `uacos ...` commands remain available for lower-level workflows.

## CI and final closure

Pull-request CI keeps the full Python 3.9/3.11/3.13 matrix on self-hosted Linux. After that exact head passes, post-merge `main` CI uses Python 3.11 only so the Release workflow can validate the merged commit without immediately duplicating the entire matrix and starving the runner queue.

Use:

```bash
python scripts/provider_readiness.py
python scripts/final_closure_check.py --repo .
python scripts/final_closure_check.py --repo . --strict-evidence
```

The strict command remains expected to fail until real-provider and real comparative evidence both pass.

## What is safe to claim now

Allowed:

> UACOS reduces unnecessary repository context sent to AI coding agents by selecting task-relevant files and validates candidate changes through local reliability and safety gates.

Allowed only with an archived benchmark report:

> UACOS achieved X% input-context reduction on Y measured tasks across Z repositories, with required-symbol recall of R% and task pass rate of N%.

Forbidden without direct evidence:

- UACOS saves 99% of tokens.
- UACOS always saves 80-90% of tokens.
- UACOS makes AI coding automatically safe.
- UACOS replaces Codex, Claude Code, Goose, or other coding agents.
- UACOS has completed real-provider E2E when only fixture/mock runs exist.

## Remaining completion gates

1. Pass fresh exact-head PR CI for the converged benchmark + WS6 branch.
2. Install/configure at least one real coding-agent provider on an eligible self-hosted runner and archive a passing real-provider E2E run.
3. Collect real comparative benchmark observations with the same provider/model across `full_repo`, `grep`, and `uacos`, at least 3 repeats per mode.
4. Run strict final closure and require PASS before marking the checklist closed.
