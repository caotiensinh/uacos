from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import os
import subprocess
import threading
import http.server
import socketserver
import time
import os
import urllib.request
import urllib.error

from uacos.config import uacos_dir
from uacos.llm.providers import init_llm_config, load_llm_config, save_llm_config, set_provider_enabled
from uacos.llm.hardened import run_llm_hardened, provider_health_check
from uacos.runtime.agent_runtime import init_runtime, configure_runtime, create_job, run_job_once, runtime_status
from uacos.adapters.openclaw import init_openclaw_adapter, openclaw_health, set_openclaw_config
from uacos.compression.engine import compressed_context
from uacos.ops.packaging import bootstrap

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def validation_dir(repo_root: Path) -> Path:
    p = uacos_dir(repo_root) / "validation"
    p.mkdir(parents=True, exist_ok=True)
    return p

def latest_report_path(repo_root: Path) -> Path:
    return validation_dir(repo_root) / "phase30_realrun_report.json"

def write_report(repo_root: Path, report: dict) -> dict:
    path = latest_report_path(repo_root)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report["report_file"] = str(path)
    return report

def realrun_preflight(repo_root: Path) -> dict:
    bootstrap(repo_root)
    llm = init_llm_config(repo_root)
    runtime = init_runtime(repo_root)
    openclaw = init_openclaw_adapter(repo_root)
    cfg = load_llm_config(repo_root)
    checks = []
    checks.append({"name": "repo_exists", "status": "pass" if repo_root.exists() else "fail"})
    checks.append({"name": "llm_config", "status": "pass", "path": llm["config"]})
    checks.append({"name": "runtime_config", "status": "pass", "path": runtime["config"]})
    checks.append({"name": "openclaw_config", "status": "pass", "path": openclaw["config"]})
    checks.append({"name": "dry_run_provider", "status": "pass" if "dry_run" in cfg.get("providers", {}) else "fail"})
    try:
        ctx = compressed_context(repo_root, "preflight validation", max_tokens=2000, max_files=3)
        checks.append({"name": "compressed_context", "status": "pass", "tokens": ctx.get("compressed_tokens_est")})
    except Exception as exc:
        checks.append({"name": "compressed_context", "status": "fail", "error": str(exc)})
    status = "pass" if all(c["status"] == "pass" for c in checks) else "fail"
    return write_report(repo_root, {"status": status, "kind": "preflight", "created_at": utcnow(), "checks": checks})

class _MockOpenAIHandler(http.server.BaseHTTPRequestHandler):
    response_text = "diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@ -1,2 +1,2 @@\n def value():\n-    return 1\n+    return 42\n"

    def do_POST(self):
        if self.path.endswith("/chat/completions"):
            body = json.dumps({
                "id": "mock-uacos",
                "object": "chat.completion",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": self.response_text}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
            }).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return

