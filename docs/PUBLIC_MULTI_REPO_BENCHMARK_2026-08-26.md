# UACOS Public Multi-Repo Benchmark Report — 2026-08-26

This report records a reproducible public benchmark pilot after merge commit
`943542689737e466c3e4a824cc022a0f139c5d26`.

It is deliberately narrower than the planned target-repository benchmark.
It provides evidence for UACOS, LANCameraViewer, and Cisco Devices Automation
only. It does not close the pending Bear Detector, RTSP Recorder, SuperConnect,
or EMSTONE/VMS Integration benchmark work.

## Summary

- Report name: Public three-repository benchmark pilot
- Date: 2026-08-26
- UACOS version: `4.1.0b4`
- UACOS commit: `943542689737e466c3e4a824cc022a0f139c5d26`
- Benchmark manifest: `evals/public_multi_repo_benchmark.json`
- Benchmark runner: `scripts/uacos_benchmark_suite.py`
- GitHub Actions run: `32982000428`
- Runner OS: Ubuntu 24.04.4 LTS
- Python version: 3.11.16
- Evidence artifact: `9611828175`
- Artifact digest: `sha256:23532ec2680dbaeed4f3848d700865eaad2f8394500597b2513bf8e13fac4658`
- Artifact retention expiry: 2026-11-24

## Repository sources

| Repository | Type | Exact commit | Included |
|---|---|---|---:|
| UACOS | repo intelligence / safety tooling | `943542689737e466c3e4a824cc022a0f139c5d26` | yes |
| LANCameraViewer | Windows RTSP application | `4051ce54a5e53d2bca67b63e6328d34cbaa2cf2b` | yes |
| Cisco Devices Automation | network automation / safety tooling | `e0b7c47becbe2771a5c4b9d7cb8eed27acd499cc` | yes |

No configured repository was skipped.

## Measured tasks

All token values below are estimates produced by
`uacos.llm.hardened.estimate_tokens`; they are not provider billing records.

| Repository | Task | Task-local baseline | Full-repo baseline | UACOS context | Task-local reduction | Full-repo input reduction | Benchmark execution |
|---|---|---:|---:|---:|---:|---:|---|
| UACOS | Trace benchmark claim policy and multi-repo coverage safeguards | 8,192 | 319,194 | 2,713 | 66.88% | 99.15% | OK |
| UACOS | Trace guarded patch apply rollback and lifecycle evidence | 13,487 | 319,194 | 2,733 | 79.74% | 99.14% | OK |
| LANCameraViewer | Trace RTSP adaptive realtime stream switching and reconnect behavior | 13,190 | 69,792 | 3,814 | 71.08% | 94.54% | OK |
| LANCameraViewer | Trace one-command Windows install and diagnostic workflow | 12,143 | 69,792 | 3,791 | 68.78% | 94.57% | OK |
| Cisco Devices Automation | Trace CBS250 context-help pagination safety and write denial | 16,179 | 202,942 | 3,836 | 76.29% | 98.11% | OK |
| Cisco Devices Automation | Trace deterministic validation to safety gate and audit evidence | 9,440 | 202,942 | 3,746 | 60.32% | 98.15% | OK |

## Aggregate results

| Metric | Value |
|---|---:|
| Repositories benchmarked | 3 |
| Benchmark tasks | 6 |
| Benchmark task execution success rate | 100% |
| Configured context-quality checks passed | 3/3 |
| Average context-quality pass rate | 100% |
| Average estimated task-local reduction | 70.52% |
| Average estimated full-repo input-context reduction | 97.28% |
| Tasks meeting at least 95% full-repo input reduction | 4/6 |
| Tasks meeting at least 99% full-repo input reduction | 2/6 |
| Skipped repositories | 0 |
| Required failed suites | 0 |

The benchmark gate required all three repository suites to run. The run passed
with `benchmarked_suite_count=3`, `skipped_suite_count=0`, and
`required_failed_suite_count=0`.

## Calculation definitions

- **Task-local reduction** compares the estimated raw-token size of the task's
  impacted baseline files with the compressed UACOS context for the same task.
- **Full-repo input-context reduction** compares the compressed UACOS context
  with an estimated text snapshot of the entire repository, excluding
  binary/generated/cache files according to the benchmark inventory rules.
- **Context-quality pass rate** uses configured expected-keyword and banned-word
  checks over the compressed context.
- **Benchmark task execution success** means the benchmark context-selection and
  compression task completed successfully. It is not an application test result.
- **Skipped repository policy** requires public evidence to identify skipped
  suites. This run skipped none of the three configured suites.

## Allowed claims from this report

The following wording is supported by this specific benchmark:

> In a six-task benchmark across three public repositories, UACOS reduced
> estimated full-repository input context by 97.28% on average and estimated
> task-local context by 70.52% on average. All six benchmark tasks completed,
> and all three configured context-quality checks passed.

The claim must stay attached to the measured task count, repository count,
estimation method, and benchmark scope.

A task-specific 99% statement is also permitted only when phrased as
**full-repository input-context reduction** for the two measured UACOS tasks
that crossed the 99% threshold.

## Claims not supported by this report

This report does not support any of the following claims:

- UACOS saves 97.28% of total AI workflow tokens.
- UACOS saves 99% of total tokens.
- UACOS always saves 70%, 80%, 90%, 97%, or 99% of tokens.
- UACOS improves application correctness by 100%.
- UACOS makes AI coding automatically safe.
- UACOS replaces an AI coding agent.
- The target five-repository benchmark is complete.
- The result generalizes to repositories or task types that were not measured.

## Limitations

- Token counts are deterministic local estimates, not provider billing data.
- No cloud LLM inference was required for this benchmark.
- The benchmark evaluates context selection/compression and configured quality
  checks; it does not run each external application's complete test suite.
- The pilot covers three repositories, including two external public projects.
- The planned target benchmark against Bear Detector, RTSP Recorder,
  SuperConnect, and EMSTONE/VMS Integration remains pending.
- Tasks were selected to exercise meaningful repository-specific workflows and
  are not a statistically random sample of software-engineering work.
- Real failed-task examples, retry counts, and agent-loop evidence are not part
  of this report.

## Evidence

- Main commit: `943542689737e466c3e4a824cc022a0f139c5d26`
- Standard post-merge CI: run `32982000286` — PASS
- Public multi-repo benchmark: run `32982000428` — PASS
- Benchmark artifact: `9611828175`
- Artifact digest: `sha256:23532ec2680dbaeed4f3848d700865eaad2f8394500597b2513bf8e13fac4658`
- Artifact files:
  - `public_multi_repo_benchmark_report.json`
  - `public_multi_repo_sources.json`

The release workflow subsequently completed successfully and detected the
existing `v4.1.0b4` release without creating a duplicate version.
