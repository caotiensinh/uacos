from pathlib import Path
import tempfile
from uacos.storage import init_storage
from uacos.llm.providers import init_llm_config
from uacos.llm.hardened import provider_health_check, run_llm_hardened, provider_summary, configure_model_route, route_provider, estimate_tokens, estimate_cost, redact_text

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        init_storage(repo)
        init_llm_config(repo)
        health = provider_health_check(repo)
        assert health["status"] == "ok"
        configure_model_route(repo, "coding", "dry_run", "dry-run", ["code", "bug"])
        route = route_provider(repo, "fix code bug")
        assert route["route"] == "coding"
        res = run_llm_hardened(repo, "hello api_key=SECRET_VALUE", task="fix code bug", dry_run=True)
        assert res["status"] == "dry_run"
        summary = provider_summary(repo)
        assert summary["runs"] >= 1
        assert estimate_tokens("hello world") >= 1
        assert estimate_cost("dry-run", 100, 50)["estimated_cost_usd"] == 0.0
        assert "SECRET_VALUE" not in redact_text("api_key=SECRET_VALUE")
        hist = (repo / ".uacos" / "llm_provider_history.jsonl").read_text(encoding="utf-8")
        assert "SECRET_VALUE" not in hist
        print("PHASE21_SMOKE_OK")
        print("route=", route["route"])
        print("runs=", summary["runs"])

if __name__ == "__main__":
    main()
