from __future__ import annotations

from dataclasses import dataclass
import json
import threading
import urllib.error
import urllib.request
import uuid
from typing import Any


class McpClientError(RuntimeError):
    pass


@dataclass(frozen=True)
class McpClientConfig:
    base_url: str
    timeout_seconds: float = 30.0
    max_response_bytes: int = 4 * 1024 * 1024
    max_pages: int = 32

    def normalized_base_url(self) -> str:
        base = self.base_url.rstrip("/")
        if not (base.startswith("http://") or base.startswith("https://")):
            raise ValueError("mcp_base_url_must_be_http_or_https")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds_must_be_positive")
        if self.max_response_bytes <= 0:
            raise ValueError("max_response_bytes_must_be_positive")
        if self.max_pages <= 0:
            raise ValueError("max_pages_must_be_positive")
        return base


class HttpJsonRpcMcpClient:
    """Small synchronous MCP JSON-RPC client for real HTTP endpoints.

    It performs actual network I/O, validates JSON-RPC envelopes, supports
    paginated tools/list responses, bounded payloads/timeouts, and unique
    request IDs safe for concurrent callers.
    """

    def __init__(self, config: McpClientConfig):
        self.config = config
        self.base_url = config.normalized_base_url()
        self._id_lock = threading.Lock()
        self._counter = 0

    def _next_id(self) -> str:
        with self._id_lock:
            self._counter += 1
            return f"uacos-{self._counter}-{uuid.uuid4().hex[:8]}"

    def _read_bounded(self, response) -> bytes:
        limit = self.config.max_response_bytes
        body = response.read(limit + 1)
        if len(body) > limit:
            raise McpClientError("mcp_response_too_large")
        return body

    def _request_json(self, url: str, *, payload: dict | None = None) -> dict:
        data = None
        headers = {"Accept": "application/json"}
        method = "GET"
        if payload is not None:
            data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            headers["Content-Type"] = "application/json"
            method = "POST"
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                raw = self._read_bounded(response)
        except urllib.error.HTTPError as exc:
            try:
                detail = exc.read(2048).decode("utf-8", errors="replace")
            except Exception:
                detail = ""
            raise McpClientError(f"mcp_http_error:{exc.code}:{detail[:512]}") from exc
        except urllib.error.URLError as exc:
            raise McpClientError(f"mcp_transport_error:{exc.reason}") from exc
        except TimeoutError as exc:
            raise McpClientError("mcp_timeout") from exc
        try:
            value = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise McpClientError("mcp_invalid_json_response") from exc
        if not isinstance(value, dict):
            raise McpClientError("mcp_response_must_be_object")
        return value

    def probe(self) -> dict:
        return self._request_json(self.base_url + "/health")

    def jsonrpc(self, method: str, params: dict | None = None) -> dict:
        request_id = self._next_id()
        envelope = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {},
        }
        response = self._request_json(self.base_url + "/jsonrpc", payload=envelope)
        if response.get("jsonrpc") != "2.0":
            raise McpClientError("mcp_invalid_jsonrpc_version")
        if response.get("id") != request_id:
            raise McpClientError("mcp_response_id_mismatch")
        if "error" in response:
            error = response.get("error") or {}
            raise McpClientError(f"mcp_remote_error:{error.get('code')}:{error.get('message')}")
        if "result" not in response:
            raise McpClientError("mcp_result_missing")
        result = response["result"]
        if not isinstance(result, dict):
            raise McpClientError("mcp_result_must_be_object")
        return result

    def list_tools(self) -> dict:
        tools: list[dict[str, Any]] = []
        cursor: str | None = None
        seen_cursors: set[str] = set()
        pages = 0
        while True:
            pages += 1
            if pages > self.config.max_pages:
                raise McpClientError("mcp_pagination_limit_exceeded")
            params = {"cursor": cursor} if cursor else {}
            result = self.jsonrpc("tools/list", params)
            page_tools = result.get("tools") or []
            if not isinstance(page_tools, list):
                raise McpClientError("mcp_tools_must_be_list")
            tools.extend(row for row in page_tools if isinstance(row, dict))
            next_cursor = result.get("nextCursor")
            if not next_cursor:
                break
            next_cursor = str(next_cursor)
            if next_cursor in seen_cursors:
                raise McpClientError("mcp_pagination_cursor_cycle")
            seen_cursors.add(next_cursor)
            cursor = next_cursor
        return {"status": "ok", "tools": tools, "pages": pages}

    def call_tool(self, name: str, arguments: dict | None = None) -> dict:
        if not str(name or "").strip():
            raise ValueError("tool_name_required")
        return self.jsonrpc("tools/call", {"name": name, "arguments": arguments or {}})
