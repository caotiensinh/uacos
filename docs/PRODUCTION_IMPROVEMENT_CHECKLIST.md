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

- [ ] Separate **full-repo input-context reduction** from **task-local context reduction**.
- [ ] Add a clear claim policy for 95-99% input-context reduction.
- [ ] Report whether a task meets the 99% input-context target.
- [ ] Keep existing benchmark compatibility.
- [ ] Add tests for benchmark claim classification.

### Done means

- Benchmark reports include full-repo baseline tokens, UACOS context tokens, task-local baseline tokens, and claim classification.
- Release gate still passes.

## Phase 2 — Real multi-repo benchmark suite

Goal: prove usefulness beyond the UACOS self-repo.

### Required items

- [ ] Add manifest support for named external repos or mounted repo paths.
- [ ] Add benchmark profiles for at least five real repos:
  - Bear Detector
  - RTSP Recorder
  - SuperConnect
  - EMSTONE/VMS integration
  - UACOS
- [ ] Record per-repo pass rate, token reduction, retry count, and failed task examples.
- [ ] Add a report that blocks public 80-90% or 99% claims if repo coverage is too narrow.

### Done means

- A multi-repo benchmark can run locally and produce comparable reports.

## Phase 3 — External-agent integration test

Goal: prove UACOS works with real AI coding agents instead of only internal CLI flows.

### Required items

- [ ] Add a Goose/MCP integration test plan.
- [ ] Verify UACOS can provide context through MCP to an external client.
- [ ] Verify patch submission can be routed through Guard Mode.
- [ ] Verify loop decision flow with at least one real client or documented mock client.

### Done means

- A developer can follow one documented flow: Goose asks UACOS for context, produces patch, UACOS validates, tests run, report is recorded.

## Phase 4 — Patch lifecycle hardening

Goal: make patch review/apply/report safer and easier.

### Required items

- [ ] Add `review-patch` style workflow that validates patch, impact alignment, and risk category.
- [ ] Add safe apply flow that always checkpoints before changing code.
- [ ] Add last-run evidence report.
- [ ] Add high-risk patch categories:
  - auth changes
  - network calls
  - CI/release scripts
  - dependency files
  - secrets/config files
  - broad multi-file rewrites

### Done means

- A patch can move through review -> guarded apply -> tests -> rollback/report without manual guessing.

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
