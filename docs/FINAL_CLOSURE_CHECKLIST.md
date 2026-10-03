# UACOS Final Closure Checklist

This checklist is the final product/CI/documentation closure gate after the WS1-WS5 implementation work.

## Rule

Implementation tests, fixture tests, mocks, binary probes, and localhost contract tests are useful evidence, but they do not substitute for the real-provider and real-benchmark evidence called out below.

Run the explicit closure checker at any time:

```bash
python scripts/final_closure_check.py --repo .
```

This non-strict mode keeps implementation readiness separate from missing real-world evidence. It writes `reports/final_closure_report.json` and reports blockers without pretending they are implementation failures.

For the final DONE gate, require real evidence:

```bash
python scripts/final_closure_check.py --repo . --strict-evidence
```

Strict mode fails unless both the real-provider E2E report and comparative benchmark report are present and PASS.

## Product surface

- [x] Root README uses a simple three-stage workflow: initialize/inspect -> bounded context -> guard/apply verified changes.
- [x] Product definition clearly states that UACOS is reliability/context/safety infrastructure, not a coding agent replacement.
- [x] Existing low-level `uacos ...` commands remain backward compatible.
- [x] Evidence output locations are documented.
- [x] Final closure checker separates implementation readiness from real-world evidence readiness.

## CI

- [x] Main CI runs compile, full tests, self-check, and release gate on Python 3.9/3.11/3.13.
- [x] CI uses the Linux self-hosted runner pool for the active production-validation path.
- [x] Real-agent E2E has a dedicated self-hosted workflow and uploads evidence artifacts.
- [ ] Final exact-head full CI is green after comparative benchmark and final documentation changes converge.

## Real Agent E2E

- [x] Real-provider runner infrastructure exists.
- [x] Missing providers are `unavailable`, never PASS.
- [x] Fixture executables are explicitly excluded from real-provider claims.
- [x] First self-hosted probe artifact was archived.
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

## Final DONE condition

UACOS reaches checklist closure when all of the following are true:

1. exact-head full CI is green;
2. at least one real coding-agent provider has a passing archived E2E run;
3. comparative benchmark observations are real, same-provider/model, repeated, and archived;
4. `python scripts/final_closure_check.py --repo . --strict-evidence` returns PASS;
5. documentation matches those actual results without stronger claims than the evidence supports.
