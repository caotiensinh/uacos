import json
import os
import subprocess
import sys
from pathlib import Path


def test_package_metadata_and_entrypoints():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-m", "uacos", "--help"],
        cwd=root,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "init" in result.stdout
    assert "auto" in result.stdout


def test_cli_error_is_short_without_debug(monkeypatch):
    from uacos.cli import safe_call

    monkeypatch.delenv("UACOS_DEBUG", raising=False)

    def boom():
        raise RuntimeError("example failure")

    data = safe_call(boom)
    assert data["status"] == "error"
    assert data["error_type"] == "RuntimeError"
    assert "next_step" in data
    assert "traceback" not in data


def test_community_readiness_check():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/community_readiness_check.py"],
        cwd=root,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    data = json.loads(result.stdout)
    assert data["status"] == "pass"
