from __future__ import annotations

from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import json
import html
import traceback

from uacos.storage import init_storage
from uacos.scanner.file_scanner import scan_repo
from uacos.search import search_repo, stats
from uacos.retrieval.context_pack import build_context_pack
from uacos.memory.store import read_memories, search_memories
from uacos.memory.regression import regression_check_patch
from uacos.execution.token_ledger import ledger_summary
from uacos.execution.failed_memory import read_failures
from uacos.apply.patch_apply import list_manifests
from uacos.dashboard.ops_summary import ops_summary

LABELS = {
    "en": {
        "title": "UACOS Operations Dashboard",
        "scan": "Scan Repo",
        "stats": "Repository Stats",
        "search": "Search",
        "context": "Context Pack",
        "memory": "Memory",
        "ledger": "Token Ledger",
        "failures": "Failures",
        "manifests": "Change Manifests",
    },
    "vi": {
        "title": "Bảng điều khiển vận hành UACOS",
        "scan": "Quét Repo",
        "stats": "Thống kê Repo",
        "search": "Tìm kiếm",
        "context": "Context Pack",
        "memory": "Bộ nhớ",
        "ledger": "Token Ledger",
        "failures": "Lỗi/Fail",
        "manifests": "Manifest thay đổi",
    },
    "ja": {
        "title": "UACOS 運用ダッシュボード",
        "scan": "リポジトリスキャン",
        "stats": "リポジトリ統計",
        "search": "検索",
        "context": "コンテキストパック",
        "memory": "メモリ",
        "ledger": "トークン台帳",
        "failures": "失敗履歴",
        "manifests": "変更マニフェスト",
    },
}

STYLE = """
body{font-family:Inter,Arial,sans-serif;background:#0b1020;color:#e5e7eb;margin:0}
header{padding:22px 28px;background:#111827;border-bottom:1px solid #263244;display:flex;justify-content:space-between;align-items:center}
h1{font-size:22px;margin:0}
main{padding:24px;display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(340px,1fr))}
.card{background:#111827;border:1px solid #273449;border-radius:14px;padding:18px;box-shadow:0 10px 24px rgba(0,0,0,.22)}
.card h2{font-size:16px;margin-top:0;color:#93c5fd}
pre{white-space:pre-wrap;word-break:break-word;background:#020617;border:1px solid #1f2937;border-radius:10px;padding:12px;max-height:360px;overflow:auto}
input,select,button,textarea{background:#020617;color:#e5e7eb;border:1px solid #374151;border-radius:8px;padding:9px;margin:4px 0}
button{cursor:pointer;background:#1d4ed8;border-color:#2563eb}
button:hover{background:#2563eb}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.small{font-size:12px;color:#9ca3af}
a{color:#93c5fd}
.full{grid-column:1/-1}
"""

def json_response(handler, data, status=200):
    raw = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)

def html_response(handler, data, status=200):
    raw = data.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)

def dashboard_html(repo_root: Path, lang: str = "en") -> str:
    labels = LABELS.get(lang, LABELS["en"])
    summary = ops_summary(repo_root)
    safe_summary = html.escape(json.dumps(summary, ensure_ascii=False, indent=2))
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{labels['title']}</title>
<style>{STYLE}</style>
</head>
<body>
<header>
  <div>
    <h1>{labels['title']}</h1>
    <div class="small">{html.escape(str(repo_root))}</div>
  </div>
  <div class="row">
    <a href="/?lang=en">EN</a>
    <a href="/?lang=vi">VI</a>
    <a href="/?lang=ja">JA</a>
  </div>
