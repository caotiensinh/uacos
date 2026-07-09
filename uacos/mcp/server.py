from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import uuid
import tempfile
import http.server
import socketserver
import threading
import urllib.request
import urllib.error

from uacos.config import uacos_dir
from uacos.compression.engine import compressed_context
from uacos.memory.store import search_memories
from uacos.patching.engine import validate_patch
from uacos.transaction.engine import run_transaction
from uacos.runtime.agent_runtime import init_runtime, create_job, run_job_once, runtime_status, list_jobs
from uacos.ops.packaging import bootstrap, health_check
from uacos.product.workflows import get_product_contract
from uacos.orchestrator.contract import build_orchestration_plan, get_orchestration_contract, next_loop_decision


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def mcp_dir(repo_root: Path) -> Path:
    p = uacos_dir(repo_root) / "mcp"
    p.mkdir(parents=True, exist_ok=True)
    return p


def latest_config_path(repo_root: Path) -> Path:
    return mcp_dir(repo_root) / "mcp_server_config.json"


def latest_report_path(repo_root: Path) -> Path:
    return mcp_dir(repo_root) / "latest_mcp_report.json"


def tool_specs() -> list[dict]:
    return [
        {
            "name": "get_context",
            "description": "Build compressed UACOS context for a task.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "task": {"type": "string"},
                    "max_tokens": {"type": "integer", "default": 6000},
                    "max_files": {"type": "integer", "default": 8}
                },
                "required": ["task"]
            }
        },
        {
            "name": "get_memory",
            "description": "Search UACOS memory for a query.",
            "input_schema": {
                "type": "object",
                "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 5}},
                "required": ["query"]
            }
        },
        {
            "name": "ingest_patch",
            "description": "Validate and optionally apply a unified diff using transaction safety.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "diff": {"type": "string"},
                    "allowed_files": {"type": "array", "items": {"type": "string"}},
                    "allowed_dirs": {"type": "array", "items": {"type": "string"}},
                    "tests": {"type": "array", "items": {"type": "string"}},
                    "apply": {"type": "boolean", "default": False},
                    "title": {"type": "string", "default": "MCP patch"}
                },
                "required": ["diff"]
            }
        },
        {
            "name": "create_job",
            "description": "Create a UACOS runtime job.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "task": {"type": "string"},
                    "backend": {"type": "string", "default": "manual"},
                    "allowed_files": {"type": "array", "items": {"type": "string"}},
                    "tests": {"type": "array", "items": {"type": "string"}},
                    "auto_apply": {"type": "boolean", "default": False}
                },
                "required": ["task"]
            }
        },
        {
            "name": "run_job",
            "description": "Run one queued UACOS job or a specific job ID.",
            "input_schema": {
                "type": "object",
                "properties": {"job_id": {"type": "string"}, "real": {"type": "boolean", "default": False}}
            }
        },
        {
            "name": "product_contract",
            "description": "Return UACOS product positioning, simplified workflows, MCP contract, and finite upgrade plan.",
            "input_schema": {
                "type": "object",
                "properties": {"section": {"type": "string"}}
            }
        },
        {
            "name": "orchestration_contract",
            "description": "Return UACOS core pillars, bounded DevOps loop steps, safety invariants, and stop conditions.",
            "input_schema": {
                "type": "object",
                "properties": {"section": {"type": "string"}}
            }
        },
        {
            "name": "plan_orchestration_loop",
            "description": "Create a finite spec-driven plan for code -> test -> record -> improve loops. This does not execute agents or apply patches.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "spec": {"type": "string"},
                    "agents": {"type": "array", "items": {"type": "string"}},
                    "tests": {"type": "array", "items": {"type": "string"}},
                    "max_iterations": {"type": "integer", "default": 3}
                },
                "required": ["spec"]
            }
        },
        {
            "name": "loop_decision",
            "description": "Return the next safe loop decision from iteration/test/spec state without executing anything.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "iteration": {"type": "integer"},
                    "max_iterations": {"type": "integer"},
                    "spec_satisfied": {"type": "boolean"},
                    "tests_passed": {"type": "boolean"},
                    "unsafe_blocked": {"type": "boolean", "default": False}
                },
                "required": ["iteration", "max_iterations", "spec_satisfied", "tests_passed"]
            }
        },
        {
            "name": "status",
            "description": "Return UACOS repo/runtime status.",
            "input_schema": {"type": "object", "properties": {}}
        },
        {
            "name": "list_tools",
            "description": "List available MCP tools.",
            "input_schema": {"type": "object", "properties": {}}
        }
    ]


