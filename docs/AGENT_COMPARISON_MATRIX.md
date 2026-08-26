# UACOS Comparison Matrix

UACOS should be compared as a repo brain, context optimizer, and safety/evidence layer — not as a replacement for AI coding agents.

| Capability | AI agent alone | UACOS + AI agent |
|---|---|---|
| General reasoning/chat | Strong | Delegated to agent |
| Code generation | Strong | Delegated to agent |
| Full-repo context control | Often manual or broad | Task-bounded context pack |
| Token reduction evidence | Usually informal | Benchmark report and claim policy |
| Selected-file explanation | Agent-dependent | `selection_explanations` |
| Symbol/call/import context | Agent-dependent | `symbol_context` from static graph |
| Route/API visibility | Agent-dependent | `api_graph` static scan |
| Test recommendation | Agent-dependent | `test_map` likely test mapping |
| Config/deploy risk visibility | Agent-dependent | `config_risk` risk map |
| Patch scope validation | Often manual | Guard Mode patch gate |
| Secret exposure scan | Agent/tool-dependent | Patch gate and review checks |
| Safe apply with checkpoint | Manual | Apply-safe transaction flow |
| Rollback on failed tests | Manual | Guarded transaction rollback |
| Done evidence | Often conversation-based | Reports, tests, release gate, lifecycle report |
| Bounded orchestration loop | Agent-dependent | Explicit max-iteration plan |

## Positioning

Correct positioning:

> UACOS makes AI coding agents safer and cheaper to use by preparing bounded context, reviewing patches, and recording evidence.

Incorrect positioning:

> UACOS replaces Goose, Codex, Claude Code, Aider, Cline, or OpenClaw.

## When to use UACOS

Use UACOS when:

- the repository is too large to paste into an AI agent
- token budget matters
- patch scope must be controlled
- tests and evidence matter
- the task touches config, auth, network, deploy, or dependencies
- you need repeatable benchmark or release-gate evidence

## When UACOS is not enough

UACOS does not replace:

- human review of high-risk patches
- real integration tests
- production observability
- security audits
- the AI coding agent itself
