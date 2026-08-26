from uacos.flow_cli import run_assist
from uacos.impact.api_graph import build_api_graph


def test_api_graph_detects_python_fastapi_routes(tmp_path):
    (tmp_path / "api.py").write_text(
        "from fastapi import APIRouter\n"
        "router = APIRouter()\n"
        "@router.get('/users/{user_id}')\n"
        "def get_user(user_id: str):\n"
        "    return {'id': user_id}\n",
        encoding="utf-8",
    )

    graph = build_api_graph(tmp_path, task="fix users API", selected_files=[{"file": "api.py"}])

    assert graph["status"] == "ok"
    assert graph["route_count"] == 1
    route = graph["routes"][0]
    assert route["method"] == "GET"
    assert route["path"] == "/users/{user_id}"
    assert route["handler"] == "get_user"
    assert route["in_selected_context"] is True
    assert graph["selected_context_files_with_api_items"] == ["api.py"]


def test_api_graph_detects_js_routes_and_client_calls(tmp_path):
    (tmp_path / "server.js").write_text(
        "const express = require('express');\n"
        "router.post('/events', handler);\n",
        encoding="utf-8",
    )
    (tmp_path / "client.ts").write_text(
        "export async function loadEvents(){ return fetch('/events'); }\n"
        "export async function save(){ return axios.post('/events'); }\n",
        encoding="utf-8",
    )

    graph = build_api_graph(tmp_path, task="events API", selected_files=[{"file": "client.ts"}])

    assert graph["route_count"] == 1
    assert graph["client_api_call_count"] == 2
    assert graph["routes"][0]["method"] == "POST"
    assert graph["routes"][0]["path"] == "/events"
    assert {call["method"] for call in graph["client_api_calls"]} == {"GET", "POST"}
    assert graph["relevant_client_api_calls"]


def test_run_assist_includes_api_graph(tmp_path):
    (tmp_path / "api.py").write_text(
        "from fastapi import FastAPI\n"
        "app = FastAPI()\n"
        "@app.post('/events')\n"
        "def create_event():\n"
        "    return {'ok': True}\n",
        encoding="utf-8",
    )

    result = run_assist(tmp_path, "fix events endpoint", max_tokens=3000, max_files=4)

    assert result["status"] == "pass"
    assert result["api_graph"]["status"] == "ok"
    assert result["api_graph"]["route_count"] == 1
    assert result["api_graph"]["routes"][0]["path"] == "/events"
    assert "api_graph" in result["next_step"]
