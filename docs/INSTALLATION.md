# Installation

## Requirements

- Python 3.9 through 3.14
- `pytest` for running the full test suite

## From Source

From the UACOS repo:

```bash
python -m pip install -e .
```

Check the CLI:

```bash
uacos --help
```

If the `uacos` executable is not on PATH, use:

```bash
python -m uacos.cli --help
```

## Add UACOS To A Project

From the target project root:

```bash
python -m uacos.cli init --repo .
```

This installs `UACOS_AUTO_START.py` and runs Auto Mode once.