</header>
<main>
  <section class="card">
    <h2>{labels['scan']}</h2>
    <button onclick="api('/api/scan','scanOut')">Run Scan</button>
    <pre id="scanOut">Ready.</pre>
  </section>

  <section class="card">
    <h2>{labels['stats']}</h2>
    <button onclick="api('/api/stats','statsOut')">Refresh</button>
    <pre id="statsOut">{safe_summary}</pre>
  </section>

  <section class="card">
    <h2>{labels['search']}</h2>
    <input id="q" placeholder="barrier open" style="width:70%"/>
    <button onclick="api('/api/search?q='+encodeURIComponent(document.getElementById('q').value),'searchOut')">Search</button>
    <pre id="searchOut"></pre>
  </section>

  <section class="card">
    <h2>{labels['context']}</h2>
    <textarea id="task" placeholder="Fix barrier open safely" style="width:95%;height:72px"></textarea>
    <button onclick="api('/api/context?task='+encodeURIComponent(document.getElementById('task').value),'contextOut')">Build Context</button>
    <pre id="contextOut"></pre>
  </section>

  <section class="card">
    <h2>{labels['memory']}</h2>
    <input id="mq" placeholder="memory search" style="width:70%"/>
    <button onclick="api('/api/memory?q='+encodeURIComponent(document.getElementById('mq').value),'memoryOut')">Memory</button>
    <pre id="memoryOut"></pre>
  </section>

  <section class="card">
    <h2>{labels['ledger']}</h2>
    <button onclick="api('/api/token-ledger','ledgerOut')">Refresh</button>
    <pre id="ledgerOut"></pre>
  </section>

  <section class="card">
    <h2>{labels['failures']}</h2>
    <button onclick="api('/api/failures','failOut')">Refresh</button>
    <pre id="failOut"></pre>
  </section>

  <section class="card">
    <h2>{labels['manifests']}</h2>
    <button onclick="api('/api/manifests','manifestOut')">Refresh</button>
    <pre id="manifestOut"></pre>
  </section>

  <section class="card full">
    <h2>API</h2>
    <pre>/api/summary
/api/stats
/api/scan
/api/search?q=...
/api/context?task=...
/api/memory?q=...
/api/token-ledger
/api/failures
/api/manifests</pre>
  </section>
</main>
<script>
async function api(url,id){{
  const el=document.getElementById(id);
  el.textContent='Loading...';
  try{{
    const r=await fetch(url);
    const t=await r.text();
    try{{ el.textContent=JSON.stringify(JSON.parse(t),null,2); }}
    catch(e){{ el.textContent=t; }}
  }}catch(e){{el.textContent='ERROR: '+e;}}
}}
</script>
</body>
</html>"""

class DashboardHandler(BaseHTTPRequestHandler):
    repo_root: Path = Path(".").resolve()

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        try:
            if parsed.path == "/":
                lang = qs.get("lang", ["en"])[0]
                return html_response(self, dashboard_html(self.repo_root, lang))
            if parsed.path == "/api/summary":
                return json_response(self, ops_summary(self.repo_root))
            if parsed.path == "/api/stats":
                return json_response(self, stats(self.repo_root))
            if parsed.path == "/api/scan":
                init_storage(self.repo_root)
                return json_response(self, scan_repo(self.repo_root))
            if parsed.path == "/api/search":
                q = qs.get("q", [""])[0]
                return json_response(self, {"query": q, "results": search_repo(self.repo_root, q, limit=20)})
            if parsed.path == "/api/context":
                task = qs.get("task", [""])[0]
                if not task:
                    return json_response(self, {"error": "task required"}, status=400)
                pack = build_context_pack(self.repo_root, task, max_tokens=3500, search_limit=8)
                return json_response(self, {"id": pack["id"], "token_count": pack["token_count"], "content": pack["content"]})
            if parsed.path == "/api/memory":
                q = qs.get("q", [""])[0]
                if q:
                    data = search_memories(self.repo_root, q, include_invalid=False, limit=50)
                else:
                    data = read_memories(self.repo_root, include_invalid=False)
                return json_response(self, {"query": q, "memories": data})
            if parsed.path == "/api/token-ledger":
                return json_response(self, ledger_summary(self.repo_root))
            if parsed.path == "/api/failures":
                return json_response(self, {"failures": read_failures(self.repo_root)})
            if parsed.path == "/api/manifests":
                return json_response(self, list_manifests(self.repo_root))
            return json_response(self, {"error": "not found"}, status=404)
        except Exception as exc:
            return json_response(self, {"error": f"{type(exc).__name__}:{exc}", "traceback": traceback.format_exc()}, status=500)

    def log_message(self, fmt, *args):
        # quiet but still useful for local dev if needed
        return

def run_dashboard(repo_root: Path, host: str = "127.0.0.1", port: int = 8765):
    init_storage(repo_root)
    handler_cls = type("UACOSDashboardHandler", (DashboardHandler,), {"repo_root": repo_root})
    server = ThreadingHTTPServer((host, port), handler_cls)
    print(f"UACOS dashboard running at http://{host}:{port}/")
    print(f"Repo: {repo_root}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping dashboard.")
    finally:
        server.server_close()
