# UACOS Onboarding

This guide is for users who want the shortest safe path from a repository to useful AI-agent context.

## One-command setup

Run from the repository root:

```bash
uacos-flow setup --repo . --task "fix login bug safely"
```

This runs local-only preparation steps:

- bootstrap UACOS metadata
- scan/index repository files
- build the Python dependency graph
- build the summary cache
- write convenience dashboard scripts under `.uacos/scripts/`
- run actionable doctor

It does not call cloud LLM providers and does not apply patches.

## Doctor

Run:

```bash
uacos-flow doctor --repo .
```

Doctor returns:

- `status`: `pass`, `warn`, or `fail`
- failed checks
- optional warnings
- recommended commands
- a concrete next step

Example when metadata is missing:

```json
{
  "status": "fail",
  "summary": "not ready",
  "recommended_actions": [
    {
      "check": "db_exists",
      "action": "initialize UACOS metadata",
      "command": "uacos-flow setup --repo ."
    }
  ]
}
```

## Status summary

Run:

```bash
uacos-flow status --repo .
```

Status returns a compact terminal/dashboard-friendly view:

- doctor status
- whether core artifacts are ready
- missing core artifacts
- missing evidence artifacts
- recommended workflow
- next step

An example report is available at:

```text
examples/reports/uacos_flow_status_example.json
```

## Normal workflow after setup

```bash
uacos-flow assist --repo . --task "fix login bug safely" --max-tokens 6000
uacos-flow guard --repo . --patch change.diff --allowed-file app/auth.py --test "pytest -q"
uacos-flow apply-safe --repo . --patch change.diff --allowed-file app/auth.py --test "pytest -q" --yes
```

## Recipes

See [Workflow Recipes](WORKFLOW_RECIPES.md) for common safe workflows:

- first-time setup
- AI-assisted edit
- high-risk config/deploy change
- finite orchestration plan
- benchmark before making public claims

## What setup does not prove

- It does not prove the project is production-ready.
- It does not execute your application.
- It does not apply AI-generated patches.
- It does not prove token-saving claims.
- It does not replace release gate or real tests.

Setup only makes UACOS ready to produce better context, safer patch review, and clearer evidence.
