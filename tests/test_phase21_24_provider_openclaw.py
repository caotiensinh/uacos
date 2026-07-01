from pathlib import Path
from uacos.ops.packaging import bootstrap
from uacos.llm.providers import init_llm_config
from uacos.llm.hardened import provider_health_check, run_llm_hardened, provider_summary, configure_model_route, route_provider
from uacos.adapters.openclaw import init_openclaw_adapter, validate_openclaw_config, build_openclaw_prompt, run_openclaw, openclaw_summary

def test_provider_hardening_dry_run(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    bootstrap(repo)
    init_llm_config(repo)
    health = provider_health_check(repo)
    assert health["status"] == "ok"
    configure_model_route(repo, "coding", "dry_run", "dry-run", ["bug"])
    route = route_provider(repo, "fix bug")
    assert route["route"] == "coding"
    res = run_llm_hardened(repo, "hello api_key=SECRET_VALUE", task="fix bug", dry_run=True)
    assert res["status"] == "dry_run"
    hist = (repo / ".uacos" / "llm_provider_history.jsonl").read_text(encoding="utf-8")
    assert "SECRET_VALUE" not in hist
    assert provider_summary(repo)["runs"] >= 1

def test_openclaw_adapter_dry_run(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def ok():\n    return True\n", encoding="utf-8")
    bootstrap(repo)
    init_openclaw_adapter(repo)
    val = validate_openclaw_config(repo)
    assert val["status"] == "pass"
    prompt = build_openclaw_prompt(repo, "fix ok", agent="leader")
    assert prompt["status"] == "ok"
    assert Path(prompt["prompt_file"]).exists()
    run = run_openclaw(repo, "fix ok", agent="leader", real=False)
    assert run["status"] == "dry_run"
    assert openclaw_summary(repo)["runs"] >= 1
