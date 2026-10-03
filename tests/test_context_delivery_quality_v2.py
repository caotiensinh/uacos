from pathlib import Path

from uacos.eval.context_quality import (
    ContextQualityThresholds,
    evaluate_delivered_manifest,
    evaluate_delivered_task_context,
    evaluate_task_context,
)
from uacos.graph.builder import build_graph


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_delivered_evaluator_prevents_same_file_false_symbol_pass(tmp_path: Path):
    _write(tmp_path, "pkg/__init__.py", "")
    _write(
        tmp_path,
        "pkg/mod.py",
        "class Worker:\n"
        "    def target(self):\n"
        "        return 1\n\n"
        "    def hidden_required(self):\n"
        "        return 2\n",
    )
    build_graph(tmp_path)

    legacy = evaluate_task_context(
        tmp_path,
        "fix pkg.mod:Worker.target",
        required_files=["pkg/mod.py"],
        required_symbols=["pkg.mod:Worker.hidden_required"],
        max_files=1,
        refresh_graph=False,
    )
    delivered = evaluate_delivered_task_context(
        tmp_path,
        "fix pkg.mod:Worker.target",
        required_files=["pkg/mod.py"],
        required_symbols=["pkg.mod:Worker.hidden_required"],
        max_files=1,
        max_chars=5000,
        refresh_graph=False,
    )

    assert legacy["quality"]["metrics"]["required_symbol_recall"] == 1.0
    assert delivered["quality"]["metrics"]["file_recall"] == 1.0
    assert delivered["quality"]["metrics"]["required_symbol_recall"] == 0.0
    assert delivered["status"] == "fail"
    assert "pkg.mod:Worker.hidden_required" in delivered["quality"]["missing_required_symbol_ids"]


def test_delivered_evaluator_passes_for_symbol_actually_sent_to_agent(tmp_path: Path):
    _write(tmp_path, "pkg/__init__.py", "")
    _write(tmp_path, "pkg/service.py", "def critical_handler(value):\n    return value * 2\n")
    build_graph(tmp_path)

    result = evaluate_delivered_task_context(
        tmp_path,
        "fix pkg.service:critical_handler",
        required_files=["pkg/service.py"],
        required_symbols=["pkg.service:critical_handler"],
        required_roles=["target"],
        max_files=2,
        max_chars=5000,
        thresholds=ContextQualityThresholds(max_noise_ratio=0.5),
        refresh_graph=False,
    )

    assert result["status"] == "pass"
    assert result["evaluation_model"] == "actual_delivered_context_v1"
    assert result["context_model"] == "dynamic_semantic_budget_v1"
    assert result["quality"]["metrics"]["required_symbol_recall"] == 1.0
    assert "pkg.service:critical_handler" in result["delivery"]["included_symbol_ids"]
    assert "target" in result["delivery"]["delivered_roles"]


def test_delivered_manifest_reports_budget_and_delivery_aggregates(tmp_path: Path):
    _write(tmp_path, "pkg/__init__.py", "")
    _write(tmp_path, "pkg/service.py", "def critical_handler(value):\n    return value * 2\n")
    build_graph(tmp_path)

    report = evaluate_delivered_manifest(
        tmp_path,
        {
            "thresholds": {
                "min_file_recall": 0.95,
                "min_required_symbol_recall": 0.95,
                "max_noise_ratio": 0.5,
            },
            "tasks": [
                {
                    "task": "fix pkg.service:critical_handler",
                    "required_files": ["pkg/service.py"],
                    "required_symbols": ["pkg.service:critical_handler"],
                    "required_roles": ["target"],
                    "max_files": 2,
                    "max_chars": 5000,
                }
            ],
        },
    )

    assert report["status"] == "pass"
    assert report["evaluation_model"] == "actual_delivered_context_v1"
    assert report["pass_rate"] == 1.0
    assert report["aggregate"]["average_required_symbol_recall"] == 1.0
    assert report["aggregate"]["average_delivered_symbol_entries"] >= 1.0
    assert report["aggregate"]["average_delivered_entries"] >= 1.0
