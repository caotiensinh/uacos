# Known Issues

- Release must not be produced unless `python scripts/release_gate.py` exits with code 0.
- Real LLM execution depends on local/provider configuration; self-check records failures instead of masking them.
- This sprint intentionally avoids external queue, database, vector-store, and multi-tenant infrastructure.
