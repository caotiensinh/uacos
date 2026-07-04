from pathlib import Path

from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.graph.builder import build_graph
from uacos.retrieval.context_pack import build_context_pack
from uacos.autopilot.orchestrator import autopilot_plan
from uacos.impact.analyzer import impact_alignment_check


def _init_repo_with_call_graph(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "invoice.py").write_text(
        "def calculate_total(items):\n"
        "    return sum(items)\n",
        encoding="utf-8",
    )
    (repo / "report.py").write_text(
        "from invoice import calculate_total\n\n"
        "def build_report(items):\n"
        "    return calculate_total(items)\n",
        encoding="utf-8",
    )
    init_storage(repo)
    scan_repo(repo)
    build_graph(repo)
    return repo


def test_context_pack_includes_impact_ranking_section(tmp_path: Path):
    repo = _init_repo_with_call_graph(tmp_path)
    pack = build_context_pack(repo, "Fix calculate_total to handle empty list", max_tokens=3000)

    assert "Impact Analysis" in pack["content"]
    assert "impact_ranked_files" in pack
    ranked_paths = [row["file"] for row in pack["impact_ranked_files"]]
    assert "invoice.py" in ranked_paths


def test_autopilot_plan_auto_suggests_allowed_files_from_impact(tmp_path: Path):
    repo = _init_repo_with_call_graph(tmp_path)
    plan = autopilot_plan(repo, "Fix total calc", "Fix calculate_total to handle empty list")

    assert plan["allowed_files_source"] == "impact_analysis_auto_suggested"
    assert "invoice.py" in plan["allowed_files"]


def test_autopilot_plan_respects_explicit_allowed_files(tmp_path: Path):
    repo = _init_repo_with_call_graph(tmp_path)
    plan = autopilot_plan(
        repo,
        "Fix total calc",
        "Fix calculate_total to handle empty list",
        allowed_files=["report.py"],
    )

    assert plan["allowed_files_source"] == "user"
    assert plan["allowed_files"] == ["report.py"]


def test_impact_alignment_check_passes_when_patch_matches_impact(tmp_path: Path):
    repo = _init_repo_with_call_graph(tmp_path)
    patch = repo / "change.diff"
    patch.write_text(
        "diff --git a/invoice.py b/invoice.py\n"
        "--- a/invoice.py\n"
        "+++ b/invoice.py\n"
        "@@ -1,2 +1,2 @@\n"
        " def calculate_total(items):\n"
        "-    return sum(items)\n"
        "+    return sum(items) if items else 0\n",
        encoding="utf-8",
    )
    result = impact_alignment_check(repo, "Fix calculate_total to handle empty list", patch)
    assert result["status"] == "pass"
    assert "invoice.py" in result["aligned_files"]
    assert result["unranked_files"] == []


def test_impact_alignment_check_warns_on_unrelated_file(tmp_path: Path):
    repo = _init_repo_with_call_graph(tmp_path)
    (repo / "unrelated_config.py").write_text("SETTING = 1\n", encoding="utf-8")
    patch = repo / "change.diff"
    patch.write_text(
        "diff --git a/unrelated_config.py b/unrelated_config.py\n"
        "--- a/unrelated_config.py\n"
        "+++ b/unrelated_config.py\n"
        "@@ -1 +1 @@\n"
        "-SETTING = 1\n"
        "+SETTING = 2\n",
        encoding="utf-8",
    )
    result = impact_alignment_check(repo, "Fix calculate_total to handle empty list", patch)
    assert result["status"] == "warn"
    assert "unrelated_config.py" in result["unranked_files"]
