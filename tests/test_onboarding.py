from uacos.flow_cli import run_doctor, run_setup
from uacos.onboarding import actionable_doctor, setup_project


def test_actionable_doctor_before_setup_recommends_setup(tmp_path):
    result = actionable_doctor(tmp_path)

    assert result["status"] == "fail"
    assert result["failed_count"] > 0
    assert any(action["command"].startswith("uacos-flow setup") for action in result["recommended_actions"])


def test_setup_project_bootstraps_graph_cache_scripts_and_doctor(tmp_path):
    (tmp_path / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")

    result = setup_project(tmp_path, task="change value safely", dashboard_port=9100)

    assert result["status"] == "pass"
    assert result["doctor"]["status"] in {"pass", "warn"}
    assert any(step["name"] == "bootstrap" for step in result["steps"])
    assert any(step["name"] == "graph_build" for step in result["steps"])
    assert any(step["name"] == "summary_cache" for step in result["steps"])
    assert (tmp_path / ".uacos" / "graph" / "dependency_graph.json").exists()
    assert (tmp_path / ".uacos" / "scripts" / "run_uacos_dashboard.sh").exists()
    assert any("uacos-flow assist" in command for command in result["quick_commands"])


def test_flow_setup_and_doctor_modes(tmp_path):
    (tmp_path / "service.py").write_text("def service():\n    return True\n", encoding="utf-8")

    setup = run_setup(tmp_path, task="inspect service", refresh=True, dashboard_port=9101)
    doctor = run_doctor(tmp_path)

    assert setup["status"] == "pass"
    assert doctor["status"] in {"pass", "warn"}
    assert doctor["mode"] == "doctor"
    assert "next_step" in doctor
