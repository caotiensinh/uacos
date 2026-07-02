# Troubleshooting

## `uacos` command is not found

Use the module form:

```bash
python -m uacos.cli --help
```

Or install from the repo:

```bash
python -m pip install -e .
```

## Auto Mode fails

Run:

```bash
python -m uacos.cli auto --repo . --skip-performance
```

Then inspect:

```text
reports/uacos_auto_report.json
```

## Release gate fails

Do not create a release. Inspect:

```text
reports/release_gate_report.json
```

Run the failing command shown in the report.

## Need full debug output

Set the environment variable, then rerun the command:

```bash
# Windows (cmd)
set UACOS_DEBUG=1

# Windows (PowerShell)
$env:UACOS_DEBUG=1

# macOS / Linux
export UACOS_DEBUG=1
```

## Dashboard or MCP server won't start

Both bind to `127.0.0.1` only, by design (see [Security Model](SECURITY_MODEL.md)). If the port is already in use, pick a different `--port`:

```bash
python -m uacos.cli dashboard --repo . --port 8766
python -m uacos.cli mcp-serve --repo . --port 8770
```
