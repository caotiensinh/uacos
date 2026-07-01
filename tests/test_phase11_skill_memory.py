from __future__ import annotations

from pathlib import Path
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.skill.store import add_skill, search_skills, suggest_skills, approve_skill, reject_skill, mark_skill_used, read_skills, skill_summary_for_task
from uacos.skill.extract import extract_skill_from_file
from uacos.retrieval.context_pack import build_context_pack

def test_phase11_skill_add_search_lifecycle(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    init_storage(repo)

    skill = add_skill(
        repo,
        title="Fix Python venv version mismatch",
        problem_signatures=["TypeError: unsupported operand type(s) for |", "str | None", "Python39"],
        root_cause="Python 3.9 venv is too old for Python 3.10+ union syntax.",
        solution_steps=["Recreate venv with Python 3.12", "Reinstall package editable"],
        commands=["py -3.12 -m venv .venv", "pip install -e ."],
        verification=["python --version", "uacos --help"],
        category="python_env",
        status="candidate",
        confidence=0.9,
    )
    assert skill["id"].startswith("SKILL-")

    found = search_skills(repo, "unsupported operand str None Python39")
    assert found
    assert found[0]["id"] == skill["id"]

    approve_skill(repo, skill["id"])
    suggested = suggest_skills(repo, "uacos TypeError unsupported operand type for str | None")
    assert suggested
    assert suggested[0]["status"] == "approved"

    mark_skill_used(repo, skill["id"], task="install uacos")
    rows = read_skills(repo, include_inactive=True)
    used = [s for s in rows if s["id"] == skill["id"]][0]
    assert used["times_used"] == 1

    reject_skill(repo, skill["id"], "test rejection")
    active = read_skills(repo)
    assert not any(s["id"] == skill["id"] for s in active)

def test_phase11_skill_extract_and_context_injection(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def ok():\n    return True\n", encoding="utf-8")
    init_storage(repo)
    scan_repo(repo)

    evidence = repo / "evidence.md"
    evidence.write_text(
        "Root cause: Python 3.9 venv is too old.\n"
        "TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'\n"
        "Fix: recreate venv with Python 3.12.\n"
        "py -3.12 -m venv .venv\n"
        "pip install -e .\n"
        "Verify: uacos --help\n",
        encoding="utf-8",
    )
    skill = extract_skill_from_file(repo, evidence, "Fix Python 3.9 union type error", category="python_env", auto_approve=True)
    assert skill["status"] == "approved"
    assert skill["problem_signatures"]

    summary = skill_summary_for_task(repo, "unsupported operand type NoneType Python 3.9")
    assert "Fix Python 3.9 union type error" in summary

    pack = build_context_pack(repo, "fix unsupported operand type NoneType Python 3.9", max_tokens=3000)
    assert "Relevant Skills" in pack["content"]
    assert "Fix Python 3.9 union type error" in pack["content"]
