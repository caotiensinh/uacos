# UACOS Product Workflow Contract

UACOS is not a Goose clone and should not drift into a general-purpose chat agent. Its product role is narrower and more valuable:

> UACOS is the local-first repo brain, context compressor, and patch safety gate for AI coding agents.

UACOS should integrate with agents such as Goose, Claude Code, Codex, OpenClaw, Aider, Cline, and manual chat workflows. It should make those agents cheaper and safer by preparing the right project context and guarding patch application.

## Product boundary

### In scope

- Repo scanning and project memory.
- Dependency and impact analysis before an AI edit.
- Task-specific compressed context generation.
- Patch scope validation.
- Secret scanning on added lines.
- Transaction checkpoint, test execution, and rollback.
- Local-only MCP access for external agents.
- Repeatable token and release-gate reports.

### Out of scope

- Becoming a full desktop AI agent platform.
- Competing directly with Goose as a general-purpose agent runtime.
- Cloud-first execution as the default path.
- Unattended patch application without explicit opt-in, scope, tests, and rollback.
- Claiming 80-90% savings without benchmark evidence.

## Three supported workflows

### 1. Prepare Mode

Use this before any AI-assisted change:

```bash
uacos bootstrap --repo .
uacos health --repo .
uacos graph-build --repo .
uacos compress-cache --repo .
uacos auto --repo . --summary
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

Purpose: validate scope, check task alignment, scan for secrets, checkpoint affected files, run tests, and roll back on failure.

Guard Mode can edit code only through explicit opt-in and must keep release-gate evidence.

## Finite upgrade plan

The current priority upgrade is limited to four sessions:

1. **Positioning and workflow contract** — publish product boundary, three workflows, MCP product contract, and finite plan.
2. **MCP compatibility hardening** — validate HTTP/JSON-RPC tool behavior and keep MCP localhost-only by default.
3. **Benchmark suite for real repos** — measure file selection, raw tokens, compressed tokens, savings, and task success signals.
4. **Product command simplification** — group user-facing usage around prepare/assist/guard while preserving existing commands.

No open-ended development loop is allowed. A session is not complete until its scope, impact, tests, and remaining work are reported.

## MCP product contract

The MCP server exposes:

```text
product_contract
```

This lets external agents inspect UACOS positioning, workflows, MCP tool contract, and the finite four-session plan before deciding how to use UACOS.

Example JSON-RPC call:

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": {
    "name": "product_contract",
    "arguments": {"section": "workflow_modes"}
  }
}
```

## Safety rule

If a change touches compression, patching, transaction, provider, or runtime code, it must declare why the existing behavior cannot remain untouched. Default behavior is to add a narrow layer around stable code, not rewrite stable code.
