from pathlib import Path
import tempfile
from uacos.ops.packaging import bootstrap
from uacos.runtime.agent_runtime import init_runtime, validate_runtime, create_job, run_job_once, list_jobs, runtime_status, job_report

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
        bootstrap(repo)
        init = init_runtime(repo)
        assert init["status"] == "ok"
        val = validate_runtime(repo)
        assert val["status"] == "pass", val
        job = create_job(repo, "fix value function", backend="manual", allowed_files=["app.py"], tests=["python -S -c \"from pathlib import Path; assert 'return 42' in Path('app.py').read_text()\""])
        assert job["status"] == "queued"
        run = run_job_once(repo, job["id"])
        assert run["status"] == "waiting_manual", run
        assert Path(run["prompt_file"]).exists()
        jobs = list_jobs(repo)
        assert jobs["count"] == 1
        status = runtime_status(repo)
        assert status["by_status"].get("waiting_manual") == 1
        report = job_report(repo, job["id"])
        assert "Runtime Job Report" in report
        print("PHASE28_SMOKE_OK")
        print("job=", job["id"])
        print("status=", run["status"])

if __name__ == "__main__":
    main()
