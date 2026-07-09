# UACOS Production Improvement Checklist

This checklist turns the current strategic review into a finite production upgrade plan. The goal is to improve UACOS from a useful local engineering tool into a stronger product for developers and teams using AI coding agents.

## Completion rule

A checklist item is not complete until it has:

- scoped implementation
- tests or release-gate evidence
- documented impact
- clear remaining gaps

Do not claim production readiness or 99% token saving without benchmark evidence.

## Phase 1 — Evidence-grade token benchmark

Goal: make token-saving claims measurable and honest.

### Required items

- [x] Separate **full-repo input-context reduction** from **task-local context reduction**.
- [x] Add a clear claim policy for 95-99% input-context reduction.
- [x] Report whether a task meets the 99% input-context target.
- [x] Keep existing benchmark compatibility.
- [x] Add tests for benchmark claim classification.

### Done means

- [x] Benchmark reports include full-repo baseline tokens, UACOS context tokens, task-local baseline tokens, and claim classification.
- [x] Release gate still passes.

### Evidence

- CI run `29003442656` passed compile, tests, self check, and release gate on Python 3.9, 3.11, and 3.13.

## Phase 2 — Real multi-repo benchmark suite

Goal: prove usefulness beyond the UACOS self-repo.

### Required items

- [x] Add manifest support for named external repos or mounted repo paths.
- [x] Add benchmark profiles for at least five real repos:
  - UACOS
  - Bear Detector
  - RTSP Recorder
  - SuperConnect
  - EMSTONE/VMS integration
- [x] Record per-repo benchmark coverage, skipped repos, token reduction, task success, and context quality.
- [x] Add a report that blocks public 80-90% or 99% claims if repo coverage is too narrow.
- [ ] Run the multi-repo benchmark against mounted real repos and archive the generated report.
- [ ] Add real failed-task examples and retry counts from actual agent runs.

### Done means

- [ ] A multi-repo benchmark can run locally and produce comparable reports against the actual target repos.

### Current implementation status

- `evals/multi_repo_benchmark.example.json` provides an example profile for the five target repos.
- Optional repos can be skipped when not mounted, so CI can validate the profile shape without requiring private project repos.
- This is a foundation step, not final proof. Public claims still require real mounted-repo runs.

## Phase 3 — External-agent integration test

Goal: prove UACOS works with real AI coding agents instead of only internal CLI flows.

### Required items

- [x] Add a Goose/MCP integration test plan.
- [x] Verify UACOS can provide context through MCP to an external client using a mock client.
- [x] Verify patch submission can be routed through Guard Mode validation using a mock client.
- [x] Verify loop decision flow with a documented mock client.
- [ ] Verify the same flow with a real Goose or MCP-capable client.
- [ ] Archive real-client evidence: context request, patch validation, tests/release gate, and loop decision.

### Done means

- [ ] A developer can follow one documented flow with a real client: Goose asks UACOS for context, produces patch, UACOS validates, tests run, report is recorded.

### Current implementation status

- `docs/EXTERNAL_AGENT_INTEGRATION.md` documents the integration boundary and mock flow.
- `tests/test_external_agent_mcp_flow.py` starts a localhost MCP server and simulates an external agent calling `list_tools`, `get_context`, `plan_orchestration_loop`, `ingest_patch(apply=false)`, and `loop_decision`.
- This proves the local MCP contract shape, but does not yet prove Goose UI/CLI integration.

## Phase 4 — Patch lifecycle hardening

Goal: make patch review/apply/report safer and easier.

### Required items

- [x] Add `review-patch` style workflow that validates patch, impact alignment, and risk category.
- [ ] Add safe apply flow that always checkpoints before changing code.
- [ ] Add last-run evidence report.
- [x] Add high-risk patch categories:
  - auth changes
  - network calls
  - CI/release scripts
  - dependency files
  - secrets/config files
  - broad multi-file rewrites

### Done means

- [ ] A patch can move through review -> guarded apply -> tests -> rollback/report without manual guessing.

### Current implementation status

- `uacos.security.patch_review` adds patch risk classification around the existing patch gate.
- `uacos-flow guard` now returns `validation`, `risk_review`, and optional `impact_alignment` without applying code.
- `docs/PATCH_LIFECYCLE.md` documents the risk categories and safe lifecycle.
- This is a review/risk foundation step. Safe apply flow and last-run evidence report are still pending.

## Phase 5 — Context intelligence upgrade

Goal: improve file selection quality before chasing extreme token reduction.

### Required items

- [ ] Add symbol-level index support where practical.
- [ ] Add route/API graph support for web apps.
- [ ] Add test-to-source mapping.
- [ ] Add config/deployment risk map.
- [ ] Add selected-file quality metrics.

### Done means

- UACOS can explain why each file was selected and how it relates to the task.

## Phase 6 — Usability and onboarding

Goal: make UACOS easier for real users.

### Required items

- [ ] Add one-command project setup.
- [ ] Add `doctor` output focused on user action, not internal implementation.
- [ ] Add common workflow recipes.
- [ ] Add example reports.
- [ ] Add dashboard summary or terminal TUI for key status.

### Done means

- A new developer can install, prepare a repo, generate context, validate a patch, and read evidence without studying the full command surface.

## Phase 7 — Product proof package

Goal: prepare credible public or customer-facing proof.

### Required items

- [ ] Add public-safe benchmark report template.
- [ ] Add case study format.
- [ ] Add comparison matrix versus using agents directly.
- [ ] Add claim wording guide:
  - safe claim
  - benchmarked claim
  - forbidden claim

### Done means

- UACOS can be presented without overclaiming and without hiding limitations.

## Target claim policy

### Allowed now

> UACOS reduces unnecessary repository context sent to AI coding agents by selecting task-relevant files, compressing context, and validating changes through local safety gates.

### Allowed only after benchmark evidence

> UACOS achieved X% input-context reduction on Y benchmark tasks across Z repositories, while preserving test pass rate of N%.

### Forbidden until proven

- UACOS saves 99% token.
- UACOS always saves 80-90% token.
- UACOS makes AI coding safe automatically.
- UACOS replaces Goose, Codex, Claude Code, or other agents.

### Research target

> Target up to 95-99% full-repo input-context reduction on narrow, task-local changes, with measured task pass-rate protection.
