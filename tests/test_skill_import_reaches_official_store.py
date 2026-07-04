from pathlib import Path
import json

from uacos.storage import init_storage
from uacos import skill35
from uacos.skill.store import suggest_skills, skill_summary_for_task, read_skills


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    init_storage(repo)
    return repo


def test_import_skills_reaches_the_official_store_not_just_skill35_local(tmp_path: Path):
    # Regression test: skill35.py's own module docstring states a "Phase 42"
    # production rule that this module "must not implement a separate skill
    # engine" and "routes to the official skill store when available". The
    # actual code violated that rule silently: import_skills() wrote only to
    # .uacos/skill35/ (a separate local store) while claiming
    # "source": "uacos.skill.store" in its response. Skills "imported from
    # outside" via this CLI-documented path never reached
    # uacos.skill.store.suggest_skills()/skill_summary_for_task() — the
    # functions context_pack.py, autopilot, and the MCP server actually read.
    repo = _init_repo(tmp_path)

    external_skill_data = [{
        "task": "fix null pointer in login handler",
        "response": "Check for None before calling .strip() on user input; add a guard clause.",
        "tags": ["login", "null-check"],
        "source": "imported_from_external_blog",
    }]
    import_file = tmp_path / "external_skills.json"
    import_file.write_text(json.dumps(external_skill_data), encoding="utf-8")

    result = skill35.import_skills(str(repo), str(import_file))
    assert result["status"] == "ok"
    assert result["imported"] == 1
    assert result["source"] == "uacos.skill.store"

    # The real test: does the pipeline that actually matters see it?
    suggestions = suggest_skills(repo, "fix null pointer in login handler", min_score=0.0)
    assert suggestions, "imported skill did not reach uacos.skill.store"

    summary = skill_summary_for_task(repo, "fix null pointer in login handler")
    assert "guard clause" in summary


def test_export_then_import_round_trips_through_official_store(tmp_path: Path):
    repo_a = tmp_path / "repo_a"
    repo_a.mkdir()
    init_storage(repo_a)

    from uacos.skill.store import add_skill
    add_skill(
        repo_a,
        title="Fix flaky retry test",
        problem_signatures=["AssertionError: retry count mismatch"],
        root_cause="Test asserted on wall-clock timing under load.",
        solution_steps=["Mock the clock instead of sleeping in the test."],
        tags=["testing", "flaky"],
    )

    export_file = tmp_path / "skills_export.json"
    export_result = skill35.export_skills(str(repo_a), str(export_file))
    assert export_result["status"] == "ok"
    assert export_result["exported"] == 1
    assert export_result["source"] == "uacos.skill.store"

    repo_b = tmp_path / "repo_b"
    repo_b.mkdir()
    init_storage(repo_b)
    import_result = skill35.import_skills(str(repo_b), str(export_file))
    assert import_result["imported"] == 1

    suggestions = suggest_skills(repo_b, "fix flaky retry test wall clock", min_score=0.0)
    assert suggestions
    assert suggestions[0]["title"] == "Fix flaky retry test"
