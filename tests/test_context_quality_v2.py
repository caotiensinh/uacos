from pathlib import Path

from uacos.eval.context_quality import (
    ContextQualityThresholds,
    evaluate_manifest,
    evaluate_selection,
    evaluate_task_context,
)
from uacos.graph.builder import build_graph


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_evaluate_selection_measures_precision_recall_and_noise():
    result = evaluate_selection(
        ["pkg/a.py", "pkg/b.py", "pkg/noise.py"],
        ["pkg/a.py", "pkg/b.py"],
        selected_symbol_ids=["pkg.a:run", "pkg.b:helper"],
        required_symbol_ids=["pkg.b:helper"],
        thresholds=ContextQualityThresholds(
            min_file_recall=0.95,
            min_required_symbol_recall=0.95,
            max_noise_ratio=0.20,
        ),
    )
    assert result["metrics"]["file_precision"] == 0.6667
    assert result["metrics"]["file_recall"] == 1.0
    assert result["metrics"]["required_symbol_recall"] == 1.0
    assert result["metrics"]["noise_ratio"] == 0.3333
    assert result["status"] == "fail"
    assert "pkg/noise.py" in result["noisy_files"]


def test_support_files_do_not_count_as_noise():
    result = evaluate_selection(
        ["pkg/a.py", "pkg/b.py"],
        ["pkg/b.py"],
        allowed_support_files=["pkg/a.py"],
    )
    assert result["metrics"]["file_precision"] == 1.0
    assert result["metrics"]["file_recall"] == 1.0
    assert result["metrics"]["noise_ratio"] == 0.0
    assert result["status"] == "pass"


def test_task_context_covers_required_symbol_and_reports_provenance(tmp_path: Path):
    _write(tmp_path, "pkg/__init__.py", "")
    _write(tmp_path, "pkg/b.py", "def helper():\n    return 1\n")
    _write(
        tmp_path,
        "pkg/a.py",
        "from .b import helper\n\n"
        "def caller():\n"
        "    return helper()\n",
    )
    _write(tmp_path, "pkg/noise.py", "def unrelated():\n    return 0\n")
    build_graph(tmp_path)

    result = evaluate_task_context(
        tmp_path,
        "helper behavior",
        required_files=["pkg/b.py"],
        required_symbols=["pkg.b:helper"],
        allowed_support_files=["pkg/a.py"],
        max_files=2,
        refresh_graph=False,
    )
    assert result["status"] == "pass"
    assert result["quality"]["metrics"]["file_recall"] == 1.0
    assert result["quality"]["metrics"]["required_symbol_recall"] == 1.0
    assert result["quality"]["metrics"]["noise_ratio"] == 0.0
    assert "pkg/b.py" in result["selection_provenance"]


def test_ambiguous_ground_truth_symbol_fails_instead_of_false_pass(tmp_path: Path):
    _write(tmp_path, "pkg/__init__.py", "")
    _write(tmp_path, "pkg/a.py", "def run():\n    return 1\n")
    _write(tmp_path, "pkg/b.py", "def run():\n    return 2\n")
    build_graph(tmp_path)

    result = evaluate_task_context(
        tmp_path,
        "run",
        required_files=["pkg/a.py"],
        required_symbols=["run"],
        max_files=2,
        refresh_graph=False,
    )
    assert result["status"] == "fail"
    assert result["required_symbol_resolution"]["ambiguous"]
    assert "ambiguous_required_symbols" in result["quality"]["gate_reasons"]


def test_manifest_aggregate_reports_task_pass_rate(tmp_path: Path):
    _write(tmp_path, "pkg/__init__.py", "")
    _write(tmp_path, "pkg/b.py", "def helper():\n    return 1\n")
    _write(
        tmp_path,
        "pkg/a.py",
        "from .b import helper\n\n"
        "def caller():\n"
        "    return helper()\n",
    )
    build_graph(tmp_path)
    manifest = {
        "thresholds": {
            "min_file_recall": 0.95,
            "min_required_symbol_recall": 0.95,
            "max_noise_ratio": 0.50,
        },
        "tasks": [
            {
                "task": "helper behavior",
                "required_files": ["pkg/b.py"],
                "required_symbols": ["pkg.b:helper"],
                "allowed_support_files": ["pkg/a.py"],
                "max_files": 2,
            }
        ],
    }
    result = evaluate_manifest(tmp_path, manifest)
    assert result["task_count"] == 1
    assert result["passed_task_count"] == 1
    assert result["pass_rate"] == 1.0
    assert result["aggregate"]["average_required_symbol_recall"] == 1.0
