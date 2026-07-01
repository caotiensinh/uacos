# MCP Setup

Start the local MCP server from the repo root:

```bash
uacos mcp-serve --repo . --host 127.0.0.1 --port 8769
```

Supported HTTP endpoints:

- `/`
- `/health`
- `/tools`
- `/sse`
- `/call`
- `/jsonrpc`

The `/sse` endpoint returns `Content-Type: text/event-stream` and emits `ready` and `tools` events.
