from pathlib import Path

from uacos.context.planner import build_context_plan
from uacos.graph.builder import build_graph
from uacos.impact.analyzer import smart_context


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _repo(tmp_path: Path) -> None:
    _write(tmp_path, "pkg/__init__.py", "")
    _write(
        tmp_path,
        "pkg/service.py",
        "def helper():\n"
        "    return 1\n\n"
        "class Runner:\n"
        "    def run(self):\n"
        "        return helper()\n",
    )
    filler = "\n".join(f"# filler {i}" for i in range(80))
    _write(
        tmp_path,
        "tests/test_service.py",
        filler + "\n\ndef test_runner_failure():\n    assert Runner.run\n",
    )
    _write(tmp_path, "docs/notes.md", "service notes\nRunner.run troubleshooting\n")
    build_graph(tmp_path)


def test_plan_prioritizes_target_contract_neighbor_and_test_support(tmp_path: Path):
    _repo(tmp_path)
    impact = {
        "task": "Runner.run failure",
        "matched_symbol_ids": ["pkg.service:Runner.run"],
        "impacted_files": [
            {
                "file": "pkg/service.py",
                "score": 5.0,
                "reasons": ["symbol:Runner.run"],
                "evidence": [
                    {
                        "kind": "callee:Runner.run",
                        "target_symbol_id": "pkg.service:helper",
                    }
                ],
            },
            {
                "file": "tests/test_service.py",
                "score": 2.0,
                "reasons": ["keyword_search"],
                "evidence": [],
            },
            {
                "file": "docs/notes.md",
                "score": 1.0,
                "reasons": ["keyword_search"],
                "evidence": [],
            },
        ],
    }

    plan = build_context_plan(tmp_path, impact, max_chars=7000, max_files=4)
    by_symbol = {
        row["symbol_id"]: row
        for row in plan["entries"]
        if row.get("symbol_id")
    }
    assert by_symbol["pkg.service:Runner.run"]["role"] == "target"
    assert by_symbol["pkg.service:Runner"]["role"] == "contract"
    assert by_symbol["pkg.service:helper"]["role"] == "neighbor"
    assert by_symbol["pkg.service:Runner.run"]["allocated_chars"] > by_symbol["pkg.service:helper"]["allocated_chars"]

    test_rows = [row for row in plan["entries"] if row.get("file") == "tests/test_service.py"]
    assert test_rows
    assert test_rows[0]["role"] == "test_support"
    assert "Runner.run" in test_rows[0]["content"]
    assert "# filler 0" not in test_rows[0]["content"]


def test_plan_limits_repeated_symbols_from_one_file(tmp_path: Path):
    _repo(tmp_path)
    impact = {
        "task": "Runner.run helper",
        "matched_symbol_ids": ["pkg.service:Runner.run"],
        "impacted_files": [
            {
                "file": "pkg/service.py",
                "score": 5.0,
                "reasons": [],
                "evidence": [
                    {"kind": "a", "symbol_id": "pkg.service:helper"},
                    {"kind": "b", "source_symbol_id": "pkg.service:Runner.run"},
                ],
            }
        ],
    }
    plan = build_context_plan(
        tmp_path,
        impact,
        max_chars=6000,
        max_files=3,
        max_symbols_per_file=1,
    )
    service_slices = [
        row for row in plan["entries"]
        if row.get("file") == "pkg/service.py" and row.get("mode") == "symbol_slice"
    ]
    # Target files may use one extra slot so the target and its containing
    # contract can coexist, but unrelated neighbors cannot monopolize context.
    assert len(service_slices) <= 2
    assert any(row.get("role") == "target" for row in service_slices)


def test_smart_context_reports_dynamic_budget_model(tmp_path: Path):
    _repo(tmp_path)
    result = smart_context(
        tmp_path,
        "fix pkg.service:Runner.run failure",
        max_files=4,
        max_chars=7000,
    )
    assert result["status"] == "ok"
    assert result["context_model"] == "dynamic_semantic_budget_v1"
    assert result["context_plan"]["planner"] == "dynamic_semantic_budget_v1"
    assert result["symbol_slice_count"] >= 1
    assert "pkg.service:Runner.run" in result["content"]
    assert result["char_count"] <= 7000
