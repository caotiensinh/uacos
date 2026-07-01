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

Set:

```bash
set UACOS_DEBUG=1
```

Then rerun the command.
