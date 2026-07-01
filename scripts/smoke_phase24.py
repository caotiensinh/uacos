from pathlib import Path
import tempfile
from uacos.storage import init_storage
from uacos.adapters.openclaw import init_openclaw_adapter, validate_openclaw_config, openclaw_health, build_openclaw_prompt, run_openclaw, openclaw_summary

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        (repo / "app.py").write_text("def ok():\n    return True\n", encoding="utf-8")
        init_storage(repo)
        init = init_openclaw_adapter(repo)
        assert init["status"] == "ok"
        val = validate_openclaw_config(repo)
        assert val["status"] == "pass", val
        health = openclaw_health(repo)
        assert health["status"] == "ok"
        prompt = build_openclaw_prompt(repo, "fix ok function", agent="leader")
        assert prompt["status"] == "ok"
        assert Path(prompt["prompt_file"]).exists()
        run = run_openclaw(repo, "fix ok function", agent="leader", real=False)
        assert run["status"] == "dry_run", run
        summary = openclaw_summary(repo)
        assert summary["runs"] >= 1
        print("PHASE24_SMOKE_OK")
        print("prompt_chars=", prompt["prompt_chars"])
        print("runs=", summary["runs"])

if __name__ == "__main__":
    main()
