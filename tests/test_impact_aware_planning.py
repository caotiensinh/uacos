from pathlib import Path

from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.graph.builder import build_graph
from uacos.agent.task import create_task
from uacos.retrieval.context_pack import build_context_pack
from uacos.autopilot.orchestrator import autopilot_plan, autopilot_run
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


def test_autopilot_plan_flags_unrestricted_scope_when_impact_finds_nothing(tmp_path: Path):
    # If the objective shares no vocabulary with any real symbol/file name,
    # impact_by_task() returns nothing to suggest. patch_gate.validate_patch_text
    # treats empty allowed_files + allowed_dirs as "no restriction at all" (see
    # uacos/security/patch_gate.py _path_allowed), so this must be surfaced
    # loudly rather than silently producing an unrestricted-scope task.
    repo = _init_repo_with_call_graph(tmp_path)
    plan = autopilot_plan(repo, "Fix checkout", "checkout page shows wrong amount owed")

    assert plan["allowed_files_source"] == "none_determined_scope_open"
    assert plan["allowed_files"] == []
    assert "scope_warning" in plan
    assert "UNRESTRICTED" in plan["scope_warning"]


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


def test_autopilot_run_actually_executes_impact_alignment_step(tmp_path: Path):
    # autopilot_run is only ever called from autopilot_loop(), which never
    # passes patch_file/agent_output — so the "if extracted_patch:" branch
    # (regression_check + impact_alignment) is never exercised by
    # test_autopilot_loop.py. This test calls autopilot_run directly with a
    # real patch_file to prove the wiring actually executes, not just that
    # impact_alignment_check works as a standalone function.
    repo = _init_repo_with_call_graph(tmp_path)
    task_file = create_task(
        repo,
        title="Fix total calc",
        objective="Fix calculate_total to handle empty list",
        allowed_files=["invoice.py"],
        tests=[],
    )
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

    run = autopilot_run(repo, task_file, adapter="ollama_openai", patch_file=patch, apply_changes=True)

    step_names = [s["name"] for s in run["steps"]]
    assert "impact_alignment" in step_names, f"impact_alignment step never ran; steps were {step_names}"
    alignment_step = next(s for s in run["steps"] if s["name"] == "impact_alignment")
    assert alignment_step["status"] == "ok"
    assert alignment_step["result"]["status"] == "pass"
    assert "invoice.py" in alignment_step["result"]["aligned_files"]
    # The patch was on-scope and on-target: it should actually apply, not be blocked.
    assert run["status"] == "done"
