# External Agent Integration

This guide describes how UACOS should integrate with external AI coding agents such as Goose, Claude Code, Codex, OpenClaw, Cline, Aider, or a manual chat workflow.

UACOS must remain the repo brain, context optimizer, orchestration planner, and patch safety gate. The external agent remains the worker that proposes changes.

## Integration boundary

```text
External AI coding agent
Goose / Claude Code / Codex / OpenClaw / Cline / Aider / manual chat
        |
        v
UACOS MCP server / uacos-flow
        |
        v
get_context -> agent proposes patch -> ingest_patch(validate only) -> tests/release gate -> loop_decision
```

## Non-negotiable rules

- The agent must treat UACOS patch responses as the authority for whether a patch is safe to trust.
- The agent must not claim done only because it generated code.
- The first integration path should validate patches without applying them.
- Patch application must go through Guard Mode, transaction, or explicit `ingest_patch(apply=true)` with allowed scope and tests.
- UACOS must keep MCP localhost-only by default.
- UACOS must stop bounded loops when tests pass, safety blocks the patch, scope expands, or `max_iterations` is exhausted.

## Required MCP tools for external agents

| Tool | Purpose | Write behavior |
|---|---|---|
| `list_tools` | Discover UACOS tool contract | Read-only |
| `product_contract` | Read product boundary and workflows | Read-only |
| `orchestration_contract` | Read loop rules and safety invariants | Read-only |
| `plan_orchestration_loop` | Plan bounded spec-driven work | Read-only |
| `loop_decision` | Decide whether to continue/stop/block | Read-only |
| `get_context` | Fetch compressed task context | Read-only |
| `ingest_patch` | Validate or explicitly apply a patch | Validate-only by default; apply requires explicit opt-in |
| `status` | Read repo/runtime status | Read-only |

## Mock external-agent flow

The current CI-safe integration test uses UACOS's localhost MCP server as a mock external-agent client:

1. Start a temporary MCP server.
2. Call `list_tools` to verify the required contract exists.
3. Call `get_context` for a concrete task.
4. Call `plan_orchestration_loop` with a bounded spec and test command.
5. Submit a patch through `ingest_patch` with `apply=false`.
6. Verify UACOS returns `validated`, not `applied`.
7. Call `loop_decision` for the next safe step.
8. Confirm unsafe or exhausted loops stop instead of continuing silently.

This proves the contract shape before testing a real Goose client.

## Real Goose integration target

The next real-client milestone should prove this flow with Goose or another MCP-capable agent:

```text
Goose connects to UACOS MCP
Goose calls get_context
Goose proposes unified diff
UACOS ingest_patch validates only
User or guarded automation applies through transaction/test flow
UACOS loop_decision returns continue/stop/block
UACOS writes evidence report
```

## Validation commands

Run the current mock contract test:

```bash
python -m pytest -q tests/test_external_agent_mcp_flow.py
```

Run the built-in MCP self-test through the release gate:

```bash
python scripts/release_gate.py
```

## What this does not prove yet

- It does not prove Goose UI/CLI can consume UACOS MCP directly.
- It does not prove provider-specific agent behavior.
- It does not measure token savings from a real agent conversation.
- It does not prove full automatic patch application is safe.

Those require the next milestone: a real Goose or MCP-client run with archived evidence.
