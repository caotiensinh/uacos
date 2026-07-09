from uacos.flow_cli import run_assist
from uacos.graph.builder import build_graph
from uacos.impact.symbol_context import build_symbol_context


def test_symbol_context_explains_selected_file_symbols_and_calls(tmp_path):
    (tmp_path / "service.py").write_text(
        "def value():\n"
        "    return 1\n",
        encoding="utf-8",
    )
    (tmp_path / "app.py").write_text(
        "from service import value\n\n"
        "def main():\n"
        "    return value()\n",
        encoding="utf-8",
    )
    build_graph(tmp_path)

    result = build_symbol_context(tmp_path, task="change value", selected_files=[{"file": "service.py"}])

    assert result["status"] == "ok"
    assert result["selected_file_count"] == 1
    service_symbols = next(row for row in result["selected_file_symbols"] if row["file"] == "service.py")
    assert any("value" in symbol for symbol in service_symbols["symbols"])
    assert result["task_symbol_matches"]
    assert any(edge["source_file"] == "app.py" for edge in result["incoming_calls_to_selected"])
    assert any(edge["source"] == "app.py" for edge in result["incoming_imports_to_selected"])


def test_symbol_context_falls_back_to_task_symbol_matches(tmp_path):
    (tmp_path / "service.py").write_text("def calculate_total():\n    return 42\n", encoding="utf-8")
    build_graph(tmp_path)

    result = build_symbol_context(tmp_path, task="calculate total", selected_files=[])

    assert result["status"] == "ok"
    assert result["selected_file_count"] >= 1
    assert any(row["file"] == "service.py" for row in result["selected_file_symbols"])


def test_run_assist_includes_symbol_context(tmp_path):
    (tmp_path / "service.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    (tmp_path / "app.py").write_text("from service import value\ndef main(): return value()\n", encoding="utf-8")

    result = run_assist(tmp_path, "change value", max_tokens=3000, max_files=4)

    assert result["status"] == "pass"
    assert result["symbol_context"]["status"] == "ok"
    assert "graph_stats" in result["symbol_context"]
    assert "symbol_context" in result["next_step"]
