# UACOS Claim Wording Guide

This guide prevents UACOS from making claims stronger than the evidence supports.

## Safe baseline claims

These claims are allowed when the repository passes local tests/release gate:

- UACOS is a local-first repo brain and safety layer for AI coding workflows.
- UACOS helps reduce unnecessary context by selecting task-relevant files and compressing summaries.
- UACOS validates AI-generated patches through scope checks, risk review, secret scanning, and guarded apply flows.
- UACOS records local evidence for setup, context, patch review, tests, and release readiness.

## Benchmarked claims

These claims require benchmark evidence from the exact benchmark report being cited:

- UACOS reduced input context by **X%** on **Y tasks** across **Z repositories**.
- UACOS preserved a **N% test pass rate** on the benchmarked task set.
- UACOS reached **X% full-repo input-context reduction** for narrow task-local changes.

A benchmarked claim must include:

- repository count
- task count
- benchmark date or report file
- baseline definition
- UACOS context definition
- pass-rate or validation result
- skipped repo/task count, if any

## Forbidden claims

Do not use these unless there is direct evidence that exactly supports them:

- UACOS saves 99% token.
- UACOS always saves 80-90% token.
- UACOS makes AI coding safe automatically.
- UACOS replaces Goose, Codex, Claude Code, OpenClaw, Cline, or Aider.
- UACOS guarantees correct patches.
- UACOS proves production readiness by itself.

## Correct 99% wording

Allowed only if the benchmark report supports it:

> UACOS achieved up to 99% **full-repo input-context reduction** on narrow, task-local benchmark tasks. This does not mean 99% total workflow token reduction or guaranteed patch correctness.

## Unsafe 99% wording

Do not say:

> UACOS saves 99% of tokens.

That is too broad and misleading.

## Comparison wording

Allowed:

> UACOS complements AI coding agents by preparing bounded context, validating patch scope, and recording local evidence.

Forbidden:

> UACOS is better than Goose/Codex/Claude Code.

Reason: UACOS and agent runtimes solve different layers of the workflow.

## Public release rule

Before publishing a public claim, attach or reference:

- benchmark report
- test/release-gate evidence
- repo/task coverage
- known limitations
