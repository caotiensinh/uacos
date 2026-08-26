# UACOS Strategic Status

This document records the current strategic position of UACOS after the priority upgrade sessions that focused on product clarity, bounded orchestration, benchmark evidence, and simplified workflows.

## Current product position

UACOS is not a general-purpose AI agent and should not become a Goose clone.

UACOS is best positioned as:

> A local-first repo brain, prompt/context optimizer, agent-code coordination layer, and safety/release gate for AI coding workflows.

In practical terms:

- Goose, Claude Code, Codex, OpenClaw, Aider, Cline, and manual chat workflows can act as coding agents.
- UACOS prepares bounded project context for those agents.
- UACOS validates patches before code changes are trusted.
- UACOS records evidence through tests, release gates, and benchmark reports.
- UACOS stops bounded loops when a spec passes, when safety blocks a patch, or when iteration budget is exhausted.

## Original target alignment

| Original target | Current status | Notes |
|---|---:|---|
| Save tokens | Foundation in place | UACOS has compressed context and repeatable benchmark evidence. Do not claim 80-90% savings without wider real-repo benchmarks. |
| Optimize prompts/context | Strong | Product docs, context packs, memory/skill reuse, and `uacos-flow assist` all reinforce bounded context. |
| Make code changes safer | Strong | Patch validation, secret scanning, impact checks, transactions, rollback, and release gate are core workflows. |
| Stay below agents, not become an agent | Strong | Product boundary explicitly says UACOS is not a Goose clone or general chat agent. |
| Coordinate agents and code | Medium-strong | Orchestration contract and MCP tools exist, but full external-agent execution still needs deeper integration testing. |
| Run a DevOps-style loop | Medium | Bounded planning exists. A production-grade executor loop still needs real multi-agent/client integration. |
| Stop infinite automation | Strong | Orchestration requires `max_iterations`, explicit stop conditions, and evidence. |
| Prove changes through tests | Strong | CI matrix validates compile, tests, self check, and release gate across supported Python versions. |

## What improved in the priority sessions

### Session 1 — Product and workflow contract

Delivered:

- Product boundary: repo brain and safety gate, not a general agent.
- Prepare / Assist / Guard workflow structure.
- MCP-visible product contract.
- Finite four-session upgrade plan.

Impact:

- Prevents product drift into a Goose clone.
- Gives contributors a clear product frame.

### Session 2 — Bounded orchestration contract

Delivered:

- Four core pillars:
  - token and prompt optimization
  - safe code change and upgrade
  - agent-code coordination layer
  - spec-driven DevOps loop
- Orchestration contract.
- MCP tools for orchestration planning and loop decisions.
- Explicit stop conditions and iteration caps.

Impact:

- UACOS can coordinate work without pretending to be the coding agent itself.
- Autonomous loops are constrained by design.

### Session 3 — Benchmark evidence

Delivered:

- Repeatable benchmark manifest.
- Benchmark suite runner.
- Context quality and token-efficiency report schema.
- Release-gate integration.
- Claim policy that blocks unsupported 80-90% token-saving claims.

Impact:

- Token-saving claims must be evidence-driven.
- Benchmark failure can block release readiness.

### Session 4 — Simplified workflow CLI

Delivered:

- `uacos-flow` command wrapper.
- Simple modes:
  - `list`
  - `prepare`
  - `assist`
  - `guard`
  - `orchestrate`
  - `benchmark`
- Backward compatibility with existing `uacos ...` commands.
- Release-gate smoke check for `uacos-flow list`.

Impact:

- Users no longer need to remember the full low-level command surface.
- Existing advanced commands remain available.
- Product usage is easier without risky dispatcher rewrites.

## Current workflow model

```text
External coding agents
Goose / Claude Code / Codex / OpenClaw / Cline / Aider / manual chat
        |
        v
UACOS MCP + uacos-flow
        |
        v
Repo scan -> impact analysis -> compressed context -> patch gate -> tests -> release gate -> benchmark evidence
```

## UACOS vs Goose

| Area | Goose | UACOS |
|---|---|---|
| Product type | General-purpose AI agent runtime | Repo intelligence, context optimizer, orchestration, and safety gate |
| Main user action | Ask an agent to perform work | Prepare/guard/benchmark work done by agents |
| Desktop app | Yes | Not currently |
| CLI | Full agent CLI | Workflow and repo-safety CLI |
| API/MCP ecosystem | Mature provider and extension ecosystem | Local MCP tools focused on repo context and safety |
| Multi-provider support | Strong | Present direction, not primary strength yet |
| Token optimization | Useful but not the core product claim | Core product claim, now guarded by benchmark evidence |
| Patch safety | Agent/tool permission oriented | Patch-scope, secret-scan, transaction, test, rollback, release-gate oriented |
| Best role | The worker/agent | The repo brain, context filter, and safety gate under agents |

## Strategic conclusion

UACOS should not compete with Goose as another general-purpose agent runtime.

The stronger strategy is:

> Make UACOS the repo intelligence and safety layer underneath Goose and other AI coding agents.

A simple product sentence:

> Goose helps agents do work. UACOS helps agents avoid reading blindly, editing blindly, wasting tokens, and claiming success without evidence.

## Current maturity estimate

| Area | Maturity after upgrade | Why |
|---|---:|---|
| Product positioning | 90% | Boundary and workflows are explicit. |
| Token/prompt optimization | 80% | Core system and benchmark suite exist; needs broader real-repo benchmarks. |
| Code safety | 85% | Patch gate, transaction, rollback, release gate, and CI are present. |
| Orchestration layer | 65% | Contract and MCP tools exist; real external-agent integration is next. |
| DevOps loop | 65% | Bounded loop is defined; production executor still needs hardening. |
| Product usability | 70% | `uacos-flow` simplifies usage; dashboard/onboarding still need work. |
| Goose integration readiness | 70% | Product shape is right; needs actual Goose MCP/client test. |
| Commercial clarity | 80% | Differentiation is clear, but proof needs wider benchmark evidence. |

Overall maturity against the original target is currently about **78-82%**.

This should not be presented as final product maturity. It means the project direction, architecture boundary, and safety evidence are now much more aligned with the original goal.

## What remains before a stronger production claim

1. **Real external-agent integration test**
   - Test UACOS with Goose or another MCP-capable agent as a real client.
   - Verify context retrieval, patch submission, validation, and loop decision flow.

2. **Wider real-repo benchmark suite**
   - Run on multiple real repositories, not only UACOS self-repo.
   - Suggested targets: Bear Detector, RTSP Recorder, SuperConnect, EMSTONE/VMS integration code, and UACOS itself.

3. **Production orchestration executor**
   - Move from contract/planning to a guarded executor that delegates to agents and routes all patch application through Guard Mode.

4. **Better onboarding**
   - One-command setup.
   - Clear project templates.
   - Example workflows with real reports.

5. **Dashboard-level visibility**
   - Show context savings, patch risk, release status, benchmark trend, and per-iteration evidence.

## Non-negotiable rules going forward

- Do not turn UACOS into a general-purpose agent.
- Do not claim 80-90% savings without benchmark evidence.
- Do not apply patches outside Guard Mode or explicit transaction/autopilot confirmation.
- Do not allow unbounded loops.
- Do not report done without test/release evidence.
- Prefer adding narrow layers around stable code over rewriting working core engines.
