from __future__ import annotations

import http.client
import json

from uacos.mcp.http_limits import MAX_MCP_REQUEST_BYTES
from uacos.mcp.server import start_test_server


def _request(port: int, *, content_length: str | None, body: bytes = b"") -> tuple[int, dict]:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        conn.putrequest("POST", "/call", skip_accept_encoding=True)
        conn.putheader("Content-Type", "application/json")
        if content_length is not None:
            conn.putheader("Content-Length", content_length)
        conn.endheaders()
        if body:
            conn.send(body)
        response = conn.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        return response.status, payload
    finally:
        conn.close()


def test_mcp_http_rejects_missing_content_length_before_body_read(tmp_path):
    server = start_test_server(tmp_path, port=0)
    try:
        status, payload = _request(server.server_address[1], content_length=None)
        assert status == 411
        assert payload["error"]["message"] == "content_length_required"
    finally:
        server.shutdown()
        server.server_close()


def test_mcp_http_rejects_invalid_content_length_before_body_read(tmp_path):
    server = start_test_server(tmp_path, port=0)
    try:
        status, payload = _request(server.server_address[1], content_length="abc")
        assert status == 400
        assert payload["error"]["message"] == "invalid_content_length"
    finally:
        server.shutdown()
        server.server_close()


def test_mcp_http_rejects_oversized_content_length_without_waiting_for_body(tmp_path):
    server = start_test_server(tmp_path, port=0)
    try:
        status, payload = _request(
            server.server_address[1],
            content_length=str(MAX_MCP_REQUEST_BYTES + 1),
        )
        assert status == 413
        assert payload["error"]["message"] == "request_too_large"
    finally:
        server.shutdown()
        server.server_close()


def test_mcp_http_accepts_normal_bounded_request(tmp_path):
    server = start_test_server(tmp_path, port=0)
    try:
        body = json.dumps({"tool": "list_tools", "arguments": {}, "id": "limit-test"}).encode("utf-8")
        status, payload = _request(
            server.server_address[1],
            content_length=str(len(body)),
            body=body,
        )
        assert status == 200
        assert payload["id"] == "limit-test"
        assert payload["result"]["status"] == "ok"
    finally:
        server.shutdown()
        server.server_close()
