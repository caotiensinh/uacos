from uacos.flow_cli import run_assist
from uacos.impact.config_risk import build_config_risk_map, classify_config_file


def test_config_risk_flags_env_and_secret_values(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("API_TOKEN=abc\nDATABASE_URL=postgres://example\n", encoding="utf-8")

    row = classify_config_file(env_file, tmp_path)

    assert row["risk_level"] == "high"
    assert "secret_or_environment_config" in row["categories"]
    assert "database_or_migration" in row["categories"]


def test_config_risk_detects_docker_and_ci_files(tmp_path):
    docker = tmp_path / "Dockerfile"
    docker.write_text("FROM python:3.11\nEXPOSE 8000\n", encoding="utf-8")
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    ci = workflow_dir / "ci.yml"
    ci.write_text("name: CI\njobs:\n  test:\n    steps:\n      - run: pytest\n", encoding="utf-8")

    result = build_config_risk_map(tmp_path, selected_files=[{"file": "Dockerfile"}])

    assert result["status"] == "ok"
    assert result["config_file_count"] == 2
    docker_row = next(row for row in result["config_files"] if row["file"] == "Dockerfile")
    ci_row = next(row for row in result["config_files"] if row["file"] == ".github/workflows/ci.yml")
    assert docker_row["risk_level"] == "medium"
    assert docker_row["in_selected_context"] is True
    assert "container_runtime" in docker_row["categories"]
    assert ci_row["risk_level"] == "high"
    assert "ci_release_pipeline" in ci_row["categories"]


def test_run_assist_includes_config_risk(tmp_path):
    (tmp_path / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")

    result = run_assist(tmp_path, "change project packaging", max_tokens=3000, max_files=4)

    assert result["status"] == "pass"
    assert result["config_risk"]["status"] == "ok"
    assert result["config_risk"]["config_file_count"] >= 1
    assert any(row["file"] == "pyproject.toml" for row in result["config_risk"]["config_files"])
    assert "config_risk" in result["next_step"]
