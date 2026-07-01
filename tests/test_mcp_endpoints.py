from pathlib import Path
import json
import urllib.request

from uacos.mcp.server import start_test_server


def _get(base, path):
    req = urllib.request.Request(base + path, method="GET")
    return urllib.request.urlopen(req, timeout=10)


def _json(base, path):
    with _get(base, path) as resp:
        assert resp.status == 200
        return resp.headers, json.loads(resp.read().decode("utf-8"))


def _parse_sse(text):
    events = {}
    for block in text.strip().split("\n\n"):
        event = None
        data = None
        for line in block.splitlines():
            if line.startswith("event: "):
                event = line.split(": ", 1)[1]
            elif line.startswith("data: "):
                data = json.loads(line.split(": ", 1)[1])
        if event:
            events[event] = data
    return events


def test_mcp_get_endpoints(tmp_path):
    repo = Path(tmp_path)
    server = start_test_server(repo, port=0)
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        _, root = _json(base, "/")
        assert root["status"] == "ok"

        _, health = _json(base, "/health")
        assert health["status"] == "ok"

        _, tools = _json(base, "/tools")
        assert tools["status"] == "ok"
        assert isinstance(tools["tools"], list)
        assert tools["tools"]

        with _get(base, "/sse") as resp:
            assert resp.status == 200
            assert "text/event-stream" in resp.headers.get("Content-Type", "")
            body = resp.read().decode("utf-8")

        assert "\\n" not in body
        events = _parse_sse(body)
        assert events["ready"]["status"] == "ok"
        assert isinstance(events["tools"]["tools"], list)
        assert events["tools"]["tools"]
    finally:
        server.shutdown()
        server.server_close()
