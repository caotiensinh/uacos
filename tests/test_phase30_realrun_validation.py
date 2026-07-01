from pathlib import Path
from uacos.validation.realrun import realrun_preflight, mock_provider_e2e, runtime_provider_mock_e2e, ollama_realrun_check, openclaw_realrun_check, phase30_full_validation

def test_phase30_preflight_and_mock_provider(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    pre = realrun_preflight(repo)
    assert pre["status"] == "pass", pre
    mock = mock_provider_e2e(repo, port=0)
    assert mock["status"] == "pass", mock
    ollama_dry = ollama_realrun_check(repo, real=False)
    assert ollama_dry["status"] == "pass", ollama_dry
    openclaw_dry = openclaw_realrun_check(repo, real=False)
    assert openclaw_dry["status"] == "pass", openclaw_dry

def test_phase30_runtime_mock_e2e(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    result = runtime_provider_mock_e2e(repo, port=0)
    assert result["status"] == "pass", result
    assert "return 42" in (repo / "app.py").read_text(encoding="utf-8")

def test_phase30_full_validation(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    result = phase30_full_validation(repo)
    assert result["status"] == "pass", result
