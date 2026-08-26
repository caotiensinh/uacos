from uacos.flow_cli import run_assist
from uacos.impact.explainer import explain_selected_files
from uacos.compression.engine import build_summary_cache


def test_explain_selected_files_adds_roles_and_token_tradeoff(tmp_path):
    (tmp_path / "auth.py").write_text(
        "def login(user, password):\n    return user == 'admin' and password == 'ok'\n",
        encoding="utf-8",
    )
    build_summary_cache(tmp_path)
    selected = [{"file": "auth.py", "score": 1.25, "raw_tokens": 30, "summary_tokens": 20}]
    impact = {"status": "ok", "impacted_files": [{"file": "auth.py", "score": 1.25, "reasons": ["symbol:login", "keyword_search"]}]}

    result = explain_selected_files(tmp_path, "fix login auth", selected, impact=impact)

    assert result["status"] == "ok"
    assert result["explained_file_count"] == 1
    row = result["explanations"][0]
    assert row["file"] == "auth.py"
    assert row["confidence"] == "high"
    assert "security_or_auth" in row["roles"]
    assert "login" in row["matched_task_terms"]
    assert any("symbol match from task: login" in reason for reason in row["reasons"])
    assert any("token tradeoff" in reason for reason in row["reasons"])


def test_run_assist_includes_selection_explanations(tmp_path):
    (tmp_path / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")

    result = run_assist(tmp_path, "change value", max_tokens=3000, max_files=4)

    assert result["status"] == "pass"
    assert "selection_explanations" in result
    assert result["selection_explanations"]["status"] == "ok"
    assert result["selection_explanations"]["explained_file_count"] == result["context"]["selected_file_count"]
    assert "review selection_explanations" in result["next_step"]
