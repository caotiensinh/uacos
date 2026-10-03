from pathlib import Path

from uacos.graph.builder import build_graph
from uacos.impact.analyzer import impact_by_task


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_qualified_symbol_candidate_is_preserved(tmp_path: Path):
    _write(tmp_path, "pkg/__init__.py", "")
    _write(tmp_path, "pkg/service.py", "class Worker:\n    def run(self):\n        return 1\n")
    build_graph(tmp_path)

    result = impact_by_task(tmp_path, "fix pkg.service:Worker.run timeout", limit=3)
    assert result["ranking_model"] == "evidence_weighted_v2"
    assert "pkg.service:Worker.run" in result["symbol_candidates"]
    assert "pkg.service:Worker.run" in result["matched_symbol_ids"]
    assert result["impacted_files"][0]["file"] == "pkg/service.py"
    assert result["impacted_files"][0]["evidence_count"] >= 2


def test_multiple_independent_signals_accumulate_score(tmp_path: Path):
    _write(tmp_path, "pkg/__init__.py", "")
    _write(tmp_path, "pkg/helper.py", "def helper():\n    return 1\n")
    _write(
        tmp_path,
        "pkg/caller.py",
        "from .helper import helper\n\n"
        "def call_helper():\n"
        "    return helper()\n",
    )
    _write(tmp_path, "pkg/noise.py", "def unrelated():\n    return 0\n")
    build_graph(tmp_path)

    result = impact_by_task(tmp_path, "helper", limit=3)
    rows = {row["file"]: row for row in result["impacted_files"]}
    assert "pkg/helper.py" in rows
    assert rows["pkg/helper.py"]["score"] > 1.0
    assert any(reason.startswith("symbol:helper") for reason in rows["pkg/helper.py"]["reasons"])
    assert rows["pkg/helper.py"]["evidence"]


def test_ambiguous_symbol_keeps_all_semantic_candidates_visible(tmp_path: Path):
    _write(tmp_path, "pkg/__init__.py", "")
    _write(tmp_path, "pkg/a.py", "def run():\n    return 1\n")
    _write(tmp_path, "pkg/b.py", "def run():\n    return 2\n")
    build_graph(tmp_path)

    result = impact_by_task(tmp_path, "run", limit=4)
    hits = [row for row in result["symbol_hits"] if row["query"] == "run"]
    assert len(hits) == 2
    assert all(row["ambiguous"] is True for row in hits)
    assert {row["symbol_id"] for row in hits} == {"pkg.a:run", "pkg.b:run"}


def test_ranking_is_deterministic_for_equal_scores(tmp_path: Path):
    _write(tmp_path, "pkg/__init__.py", "")
    _write(tmp_path, "pkg/a.py", "def same():\n    return 1\n")
    _write(tmp_path, "pkg/b.py", "def same():\n    return 2\n")
    build_graph(tmp_path)

    first = impact_by_task(tmp_path, "same", limit=4)
    second = impact_by_task(tmp_path, "same", limit=4)
    assert first["impacted_files"] == second["impacted_files"]
