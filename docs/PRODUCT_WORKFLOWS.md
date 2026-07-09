# UACOS Product Workflow Contract

UACOS is not a Goose clone and should not drift into a general-purpose chat agent. Its product role is narrower and more valuable:

> UACOS is the local-first repo brain, prompt/context optimizer, agent-code coordinator, and patch safety gate for AI coding workflows.

UACOS should integrate with agents such as Goose, Claude Code, Codex, OpenClaw, Aider, Cline, and manual chat workflows. It should make those agents cheaper and safer by preparing the right project context, coordinating bounded code workflows, and guarding patch application.

## Product boundary

### In scope

- Token and prompt optimization.
- Repo scanning and project memory.
- Dependency and impact analysis before an AI edit.
- Task-specific compressed context generation.
- Coordination between external agents and codebase operations.
- Patch scope validation.
- Secret scanning on added lines.
- Transaction checkpoint, test execution, and rollback.
- Evidence recording after each iteration.
- Local-only MCP access for external agents.
- Repeatable token and release-gate reports.

### Out of scope

- Becoming a full desktop AI agent platform.
- Competing directly with Goose as a general-purpose agent runtime.
- Cloud-first execution as the default path.
- Unattended patch application without explicit opt-in, scope, tests, and rollback.
- Unbounded autonomous loops.
- Claiming 80-90% savings without benchmark evidence.

## Simple command surface

Use `uacos-flow` for the main product workflows:

```bash
uacos-flow list
uacos-flow prepare --repo . --summary
uacos-flow assist --repo . --task "fix MCP docs" --max-tokens 6000
uacos-flow guard --repo . --patch change.diff --task "fix MCP docs" --allowed-file docs/PRODUCT_WORKFLOWS.md
uacos-flow orchestrate --spec "upgrade safely until tests pass" --agent goose --test "pytest -q" --max-iterations 3
uacos-flow benchmark --repo . --manifest evals/benchmark_suite.json
```

`uacos-flow` is a compatibility-safe wrapper. It does not remove or change the existing lower-level `uacos ...` commands.

## Four core pillars

1. **Token and prompt optimization** — select relevant files, compress context, reuse memory/skills, and keep prompts bounded.
2. **Safe code change and upgrade** — validate scope, scan secrets, checkpoint files, run tests, and roll back failed changes.
3. **Agent-code coordination layer** — coordinate external agents and codebase operations without becoming a general-purpose agent itself.
4. **Spec-driven DevOps loop** — repeat `plan -> code -> test -> record -> improve` only within explicit bounds until the user spec passes or the loop is exhausted.

## Four supported workflows

### 1. Prepare Mode

Use this before any AI-assisted change:

```bash
uacos bootstrap --repo .
uacos health --repo .
uacos graph-build --repo .
uacos compress-cache --repo .
uacos auto --repo . --summary
```

Or use the simplified wrapper:

```bash
uacos-flow prepare --repo . --summary
```

Purpose: build local repo state, graph, cache, memory, health report, and compressed readiness evidence.

Prepare Mode must not edit project code.

### 2. Assist Mode

Use this when an external AI agent needs context:

```bash
uacos impact --repo . --task "<task>"
uacos context-compressed --repo . --task "<task>" --max-tokens 6000
uacos mcp-serve --repo . --host 127.0.0.1 --port 8769
```

Or use the simplified wrapper:

```bash
uacos-flow assist --repo . --task "<task>" --max-tokens 6000
```

Purpose: give the agent bounded context instead of letting it read the whole repository.

Assist Mode must not edit project code.

### 3. Guard Mode

Use this when a patch is ready to validate or apply:

```bash
uacos patch-check --repo . --patch change.diff --allowed-file path/to/file.py
uacos impact-alignment-check --repo . --task "<task>" --patch change.diff
uacos autopilot-run --repo . --task-file .uacos/tasks/TASK-xxxx.json --apply --yes
python scripts/release_gate.py
```

Or use the simplified validation wrapper:

```bash
uacos-flow guard --repo . --patch change.diff --task "<task>" --allowed-file path/to/file.py
```

Purpose: validate scope, check task alignment, scan for secrets, checkpoint affected files, run tests, and roll back on failure.

Guard Mode can edit code only through explicit opt-in and must keep release-gate evidence. The simplified `uacos-flow guard` wrapper validates only; it does not apply patches.

### 4. Orchestrate Mode

Use this when an external agent or user wants a bounded DevOps-style loop:

```text
MCP tool: orchestration_contract
MCP tool: plan_orchestration_loop
MCP tool: loop_decision
```

Or use the simplified wrapper:

```bash
uacos-flow orchestrate --spec "<desired spec>" --agent goose --test "pytest -q" --max-iterations 3
```

Purpose: coordinate the loop `spec -> context -> delegate -> validate patch -> apply/test -> record -> stop or improve`.

Orchestrate Mode does not execute agents, apply patches, or claim success by itself. It only plans and decides the safe next step. Code changes still flow through Guard Mode.

## Benchmark evidence workflow

Run the repeatable benchmark suite before making public claims about savings:

```bash
python scripts/uacos_benchmark_suite.py --repo . --manifest evals/benchmark_suite.json --summary
uacos-flow benchmark --repo . --manifest evals/benchmark_suite.json
```

The suite records:

- baseline token estimate without UACOS
- compressed UACOS context token estimate
- estimated saved tokens and savings percent
- context quality pass rate
- task success signal
- method notes and claim policy

The benchmark suite is also part of `scripts/release_gate.py`, so a broken manifest, runner, or report schema will fail the release gate.

Important: token savings are estimates for trend tracking, not provider billing records. UACOS must not claim 80-90% savings unless repeatable benchmarks on real repositories support that claim.

## Bounded loop rule

UACOS may coordinate repeated improvement, but it must never loop forever.

Every orchestration loop must have:

- `spec`
- `max_iterations`
- tests or explicit validation evidence
- per-iteration record
- stop condition

The allowed stop conditions are:

- `acceptance_criteria_passed`
- `release_gate_passed_when_required`
- `max_iterations_exhausted`
- `scope_expansion_required`
- `unsafe_patch_blocked`
- `human_decision_required`

If the loop exhausts `max_iterations`, UACOS must stop and return a gap report instead of silently continuing.

## Finite upgrade plan

The current priority upgrade is limited to four sessions:

1. **Positioning and workflow contract** — publish product boundary, workflows, MCP product contract, and finite plan.
2. **MCP orchestration contract hardening** — publish core pillars, bounded loop contract, and MCP request/response tests.
3. **Benchmark suite for real repos** — measure file selection, raw tokens, compressed tokens, savings, and task success signals.
4. **Product command simplification** — group user-facing usage around prepare/assist/guard/orchestrate while preserving existing commands.

No open-ended development loop is allowed. A session is not complete until its scope, impact, tests, and remaining work are reported.

## MCP product and orchestration contracts

The MCP server exposes:

```text
product_contract
orchestration_contract
plan_orchestration_loop
loop_decision
```

Example JSON-RPC call:

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": {
    "name": "plan_orchestration_loop",
    "arguments": {
      "spec": "upgrade login safely until tests pass",
      "agents": ["goose", "codex"],
      "tests": ["pytest -q"],
      "max_iterations": 3
    }
  }
}
```

## Safety rule

If a change touches compression, patching, transaction, provider, or runtime code, it must declare why the existing behavior cannot remain untouched. Default behavior is to add a narrow layer around stable code, not rewrite stable code.
