from pathlib import Path
import tempfile, json
from uacos.storage import init_storage
from uacos.skill.store import add_skill, read_skills
from uacos.skill.executor import skill_execution_plan, execute_skill, execute_best_skill, skill_execution_summary

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        init_storage(repo)
        (repo / "check_target.py").write_text("def value():\n    return 42\n", encoding="utf-8")
        skill = add_skill(
            repo,
            title="Verify Python value module",
            problem_signatures=["verify value module", "python check"],
            root_cause="Need quick Python validation",
            solution_steps=["Run python assertion"],
            commands=["python -S -c \"import check_target; assert check_target.value()==42\""],
            verification=["command returns 0"],
            category="python_test",
            status="approved",
            confidence=0.95,
        )
        plan = skill_execution_plan(repo, skill["id"], task="verify value module")
        assert plan["blocked_count"] == 0
        dry = execute_skill(repo, skill["id"], task="verify value module")
        assert dry["status"] == "dry_run"
        run = execute_skill(repo, skill["id"], task="verify value module", dry_run=False)
        assert run["status"] == "done", run
        best = execute_best_skill(repo, "please verify value module python check", dry_run=True)
        assert best["status"] == "dry_run"
        summary = skill_execution_summary(repo)
        assert summary["count"] >= 3
        used = [s for s in read_skills(repo, include_inactive=True) if s["id"] == skill["id"]][0]
        assert used["times_used"] >= 1
        print("PHASE17_SMOKE_OK")
        print("skill=", skill["id"])
        print("executions=", summary["count"])

if __name__ == "__main__":
    main()
