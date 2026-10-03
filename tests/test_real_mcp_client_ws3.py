from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from uacos.mcp.client import HttpJsonRpcMcpClient, McpClientConfig, McpClientError
from uacos.mcp.server import start_test_server


def _client_for(server) -> HttpJsonRpcMcpClient:
    port = server.server_address[1]
    return HttpJsonRpcMcpClient(McpClientConfig(base_url=f"http://127.0.0.1:{port}", timeout_seconds=5))


def test_real_mcp_client_lists_and_calls_tools_over_network(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    server = start_test_server(repo, port=0)
    try:
        client = _client_for(server)
        health = client.probe()
        listed = client.list_tools()
        status = client.call_tool("status")
        assert health["status"] == "ok"
        assert listed["status"] == "ok"
        assert listed["pages"] == 1
        assert any(tool.get("name") == "get_context" for tool in listed["tools"])
        assert status["status"] == "ok"
    finally:
        server.shutdown()
        server.server_close()


def test_real_mcp_client_concurrent_calls_keep_request_ids_isolated(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    server = start_test_server(repo, port=0)
    try:
        client = _client_for(server)
        with ThreadPoolExecutor(max_workers=4) as pool:
            rows = list(pool.map(lambda _: client.call_tool("list_tools"), range(8)))
        assert len(rows) == 8
        assert all(row["status"] == "ok" for row in rows)
        assert all(row["tools"] for row in rows)
    finally:
        server.shutdown()
        server.server_close()


def test_real_mcp_client_rejects_unknown_remote_method(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    server = start_test_server(repo, port=0)
    try:
        client = _client_for(server)
        try:
            client.jsonrpc("not/a/method")
        except McpClientError as exc:
            assert "mcp_http_error:400" in str(exc)
        else:
            raise AssertionError("unknown method must fail")
    finally:
        server.shutdown()
        server.server_close()
