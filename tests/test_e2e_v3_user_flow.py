from pathlib import Path
from uacos.ops.packaging import bootstrap, health_check
from uacos.graph.builder import build_graph
from uacos.semantic.search import build_semantic_index
from uacos.budget.optimizer import build_budgeted_context
from uacos.compression.engine import compressed_context
from uacos.patching.engine import validate_patch
from uacos.transaction.engine import run_transaction
from uacos.runtime.agent_runtime import init_runtime, create_job, run_job_once
from uacos.metrics.production import production_doctor

def test_v3_user_flow_end_to_end(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    bootstrap(repo)
    assert health_check(repo)["status"] in {"pass", "ok"}
    build_graph(repo)
    build_semantic_index(repo)
    ctx = build_budgeted_context(repo, "fix app value", profile="small")
    assert ctx["selected_file_count"] >= 1
    cctx = compressed_context(repo, "fix app value", max_tokens=4000)
    assert cctx["compressed_tokens_est"] <= 4000

    patch = repo / "change.diff"
    patch.write_text("diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@ -1,2 +1,2 @@\n def value():\n-    return 1\n+    return 42\n", encoding="utf-8")
    assert validate_patch(repo, patch.read_text(encoding="utf-8"), allowed_files=["app.py"])["status"] == "pass"
    tx = run_transaction(repo, patch, title="fix value", allowed_files=["app.py"], tests=["python -S -c \"from pathlib import Path; assert 'return 42' in Path('app.py').read_text()\""])
    assert tx["status"] == "committed"
    init_runtime(repo)
    job = create_job(repo, "review app value", backend="manual", allowed_files=["app.py"])
    run = run_job_once(repo, job["id"])
    assert run["status"] == "waiting_manual"
    doctor = production_doctor(repo)
    assert doctor["status"] == "pass"
