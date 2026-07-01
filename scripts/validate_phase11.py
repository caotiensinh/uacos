from __future__ import annotations


from pathlib import Path
import tempfile, json, subprocess, sys, os
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.skill.store import add_skill, search_skills, suggest_skills, approve_skill, reject_skill, mark_skill_used, read_skills, skill_summary_for_task
from uacos.skill.extract import extract_skill_from_file
from uacos.retrieval.context_pack import build_context_pack

def assert_true(x, msg):
    if not x:
        raise AssertionError(msg)

with tempfile.TemporaryDirectory() as td:
    repo = Path(td) / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def ok():\n    return True\n", encoding="utf-8")
    init_storage(repo)
    scan_repo(repo)

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
    assert_true(skill["id"].startswith("SKILL-"), "skill id")
    found = search_skills(repo, "unsupported operand str None Python39")
    assert_true(found and found[0]["id"] == skill["id"], "skill search")
    approve_skill(repo, skill["id"])
    suggested = suggest_skills(repo, "uacos TypeError unsupported operand type for str | None")
    assert_true(suggested and suggested[0]["status"] == "approved", "skill suggest approve")
    mark_skill_used(repo, skill["id"], task="install uacos")
    used = [s for s in read_skills(repo, include_inactive=True) if s["id"] == skill["id"]][0]
    assert_true(used["times_used"] == 1, "times used")

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
    extracted = extract_skill_from_file(repo, evidence, "Fix Python 3.9 union type error", category="python_env", auto_approve=True)
    assert_true(extracted["status"] == "approved", "extract approved")
    summary = skill_summary_for_task(repo, "unsupported operand type NoneType Python 3.9")
    assert_true("Fix Python 3.9 union type error" in summary, "skill summary")
    pack = build_context_pack(repo, "fix unsupported operand type NoneType Python 3.9", max_tokens=3000)
    assert_true("Relevant Skills" in pack["content"], "context relevant skills")
    assert_true("Fix Python 3.9 union type error" in pack["content"], "context includes skill")

    reject_skill(repo, skill["id"], "test rejection")
    active = read_skills(repo)
    assert_true(not any(s["id"] == skill["id"] for s in active), "reject removes active")

print(json.dumps({"status":"pass","validated":["skill_add_search","skill_lifecycle","skill_extract","context_injection","reject"]}, ensure_ascii=False))
