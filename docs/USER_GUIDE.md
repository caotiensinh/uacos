# UACOS Quick User Guide

UACOS has two ways to use it:

- **Auto Mode** for normal users: UACOS prepares the project automatically.
- **CLI Mode** for advanced users: run exact commands when needed.

## 1. Auto Mode

From the project root:

```bash
python -m uacos.cli auto-install --repo .
```

This creates:

```text
UACOS_AUTO_START.py
```

After that, non-CLI users can run:

```bash
python UACOS_AUTO_START.py
```

Auto Mode will run bootstrap, health check, graph build, context compression, cache status, skill status, budget status, and write a report.

Report:

```text
reports/uacos_auto_report.json
```

## 2. Auto Watch Mode

Use this when you want UACOS to refresh when files change:

```bash
python -m uacos.cli auto --repo . --watch --interval 10
```

Stop with `Ctrl+C`.

## 3. Common CLI Commands

Check UACOS help:

```bash
python -m uacos.cli --help
```

Prepare a repo:

```bash
python -m uacos.cli bootstrap --repo .
```

Build dependency graph:

```bash
python -m uacos.cli graph-build --repo .
```

Analyze impacted files for a task:

```bash
python -m uacos.cli impact --repo . --task "fix login bug"
```

Create compressed context for AI:

```bash
python -m uacos.cli context-compressed --repo . --task "fix login bug"
```

Run LLM flow in safe dry-run/cache mode:

```bash
python -m uacos.cli llm-run-real --repo . --task "analyze repo quality" --size small
```

Check cache:

```bash
python -m uacos.cli cache-status
```

Check skills:

```bash
python -m uacos.cli skill35-status --repo .
```

Run full release gate:

```bash
python scripts/release_gate.py
```

## 4. Performance Report

Measure token savings:

```bash
python scripts/uacos_performance_benchmark.py --repo .
```

Report:

```text
reports/uacos_performance_report.json
```

## 5. Safety Rules

- Auto Mode does not apply patches by itself.
- Auto Mode does not create releases.
- Real LLM execution stays guarded by config and budget limits.
- Do not release if `python scripts/release_gate.py` fails.

## 6. Dogfood This Repo After Every Upgrade

Use these commands when improving UACOS itself:

```bash
python -m uacos.cli auto --repo . --summary
python scripts/uacos_performance_benchmark.py --repo . --summary
python scripts/release_gate.py
```

`auto --summary` keeps the chat/terminal short, while the full evidence remains in `reports/`. UACOS also saves compact experience into `.uacos/` so the next run can recall prior lessons before preparing context.