def call_tool(repo_root: Path, name: str, args: dict | None = None) -> dict:
    args = args or {}
    bootstrap(repo_root)
    if name == "list_tools":
        return {"status": "ok", "tools": tool_specs()}
    if name == "product_contract":
        return get_product_contract(args.get("section"))
    if name == "orchestration_contract":
        return get_orchestration_contract(args.get("section"))
    if name == "plan_orchestration_loop":
        return build_orchestration_plan(
            args.get("spec", ""),
            agents=args.get("agents") or [],
            tests=args.get("tests") or [],
            max_iterations=args.get("max_iterations"),
        )
    if name == "loop_decision":
        return next_loop_decision(
            iteration=int(args.get("iteration", 0)),
            max_iterations=int(args.get("max_iterations", 3)),
            spec_satisfied=bool(args.get("spec_satisfied", False)),
            tests_passed=bool(args.get("tests_passed", False)),
            unsafe_blocked=bool(args.get("unsafe_blocked", False)),
        )
    if name == "get_context":
        task = args["task"]
        result = compressed_context(repo_root, task, max_tokens=int(args.get("max_tokens", 6000)), max_files=int(args.get("max_files", 8)))
        return {k: v for k, v in result.items() if k != "content"} | {"content": result["content"]}
    if name == "get_memory":
        rows = search_memories(repo_root, args["query"], limit=int(args.get("limit", 5)))
        return {"status": "ok", "query": args["query"], "memories": rows}
    if name == "ingest_patch":
        diff = args["diff"]
        patch_file = mcp_dir(repo_root) / f"mcp_patch_{uuid.uuid4().hex[:8]}.diff"
        patch_file.write_text(diff, encoding="utf-8")
        allowed_files = args.get("allowed_files") or []
        allowed_dirs = args.get("allowed_dirs") or []
        tests = args.get("tests") or []
        validation = validate_patch(repo_root, diff, allowed_files=allowed_files, allowed_dirs=allowed_dirs)
        if not args.get("apply", False):
            return {"status": "validated", "validation": validation, "patch_file": str(patch_file)}
        tx = run_transaction(repo_root, patch_file, title=args.get("title", "MCP patch"), objective="MCP ingest_patch", allowed_files=allowed_files, allowed_dirs=allowed_dirs, tests=tests)
        return {"status": "applied" if tx.get("status") == "committed" else tx.get("status"), "transaction": tx}
    if name == "create_job":
        init_runtime(repo_root)
        job = create_job(repo_root, args["task"], backend=args.get("backend"), allowed_files=args.get("allowed_files") or [], allowed_dirs=args.get("allowed_dirs") or [], tests=args.get("tests") or [], auto_apply=args.get("auto_apply", False))
        return {"status": "ok", "job": job}
    if name == "run_job":
        init_runtime(repo_root)
        job = run_job_once(repo_root, job_id=args.get("job_id"), real=bool(args.get("real", False)))
        return {"status": job.get("status", "ok"), "job": job}
    if name == "status":
        init_runtime(repo_root)
        return {"status": "ok", "health": health_check(repo_root), "runtime": runtime_status(repo_root), "jobs": list_jobs(repo_root)}
    raise ValueError(f"unknown_tool:{name}")


def _json_response(handler, code: int, data: dict):
    body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class UacosMcpHandler(http.server.BaseHTTPRequestHandler):
    repo_root: Path = Path(".").resolve()

    def _send_sse(self, events):
        chunks = []
        for name, payload in events:
            chunks.append(f"event: {name}\n")
            chunks.append("data: " + json.dumps(payload, ensure_ascii=False) + "\n\n")
        body = "".join(chunks).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]

        if path in {"/", "/health"}:
            _json_response(self, 200, {
                "status": "ok",
                "server": "uacos-mcp",
                "repo": str(self.repo_root),
                "created_at": utcnow(),
                "endpoints": ["/", "/health", "/tools", "/sse", "/call", "/jsonrpc"],
            })
            return

        if path == "/tools":
            _json_response(self, 200, {
                "status": "ok",
                "tools": tool_specs(),
            })
            return

        if path == "/sse":
            try:
                tools = tool_specs()
            except Exception:
                tools = []
            self._send_sse([
                ("ready", {
                    "status": "ok",
                    "server": "uacos-mcp",
                    "created_at": utcnow(),
                    "repo": str(self.repo_root),
                }),
                ("tools", {"tools": tools}),
            ])
            return

        _json_response(self, 404, {
            "status": "error",
            "error": "not_found",
            "path": path,
        })

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8")
            payload = json.loads(raw or "{}")
            if self.path == "/call":
                name = payload.get("tool") or payload.get("name")
                args = payload.get("arguments") or payload.get("args") or {}
                result = call_tool(self.repo_root, name, args)
                _json_response(self, 200, {"jsonrpc": "2.0", "id": payload.get("id"), "result": result})
            elif self.path == "/jsonrpc":
                method = payload.get("method")
                params = payload.get("params") or {}
                if method == "tools/list":
                    result = {"tools": tool_specs()}
                elif method == "tools/call":
                    result = call_tool(self.repo_root, params.get("name"), params.get("arguments") or {})
                else:
                    _json_response(self, 400, {"jsonrpc": "2.0", "id": payload.get("id"), "error": {"code": -32601, "message": "method not found"}})
                    return
                _json_response(self, 200, {"jsonrpc": "2.0", "id": payload.get("id"), "result": result})
            else:
                _json_response(self, 404, {"status": "error", "error": "not_found"})
        except Exception as exc:
            _json_response(self, 500, {"jsonrpc": "2.0", "error": {"code": -32000, "message": str(exc), "type": type(exc).__name__}})

    def log_message(self, fmt, *args):
        return


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def serve_mcp(repo_root: Path, host: str = "127.0.0.1", port: int = 8769):
    if host not in {"127.0.0.1", "localhost"}:
        raise ValueError("MCP server is localhost-only by default for safety.")
    handler = type("RepoMcpHandler", (UacosMcpHandler,), {"repo_root": repo_root})
    with ReusableTCPServer((host, port), handler) as httpd:
        config = {"status": "running", "host": host, "port": httpd.server_address[1], "repo": str(repo_root), "tools": [t["name"] for t in tool_specs()], "created_at": utcnow()}
        latest_config_path(repo_root).write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(config, ensure_ascii=False, indent=2))
        httpd.serve_forever()


