#!/usr/bin/env bash
set -euo pipefail

rm -rf /tmp/uacos_smoke_env
python -m venv /tmp/uacos_smoke_env
/tmp/uacos_smoke_env/bin/pip install -q .
/tmp/uacos_smoke_env/bin/uacos --help
mkdir -p /tmp/smoke_repo
cd /tmp/smoke_repo
/tmp/uacos_smoke_env/bin/uacos init --repo .
/tmp/uacos_smoke_env/bin/uacos auto --repo . --summary

echo "SMOKE PASS"
