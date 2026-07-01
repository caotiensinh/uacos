from pathlib import Path
import tempfile
from uacos.ops.packaging import bootstrap
from uacos.graph.builder import build_graph
from uacos.semantic.search import build_semantic_index
from uacos.budget.optimizer import build_budgeted_context
from uacos.metrics.production import collect_production_metrics, write_metrics_report, write_html_dashboard, production_doctor

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        (repo / "app.py").write_text("def ok():\n    return True\n", encoding="utf-8")
        bootstrap(repo)
        build_graph(repo)
        build_semantic_index(repo)
        build_budgeted_context(repo, "check ok app", profile="small")
        metrics = collect_production_metrics(repo)
        assert metrics["status"] == "ok"
        assert metrics["counts"]["graph_files"] >= 1
        report = write_metrics_report(repo)
        assert Path(report["report"]).exists()
        dash = write_html_dashboard(repo)
        assert Path(dash["dashboard"]).exists()
        html = Path(dash["dashboard"]).read_text(encoding="utf-8")
        assert "UACOS Production Dashboard" in html
        doctor = production_doctor(repo)
        assert doctor["status"] == "pass", doctor
        print("PHASE25_SMOKE_OK")
        print("health=", metrics["health"]["level"])
        print("score=", metrics["health"]["score"])

if __name__ == "__main__":
    main()