def start_test_server(repo_root: Path, host: str = "127.0.0.1", port: int = 0):
    handler = type("RepoMcpHandler", (UacosMcpHandler,), {"repo_root": repo_root})
    server = ReusableTCPServer((host, port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def http_call(base_url: str, tool: str, args: dict | None = None) -> dict:
    data = json.dumps({"tool": tool, "arguments": args or {}, "id": "test"}).encode("utf-8")
    req = urllib.request.Request(base_url.rstrip("/") + "/call", data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def jsonrpc_call(base_url: str, name: str, args: dict | None = None) -> dict:
    data = json.dumps({"jsonrpc": "2.0", "id": "1", "method": "tools/call", "params": {"name": name, "arguments": args or {}}}).encode("utf-8")
    req = urllib.request.Request(base_url.rstrip("/") + "/jsonrpc", data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def mcp_self_test(repo_root: Path) -> dict:
    bootstrap(repo_root)
    if not (repo_root / "app.py").exists():
        (repo_root / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    server = start_test_server(repo_root, port=0)
    port = server.server_address[1]
    base = f"http://127.0.0.1:{port}"
    try:
        tools = http_call(base, "list_tools")
        contract = http_call(base, "product_contract")
        orchestration = http_call(base, "orchestration_contract")
        loop_plan = jsonrpc_call(base, "plan_orchestration_loop", {"spec": "return 42 after patch", "tests": ["pytest -q"], "agents": ["manual"], "max_iterations": 2})
        decision = jsonrpc_call(base, "loop_decision", {"iteration": 1, "max_iterations": 2, "spec_satisfied": False, "tests_passed": False})
        ctx = http_call(base, "get_context", {"task": "fix app value", "max_tokens": 3000, "max_files": 4})
        diff = "diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@ -1,2 +1,2 @@\n def value():\n-    return 1\n+    return 42\n"
        val = http_call(base, "ingest_patch", {"diff": diff, "allowed_files": ["app.py"], "apply": False})
        apply = jsonrpc_call(base, "ingest_patch", {"diff": diff, "allowed_files": ["app.py"], "tests": ["python -S -c \"from pathlib import Path; assert 'return 42' in Path('app.py').read_text()\""], "apply": True})
        status = http_call(base, "status")
        ok = (
            tools.get("result", {}).get("status") == "ok"
            and contract.get("result", {}).get("status") == "ok"
            and orchestration.get("result", {}).get("status") == "ok"
            and loop_plan.get("result", {}).get("status") == "ok"
            and decision.get("result", {}).get("status") == "continue"
            and any(t.get("name") == "product_contract" for t in tools.get("result", {}).get("tools", []))
            and any(t.get("name") == "orchestration_contract" for t in tools.get("result", {}).get("tools", []))
            and any(t.get("name") == "plan_orchestration_loop" for t in tools.get("result", {}).get("tools", []))
            and ctx.get("result", {}).get("status") == "ok"
            and val.get("result", {}).get("status") == "validated"
            and apply.get("result", {}).get("status") == "applied"
            and "return 42" in (repo_root / "app.py").read_text(encoding="utf-8")
        )
        report = {"status": "pass" if ok else "fail", "port": port, "tools_count": len(tools.get("result", {}).get("tools", [])), "product_contract_status": contract.get("result", {}).get("status"), "orchestration_contract_status": orchestration.get("result", {}).get("status"), "loop_plan_status": loop_plan.get("result", {}).get("status"), "loop_decision_status": decision.get("result", {}).get("status"), "context_status": ctx.get("result", {}).get("status"), "validate_status": val.get("result", {}).get("status"), "apply_status": apply.get("result", {}).get("status"), "runtime_status": status.get("result", {}).get("runtime", {})}
        latest_report_path(repo_root).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return report
    finally:
        server.shutdown()
        server.server_close()
