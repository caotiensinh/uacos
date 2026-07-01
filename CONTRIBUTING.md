# Contributing

Thank you for helping improve UACOS.

## Local Checks

Run before submitting changes:

```bash
python -m compileall -q uacos
python -m pytest -q
python scripts/uacos_self_check.py
python scripts/uacos_performance_benchmark.py --repo . --task "fix MCP SSE endpoint and docs cleanup" --max-files 4 --max-tokens 4000
python scripts/release_gate.py
```

## Rules

- Keep Auto Mode safe by default.
- Do not enable real LLM runs without explicit user action.
- Do not create release artifacts unless `scripts/release_gate.py` passes.
- Keep docs concise and update `docs/DOCUMENTATION_INDEX.md`.
