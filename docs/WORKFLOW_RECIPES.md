# UACOS Workflow Recipes

These recipes show the common safe workflows a developer should run after installing UACOS.

## Recipe 1 — First-time setup

```bash
uacos-flow setup --repo . --task "fix login bug safely"
uacos-flow doctor --repo .
uacos-flow status --repo .
```

Use this before giving the repository to an AI coding agent.

## Recipe 2 — Ask an AI agent to edit code safely

```bash
uacos-flow assist --repo . --task "fix login bug safely" --max-tokens 6000
```

Give the returned context to your AI agent.

Then validate the patch:

```bash
uacos-flow guard \
  --repo . \
  --patch change.diff \
  --task "fix login bug safely" \
  --allowed-file app/auth.py \
  --test "pytest -q"
```

Apply only after review:

```bash
uacos-flow apply-safe \
  --repo . \
  --patch change.diff \
  --allowed-file app/auth.py \
  --test "pytest -q" \
  --yes
```

## Recipe 3 — High-risk config/deploy change

```bash
uacos-flow assist --repo . --task "update docker deployment safely" --max-tokens 6000
```

Review `config_risk` before applying any patch. If the patch touches Docker, CI, `.env`, database, or deployment files, treat it as high-risk until reviewed.

```bash
uacos-flow guard \
  --repo . \
  --patch change.diff \
  --allowed-file Dockerfile \
  --test "pytest -q"
```

## Recipe 4 — Finite orchestration plan

```bash
uacos-flow orchestrate \
  --spec "fix failing auth test without broad rewrite" \
  --agent goose \
  --test "pytest -q" \
  --max-iterations 3
```

This creates a bounded plan. It does not run an agent and does not apply patches.

## Recipe 5 — Benchmark before making claims

```bash
uacos-flow benchmark --repo . --manifest evals/benchmark_suite.json
```

Do not claim 80-90% or 99% savings unless benchmark evidence supports it.

## Safe stopping rule

A task is not done just because an agent produced code. A task is done only when there is evidence:

- patch review passed
- tests passed
- release gate or relevant validation passed
- report was recorded
