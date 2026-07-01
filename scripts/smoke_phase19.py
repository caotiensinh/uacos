from pathlib import Path
import tempfile
from uacos.storage import init_storage
from uacos.graph.builder import build_graph, load_graph
from uacos.graph.query import query_symbol, related_files
from uacos.impact.analyzer import impact_by_symbol, impact_by_task, smart_context

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        (repo / "db.py").write_text("def save_user(user):\n    return True\n", encoding="utf-8")
        (repo / "service.py").write_text("from db import save_user\n\ndef validate_user(user):\n    return bool(user)\n\ndef create_user(user):\n    if validate_user(user):\n        return save_user(user)\n    return False\n", encoding="utf-8")
        (repo / "router.py").write_text("from service import create_user\n\ndef route_create(payload):\n    return create_user(payload)\n", encoding="utf-8")
        init_storage(repo)
        built = build_graph(repo)
        assert built["stats"]["file_count"] == 3
        graph = load_graph(repo)
        assert graph["stats"]["call_edge_count"] >= 3
        q = query_symbol(repo, "create_user")
        assert q["matches"]
        imp = impact_by_symbol(repo, "create_user")
        files = [r["file"] for r in imp["impacted_files"]]
        assert "service.py" in files
        assert "router.py" in files or any("router.py" == r["file"] for r in impact_by_task(repo, "fix create_user route bug")["impacted_files"])
        task_imp = impact_by_task(repo, "fix db save_user error")
        task_files = [r["file"] for r in task_imp["impacted_files"]]
        assert "db.py" in task_files
        ctx = smart_context(repo, "fix db save_user error")
        assert "db.py" in ctx["content"]
        assert ctx["included_files"]
        print("PHASE19_SMOKE_OK")
        print("files=", built["stats"]["file_count"])
        print("calls=", graph["stats"]["call_edge_count"])

if __name__ == "__main__":
    main()
