from pathlib import Path
from uacos.ops.packaging import bootstrap
from uacos.graph.builder import build_graph, load_graph
from uacos.graph.query import query_symbol
from uacos.impact.analyzer import impact_by_task, smart_context

def test_ast_graph_and_impact(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "db.py").write_text("def save_user(user):\n    return True\n", encoding="utf-8")
    (repo / "service.py").write_text(
        "from db import save_user\n\n"
        "def validate_user(user):\n    return bool(user)\n\n"
        "def create_user(user):\n    if validate_user(user):\n        return save_user(user)\n    return False\n",
        encoding="utf-8",
    )
    (repo / "router.py").write_text("from service import create_user\n\ndef route_create(payload):\n    return create_user(payload)\n", encoding="utf-8")
    bootstrap(repo)
    built = build_graph(repo)
    assert built["stats"]["file_count"] == 3
    graph = load_graph(repo)
    assert graph["stats"]["call_edge_count"] >= 3
    q = query_symbol(repo, "create_user")
    assert q["matches"]
    impact = impact_by_task(repo, "fix save_user create_user bug")
    files = [x["file"] for x in impact["impacted_files"]]
    assert "db.py" in files
    assert "service.py" in files
    ctx = smart_context(repo, "fix save_user create_user bug")
    assert "db.py" in ctx["content"] or "service.py" in ctx["content"]
