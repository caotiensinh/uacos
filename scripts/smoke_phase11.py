from __future__ import annotations

from pathlib import Path
import tempfile
from uacos.storage import init_storage
from uacos.skill.store import add_skill, suggest_skills
from uacos.retrieval.context_pack import build_context_pack
from uacos.scanner.file_scanner import scan_repo

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        (repo / "main.py").write_text("def ok():\n    return True\n", encoding="utf-8")
        init_storage(repo)
        scan_repo(repo)
        skill = add_skill(
            repo,
            title="Fix Python venv mismatch",
            problem_signatures=["unsupported operand type", "Python39", "str | None"],
            root_cause="Old Python runtime",
            solution_steps=["Recreate venv with Python 3.12"],
            commands=["py -3.12 -m venv .venv"],
            category="python_env",
            status="approved",
            confidence=0.95,
        )
        suggested = suggest_skills(repo, "unsupported operand Python39 str None", limit=3)
        pack = build_context_pack(repo, "fix unsupported operand Python39 str None", max_tokens=3000)
        assert suggested
        assert suggested[0]["id"] == skill["id"]
        assert "Relevant Skills" in pack["content"]
        assert "Fix Python venv mismatch" in pack["content"]
        print("PHASE11_SMOKE_OK")
        print("skill=", skill["id"])
        print("suggested=", len(suggested))

if __name__ == "__main__":
    main()
