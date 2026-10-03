from pathlib import Path

import pytest

from uacos.agent.provider_profiles import (
    create_provider_adapter,
    get_provider_profile,
    probe_provider,
    provider_catalog,
)


def test_catalog_contains_required_real_agent_profiles():
    names = {row["name"] for row in provider_catalog()}
    assert {"codex", "claude_code", "goose"}.issubset(names)
    assert get_provider_profile("codex").executable == "codex"
    assert get_provider_profile("claude_code").executable == "claude"
    assert get_provider_profile("goose").executable == "goose"


def test_provider_requires_explicit_version_safe_argv():
    with pytest.raises(ValueError, match="provider_argv_required:codex"):
        create_provider_adapter("codex", argv=None)


def test_provider_rejects_wrong_executable():
    with pytest.raises(ValueError, match="provider_executable_mismatch:goose"):
        create_provider_adapter("goose", argv=["python", "fake_goose.py"])


def test_provider_builds_normalized_subprocess_adapter(tmp_path: Path):
    adapter = create_provider_adapter(
        "codex",
        argv=["codex", "exec", "-"],
        version="test-version",
        cwd=tmp_path,
        env={"UACOS_TEST": "1"},
    )
    assert adapter.name == "codex"
    assert adapter.version == "test-version"
    assert adapter.argv == ["codex", "exec", "-"]
    assert adapter.cwd == tmp_path
    assert adapter.env["UACOS_TEST"] == "1"


def test_probe_provider_reports_resolved_binary(monkeypatch):
    monkeypatch.setattr("uacos.agent.provider_profiles.shutil.which", lambda exe: f"/opt/bin/{exe}")
    result = probe_provider("claude_code")
    assert result["available"] is True
    assert result["resolved_path"] == "/opt/bin/claude"
    assert result["requires_explicit_argv"] is True


def test_unknown_provider_fails_closed():
    with pytest.raises(ValueError, match="unknown_provider_profile"):
        get_provider_profile("mystery")
