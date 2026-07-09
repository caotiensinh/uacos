from uacos.flow_cli import run_assist
from uacos.impact.test_map import map_tests_to_sources, suggest_tests_for_selected_files


def test_map_tests_to_sources_by_pytest_name_and_import(tmp_path):
    (tmp_path / "service.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_service.py").write_text(
        "from service import value\n\n"
        "def test_value():\n"
        "    assert value() == 1\n",
        encoding="utf-8",
    )

    result = map_tests_to_sources(tmp_path, source_files=["service.py"])

    assert result["status"] == "ok"
    assert result["mapped_source_count"] == 1
    mapping = result["mappings"][0]
    assert mapping["source_file"] == "service.py"
    assert mapping["confidence"] == "high"
    assert mapping["tests"][0]["test_file"] == "tests/test_service.py"
    assert "import_or_reference_match" in mapping["tests"][0]["reasons"]
    assert "python -m pytest -q tests/test_service.py" in mapping["tests"][0]["recommended_commands"]
    assert any("::test_value" in command for command in mapping["tests"][0]["recommended_commands"])


def test_map_tests_to_sources_by_js_test_naming(tmp_path):
    (tmp_path / "client.ts").write_text("export function value(){ return 1 }\n", encoding="utf-8")
    (tmp_path / "client.test.ts").write_text("import { value } from './client'\n", encoding="utf-8")

    result = map_tests_to_sources(tmp_path, source_files=["client.ts"])

    assert result["mapped_source_count"] == 1
    mapping = result["mappings"][0]
    assert mapping["tests"][0]["test_file"] == "client.test.ts"
    assert "npm test -- client.test.ts" in mapping["tests"][0]["recommended_commands"]


def test_suggest_tests_for_selected_files_filters_non_sources(tmp_path):
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / "app.py").write_text("def app():\n    return True\n", encoding="utf-8")
    (tmp_path / "test_app.py").write_text("from app import app\ndef test_app(): assert app()\n", encoding="utf-8")

    result = suggest_tests_for_selected_files(tmp_path, [{"file": "README.md"}, {"file": "app.py"}])

    assert result["source_count"] == 1
    assert result["mappings"][0]["source_file"] == "app.py"
    assert result["mappings"][0]["test_count"] == 1


def test_run_assist_includes_test_map(tmp_path):
    (tmp_path / "service.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    (tmp_path / "test_service.py").write_text("from service import value\ndef test_value(): assert value() == 1\n", encoding="utf-8")

    result = run_assist(tmp_path, "change service value", max_tokens=3000, max_files=4)

    assert result["status"] == "pass"
    assert result["test_map"]["status"] == "ok"
    assert result["test_map"]["mapped_source_count"] >= 1
    assert "test_map" in result["next_step"]
