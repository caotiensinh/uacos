# Security Model

UACOS is local-first and safe by default.

## Safe By Default

- `uacos init` and `uacos auto` prepare index, graph, cache, context, and reports.
- They do not apply code patches.
- They do not create release artifacts.
- They do not enable real LLM execution.

## Real Mode

Real LLM execution requires explicit action:

```bash
python -m uacos.cli llm33-allow-real --repo . --yes
python -m uacos.cli llm-run-real --repo . --task "analyze repo" --size small --real
```

Budget checks remain active.

## MCP

The MCP server only accepts `127.0.0.1` or `localhost` by default:

```bash
python -m uacos.cli mcp-serve --repo . --host 127.0.0.1 --port 8769
```
