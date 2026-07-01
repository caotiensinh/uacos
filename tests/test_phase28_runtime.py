from pathlib import Path
from uacos.ops.packaging import bootstrap
from uacos.runtime.agent_runtime import init_runtime, validate_runtime, create_job, run_job_once, list_jobs, runtime_status, job_report

def test_runtime_manual_job_flow(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    bootstrap(repo)
    init_runtime(repo)
    assert validate_runtime(repo)["status"] == "pass"
    job = create_job(repo, "fix value", backend="manual", allowed_files=["app.py"], tests=["python -S -c \"from pathlib import Path; assert 'return 42' in Path('app.py').read_text()\""])
    assert job["status"] == "queued"
    run = run_job_once(repo, job["id"])
    assert run["status"] == "waiting_manual", run
    assert Path(run["prompt_file"]).exists()
    assert list_jobs(repo)["count"] == 1
    assert runtime_status(repo)["by_status"]["waiting_manual"] == 1
    assert "Runtime Job Report" in job_report(repo, job["id"])
