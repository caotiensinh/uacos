from pathlib import Path
import tempfile
from uacos.storage import init_storage
from uacos.skill.store import add_skill
from uacos.skill.executor import execute_skill
from uacos.learning.feedback import ingest_skill_execution, feedback_summary, skill_feedback_score, recommend_skills

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
            root_cause="Need quick validation",
            solution_steps=["Run python assertion"],
            commands=["python -S -c \"import check_target; assert check_target.value()==42\""],
            category="python_test",
            status="approved",
            confidence=0.95,
        )
        run = execute_skill(repo, skill["id"], task="verify value module", dry_run=False)
        assert run["status"] == "done", run
        fb = ingest_skill_execution(repo, execution_file=Path(run["execution_file"]))
        assert fb["score"]["success_count"] == 1
        score = skill_feedback_score(repo, skill["id"])
        assert score["score"]["reliability"] > 0.5
        rec = recommend_skills(repo, "please verify value module python check")
        assert rec["recommendations"]
        assert rec["recommendations"][0]["id"] == skill["id"]
        summary = feedback_summary(repo)
        assert summary["feedback_events"] >= 1
        print("PHASE18_SMOKE_OK")
        print("skill=", skill["id"])
        print("reliability=", score["score"]["reliability"])

if __name__ == "__main__":
    main()
