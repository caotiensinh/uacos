from pathlib import Path
import tempfile
from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.learning.auto import learn_from_file, learn_review, learn_summary, read_learning_events
from uacos.skill.store import approve_skill, suggest_skills
from uacos.retrieval.context_pack import build_context_pack

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        (repo / "app.py").write_text("def ok():\n    return True\n", encoding="utf-8")
        init_storage(repo)
        scan_repo(repo)

        evidence = repo / "evidence.md"
        evidence.write_text(
            "Root cause: Python 3.9 venv is too old for union type syntax.\n"
            "TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'\n"
            "Fix: recreate venv with Python 3.12.\n"
            "py -3.12 -m venv .venv\n"
            "pip install -e .\n"
            "Verify: uacos --help\n",
            encoding="utf-8",
        )
        learned = learn_from_file(repo, evidence, "Fix Python 3.9 union type error")
        assert learned["status"] == "ok"
        assert learned["skill"]["status"] == "candidate"
        assert learned["memory"] is not None
        review = learn_review(repo)
        assert review["candidate_skill_count"] == 1
        approve_skill(repo, learned["skill"]["id"])
        suggested = suggest_skills(repo, "unsupported operand type Python 3.9 NoneType")
        assert suggested
        pack = build_context_pack(repo, "fix unsupported operand type Python 3.9 NoneType", max_tokens=3000)
        assert "Relevant Skills" in pack["content"]
        assert "Fix Python 3.9 union type error" in pack["content"]
        summary = learn_summary(repo)
        assert summary["learning_events"] >= 1
        assert read_learning_events(repo)
        print("PHASE13_SMOKE_OK")
        print("skill=", learned["skill"]["id"])
        print("events=", summary["learning_events"])

if __name__ == "__main__":
    main()