class _ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def start_mock_openai_server(host: str = "127.0.0.1", port: int = 0):
    server = _ReusableTCPServer((host, port), _MockOpenAIHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server

def configure_mock_provider(repo_root: Path, base_url: str = "http://127.0.0.1:18765/v1") -> dict:
    init_llm_config(repo_root)
    cfg = load_llm_config(repo_root)
    cfg.setdefault("providers", {})["mock_openai"] = {
        "type": "openai_compatible",
        "base_url": base_url,
        "model": "mock-model",
        "api_key_env": "UACOS_MOCK_API_KEY",
        "enabled": True,
        "timeout_sec": 20
    }
    cfg["default_provider"] = "mock_openai"
    cfg.setdefault("safety", {})["dry_run_default"] = False
    save_llm_config(repo_root, cfg)
    return {"status": "ok", "provider": "mock_openai", "base_url": base_url}

def mock_provider_e2e(repo_root: Path, port: int = 0) -> dict:
    bootstrap(repo_root)
    if not (repo_root / "app.py").exists():
        (repo_root / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    server = start_mock_openai_server(port=port)
    actual_port = server.server_address[1]
    try:
        os.environ.setdefault("UACOS_MOCK_API_KEY", "mock-key")
        configure_mock_provider(repo_root, f"http://127.0.0.1:{actual_port}/v1")
        res = None
        ok = False
        for _ in range(3):
            res = run_llm_hardened(repo_root, "Return a unified diff to change app.value to 42", provider="mock_openai", task="fix app value", dry_run=False, retries=1)
            ok = res.get("status") == "ok" and "diff --git" in ((res.get("result") or {}).get("content") or "")
            if ok:
                break
            time.sleep(0.1)
        report = {
            "status": "pass" if ok else "fail",
            "kind": "mock_provider_e2e",
            "created_at": utcnow(),
            "port": actual_port,
            "provider_status": res.get("status"),
            "has_diff": "diff --git" in ((res.get("result") or {}).get("content") or ""),
            "result": res,
        }
        return write_report(repo_root, report)
    finally:
        server.shutdown()
        server.server_close()

def runtime_provider_mock_e2e(repo_root: Path, port: int = 0, auto_apply: bool = True) -> dict:
    bootstrap(repo_root)
    (repo_root / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    server = start_mock_openai_server(port=port)
    actual_port = server.server_address[1]
    try:
        os.environ.setdefault("UACOS_MOCK_API_KEY", "mock-key")
        configure_mock_provider(repo_root, f"http://127.0.0.1:{actual_port}/v1")
        init_runtime(repo_root)
        configure_runtime(
            repo_root,
            mode="real",
            default_backend="provider",
            provider="mock_openai",
            allowed_real_run=True,
            auto_apply_patch=auto_apply,
            max_context_tokens=4000,
            max_context_files=5,
        )
        job = create_job(
            repo_root,
            "Change app.value from 1 to 42",
            backend="provider",
            allowed_files=["app.py"],
            tests=["python -S -c \"from pathlib import Path; assert 'return 42' in Path('app.py').read_text()\""],
            auto_apply=auto_apply,
        )
        run = run_job_once(repo_root, job["id"], real=True)
        app_text = (repo_root / "app.py").read_text(encoding="utf-8")
        ok = run.get("status") in {"done", "committed"} and "return 42" in app_text
        report = {
            "status": "pass" if ok else "fail",
            "kind": "runtime_provider_mock_e2e",
            "created_at": utcnow(),
            "port": actual_port,
            "job_id": job["id"],
            "job_status": run.get("status"),
            "app_changed": "return 42" in app_text,
            "runtime_status": runtime_status(repo_root),
            "job": run,
        }
        return write_report(repo_root, report)
    finally:
        server.shutdown()
        server.server_close()

def ollama_realrun_check(repo_root: Path, model: str | None = None, prompt: str = "Reply OK", real: bool = False) -> dict:
    bootstrap(repo_root)
    init_llm_config(repo_root)
    cfg = load_llm_config(repo_root)
    if model:
        cfg.setdefault("providers", {}).setdefault("ollama", {"type": "ollama"})
        cfg["providers"]["ollama"].update({
            "type": "ollama",
            "base_url": cfg["providers"].get("ollama", {}).get("base_url", "http://127.0.0.1:11434"),
            "model": model,
            "enabled": True,
            "timeout_sec": 120,
        })
        cfg["default_provider"] = "ollama"
        cfg.setdefault("safety", {})["dry_run_default"] = not real
        save_llm_config(repo_root, cfg)
    if not real:
        res = provider_health_check(repo_root, provider="ollama", dry_run=True)
        status = "pass" if res.get("status") == "ok" else "fail"
        return write_report(repo_root, {"status": status, "kind": "ollama_dry_precheck", "created_at": utcnow(), "result": res})
    res = run_llm_hardened(repo_root, prompt, provider="ollama", task="ollama realrun check", dry_run=False, retries=1)
    status = "pass" if res.get("status") == "ok" and ((res.get("result") or {}).get("content") or "") else "fail"
    return write_report(repo_root, {"status": status, "kind": "ollama_realrun_check", "created_at": utcnow(), "result": res})

def openclaw_realrun_check(repo_root: Path, real: bool = False, agent: str = "leader") -> dict:
    bootstrap(repo_root)
    init_openclaw_adapter(repo_root)
    if not real:
        health = openclaw_health(repo_root, real=False)
        return write_report(repo_root, {"status": "pass" if health.get("status") == "ok" else "fail", "kind": "openclaw_dry_precheck", "created_at": utcnow(), "health": health})
    set_openclaw_config(repo_root, default_agent=agent, mode="real", allowed_real_run=True)
    health = openclaw_health(repo_root, real=True)
    return write_report(repo_root, {"status": "pass" if health.get("status") == "ok" else "fail", "kind": "openclaw_realrun_check", "created_at": utcnow(), "health": health})

def phase30_full_validation(repo_root: Path, include_mock_runtime: bool = True) -> dict:
    results = []
    results.append(realrun_preflight(repo_root))
    results.append(mock_provider_e2e(repo_root))
    if include_mock_runtime:
        results.append(runtime_provider_mock_e2e(repo_root))
    status = "pass" if all(r.get("status") == "pass" for r in results) else "fail"
    report = {"status": status, "kind": "phase30_full_validation", "created_at": utcnow(), "results": results}
    return write_report(repo_root, report)
