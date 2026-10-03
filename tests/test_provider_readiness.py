import json

from scripts.provider_readiness import evaluate_provider_readiness


def test_provider_readiness_reports_missing_prerequisites_without_secrets(monkeypatch):
    monkeypatch.setattr("scripts.provider_readiness.shutil.which", lambda _: None)
    report = evaluate_provider_readiness({})
    assert report["status"] == "incomplete"
    codex = next(row for row in report["providers"] if row["provider"] == "codex")
    assert codex["ready_for_real_e2e"] is False
    assert "binary_missing" in codex["blockers"]
    assert "argv_not_configured" in codex["blockers"]
    assert "auth_not_detected" in codex["blockers"]
    assert "OPENAI_API_KEY" not in json.dumps(report)


def test_codex_ready_requires_binary_valid_argv_and_auth(monkeypatch):
    monkeypatch.setattr("scripts.provider_readiness.shutil.which", lambda exe: f"/usr/bin/{exe}" if exe == "codex" else None)
    env = {
        "UACOS_CODEX_ARGV_JSON": '["codex", "exec"]',
        "OPENAI_API_KEY": "secret-value",
    }
    report = evaluate_provider_readiness(env)
    codex = next(row for row in report["providers"] if row["provider"] == "codex")
    assert codex["ready_for_real_e2e"] is True
    assert report["ready_providers"] == ["codex"]
    assert "secret-value" not in json.dumps(report)


def test_invalid_argv_json_is_not_ready(monkeypatch):
    monkeypatch.setattr("scripts.provider_readiness.shutil.which", lambda exe: f"/usr/bin/{exe}")
    report = evaluate_provider_readiness({"UACOS_CODEX_ARGV_JSON": "not-json", "OPENAI_API_KEY": "x"})
    codex = next(row for row in report["providers"] if row["provider"] == "codex")
    assert codex["argv_configured"] is False
    assert "argv_not_configured" in codex["blockers"]
