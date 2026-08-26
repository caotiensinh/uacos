# UACOS Case Study Template

Use this template to document a real UACOS usage case without exaggerating results.

## Case study title

Example:

> Reducing AI context size for a FastAPI bug fix with UACOS

## Project background

- Repository/project:
- Project type:
- Language/framework:
- Approximate file count:
- Approximate repo size:
- Test framework:
- Deployment environment:

## Problem

Describe the original development problem.

- What needed to change?
- Why was full-repo context expensive or risky?
- What could go wrong if the AI agent edited blindly?

## UACOS workflow used

Commands run:

```bash
uacos-flow setup --repo . --task "..."
uacos-flow assist --repo . --task "..." --max-tokens 6000
uacos-flow guard --repo . --patch change.diff --allowed-file <path> --test "pytest -q"
uacos-flow apply-safe --repo . --patch change.diff --allowed-file <path> --test "pytest -q" --yes
```

## Context evidence

- selected files:
- selected-file explanations:
- symbol context:
- route/API graph findings:
- test map findings:
- config/deploy risk findings:

## Patch safety evidence

- patch scope:
- risk categories:
- secret scan result:
- tests required:
- rollback available:
- lifecycle report path:

## Results

| Metric | Before | With UACOS | Notes |
|---|---:|---:|---|
| Full-repo baseline tokens | | | |
| UACOS context tokens | | | |
| Input-context reduction | | | |
| Test pass rate | | | |
| Files changed | | | |
| Patch review status | | | |
| Release gate status | | | |

## What worked

- 

## What failed or needed manual review

- 

## Limitations

- 

## Supported public claim

Write one conservative claim supported by the evidence.

> 

## Unsupported claims

List claims this case study does not prove.

- It does not prove UACOS always saves the same amount of tokens.
- It does not prove UACOS replaces the AI coding agent.
- It does not prove production readiness by itself.
