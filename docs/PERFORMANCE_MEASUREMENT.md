# Performance Measurement

UACOS measures token efficiency with `scripts/uacos_performance_benchmark.py`.

## Command

```bash
python scripts/uacos_performance_benchmark.py --repo .
```

The script writes:

```text
reports/uacos_performance_report.json
```

## Metrics

- `baseline_without_uacos_tokens_est`: estimated tokens if a user manually pasted the full raw impacted files for the task.
- `uacos_context_tokens_est`: estimated tokens in the compressed UACOS task context for the same repo and task.
- `tokens_saved_est`: baseline minus UACOS context tokens.
- `savings_percent`: estimated savings ratio for the measured session.
- `cache_saved_tokens_est_on_repeated_session`: estimated tokens saved when the same task is repeated and served from the UACOS LLM cache.

The token estimator is `uacos.llm.hardened.estimate_tokens`. These numbers are operational estimates for trend tracking and review, not provider billing records.

## Low-Token Output

Use `--summary` to print a short stdout summary while still writing the full JSON report:

```bash
python scripts/uacos_performance_benchmark.py --repo . --summary
```
