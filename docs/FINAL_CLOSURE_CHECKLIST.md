# UACOS Final Closure Checklist

This checklist is the final product/CI/documentation closure gate after the WS1-WS5 implementation work.

## Rule

Implementation tests, fixture tests, mocks, binary probes, and localhost contract tests are useful evidence, but they do not substitute for the real-provider and real-benchmark evidence called out below.

## Product surface

- [x] Root README uses a simple three-stage workflow: initialize/inspect -> bounded context -> guard/apply verified changes.
- [x] Product definition clearly states that UACOS is reliability/context/safety infrastructure, not a coding agent replacement.
- [x] Existing low-level `uacos ...` commands remain backward compatible.
- [x] Evidence output locations are documented.

## CI

- [x] Pull-request CI runs compile, full tests, self-check, and release gate on Python 3.9/3.11/3.13.
- [x] Active validation uses the Linux self-hosted runner pool.
- [x] Post-merge `main` CI uses Python 3.11 only to avoid re-running the entire three-version matrix after an exact-head PR already passed all three versions; the Release workflow still triggers only from successful validated `main` CI.
- [x] Real-agent E2E has a dedicated self-hosted workflow and uploads evidence artifacts.
- [ ] Final exact-head full PR CI is green after comparative benchmark and final documentation changes converge.

## Real Agent E2E

- [x] Real-provider runner infrastructure exists.
- [x] Missing providers are `unavailable`, never PASS.
- [x] Fixture executables are explicitly excluded from real-provider claims.
- [x] First self-hosted probe artifact was archived.
- [x] Provider-readiness diagnostics distinguish missing binary, argv, and authentication prerequisites without exposing secret values.
- [ ] Install/configure at least one real provider on an eligible runner.
- [ ] Execute at least one provider through task -> context -> patch -> guard -> tests -> terminal result.
- [ ] Archive real-provider evidence with `status=passed`.
- [ ] Do not claim provider coverage for providers that were not actually executed.

Current blocker from the first self-hosted probe: Codex CLI, Claude Code, and Goose were not installed/resolvable and no provider argv was configured.

## Comparative benchmark

- [x] `full_repo`, `grep`, and `uacos` evaluator exists.
- [x] Same-provider/model enforcement exists.
- [x] At least three unique repeats per task/mode are required.
- [x] Required-symbol recall, required-relation recall, noise, pass rate, first-pass rate, retries, tool calls, tokens, latency, and index overhead are measured.
- [x] Initial targets are encoded: required-symbol recall >=95%, noise <=20%, pass rate >= full-repo, input tokens < full-repo.
- [ ] Collect real observations using one provider/model across all three modes.
- [ ] Run at least three repeats per task/mode.
- [ ] Archive the report and source/evidence identifiers used to produce it.

## Claim policy

- [x] No 80-90% or 99% token claim without direct archived benchmark evidence.
- [x] No real-provider E2E claim based only on fixture/mock/probe runs.
- [x] No claim that UACOS replaces Codex, Claude Code, Goose, or other coding agents.

## Machine-checkable closure

Use non-strict mode during implementation validation:

```bash
python scripts/final_closure_check.py --repo .
```

This keeps implementation status separate from missing real-world evidence and reports the blockers without manufacturing a code failure.

Use strict mode only for final closure:

```bash
python scripts/final_closure_check.py --repo . --strict-evidence
```

Strict mode must fail until both real-provider E2E and the repeated comparative benchmark have archived PASS evidence.

## Final DONE condition

UACOS reaches checklist closure when all of the following are true:

1. exact-head full pull-request CI is green;
2. at least one real coding-agent provider has a passing archived E2E run;
3. comparative benchmark observations are real, same-provider/model, repeated, and archived;
4. documentation matches those actual results without stronger claims than the evidence supports;
5. `python scripts/final_closure_check.py --repo . --strict-evidence` returns PASS.
