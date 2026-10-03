from pathlib import Path

from uacos.eval.graph_recall import evaluate_graph_recall
from uacos.graph.builder import build_graph, load_graph
from uacos.graph.change_map import symbols_for_changed_lines
from uacos.graph.roles import classify_source_path


def _write_fixture(repo: Path) -> None:
    (repo / "app" / "api").mkdir(parents=True)
    (repo / "app" / "services").mkdir(parents=True)
    (repo / "app" / "repositories").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "vendor").mkdir()
    (repo / "generated").mkdir()

    (repo / "app" / "api" / "routes.py").write_text(
        "from app.services.user_service import get_user\n"
        "class Router:\n"
        "    def get(self, path):\n"
        "        return lambda fn: fn\n"
        "router = Router()\n"
        "@router.get('/users/{user_id}')\n"
        "def user_handler(user_id):\n"
        "    return get_user(user_id)\n",
        encoding="utf-8",
    )
    (repo / "app" / "services" / "user_service.py").write_text(
        "from app.repositories.user_repository import fetch_user\n"
        "def get_user(user_id):\n"
        "    return fetch_user(user_id)\n",
        encoding="utf-8",
    )
    (repo / "app" / "repositories" / "user_repository.py").write_text(
        "def fetch_user(user_id):\n"
        "    return {'id': user_id}\n",
        encoding="utf-8",
    )
    (repo / "tests" / "test_user.py").write_text(
        "from app.services.user_service import get_user\n"
        "def test_user():\n"
        "    assert get_user(1)['id'] == 1\n",
        encoding="utf-8",
    )
    (repo / "vendor" / "foreign.py").write_text("def vendored(): return 1\n", encoding="utf-8")
    (repo / "generated" / "client.py").write_text("def generated_client(): return 1\n", encoding="utf-8")


def test_route_handler_service_database_and_test_dependencies(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_fixture(repo)

    build_graph(repo)
    graph = load_graph(repo, auto_build=False)

    kinds = {edge["kind"] for edge in graph["architecture_edges"]}
    assert {"route_to_handler", "handler_to_service", "service_to_database"} <= kinds
    assert any(
        edge["kind"] == "handler_to_service"
        and edge["target_file"] == "app/services/user_service.py"
        for edge in graph["architecture_edges"]
    )
    assert any(
        edge["kind"] == "service_to_database"
        and edge["target_file"] == "app/repositories/user_repository.py"
        for edge in graph["architecture_edges"]
    )
    assert any(
        edge["source_file"] == "tests/test_user.py"
        and edge["target_file"] == "app/services/user_service.py"
        for edge in graph["test_dependency_edges"]
    )


def test_changed_lines_map_to_only_intersecting_symbols(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_fixture(repo)
    build_graph(repo)
    graph = load_graph(repo, auto_build=False)

    rows = symbols_for_changed_lines(graph, {"app/services/user_service.py": [(2, 3)]})
    ids = {row["symbol_id"] for row in rows}
    assert "app.services.user_service:get_user" in ids
    assert "app.repositories.user_repository:fetch_user" not in ids


def test_incremental_rebuild_reuses_unchanged_files(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_fixture(repo)
    build_graph(repo)

    service = repo / "app" / "services" / "user_service.py"
    service.write_text(service.read_text(encoding="utf-8") + "\n# changed\n", encoding="utf-8")
    result = build_graph(repo, incremental=True)
    assert result["build"]["reparsed_file_count"] == 1
    assert result["build"]["reused_file_count"] >= 3
    assert result["build"]["deleted_file_count"] == 0


def test_generated_and_vendor_paths_are_excluded(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_fixture(repo)
    build_graph(repo)
    graph = load_graph(repo, auto_build=False)

    assert classify_source_path("vendor/foreign.py") == "vendor"
    assert classify_source_path("generated/client.py") == "generated"
    assert "vendor/foreign.py" not in graph["files"]
    assert "generated/client.py" not in graph["files"]


def test_symbol_and_relation_recall_evaluator(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_fixture(repo)
    build_graph(repo)
    graph = load_graph(repo, auto_build=False)

    report = evaluate_graph_recall(
        graph,
        required_symbol_ids=[
            "app.api.routes:user_handler",
            "app.services.user_service:get_user",
            "app.repositories.user_repository:fetch_user",
        ],
        required_relations=[
            {
                "kind": "handler_to_service",
                "source_symbol_id": "app.api.routes:user_handler",
                "target_symbol_id": "app.services.user_service:get_user",
            },
            {
                "kind": "service_to_database",
                "source_symbol_id": "app.services.user_service:get_user",
                "target_symbol_id": "app.repositories.user_repository:fetch_user",
            },
        ],
    )
    assert report["passed"] is True
    assert report["symbol_recall"] == 1.0
    assert report["relation_recall"] == 1.0
