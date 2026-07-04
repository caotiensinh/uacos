from pathlib import Path
from uacos.ops.packaging import bootstrap
from uacos.ast_engine.js_parser import parse_repo_js_ts
from uacos.fullstack.impact import build_fullstack_index, fullstack_impact, fullstack_context
from uacos.compression.engine import build_summary_cache, load_compression_cache

def make_repo(repo: Path):
    repo.mkdir()
    (repo / "backend").mkdir()
    (repo / "frontend").mkdir()
    (repo / "backend" / "api.py").write_text(
        "from fastapi import FastAPI\n"
        "app = FastAPI()\n\n"
        "@app.get('/api/users')\n"
        "def list_users():\n"
        "    return []\n\n"
        "@app.post('/api/users')\n"
        "def create_user(user: dict):\n"
        "    return user\n",
        encoding="utf-8",
    )
    (repo / "frontend" / "dashboard.js").write_text(
        "import { render } from './ui.js';\n\n"
        "export async function loadUsers() {\n"
        "  const res = await fetch('/api/users');\n"
        "  return await res.json();\n"
        "}\n\n"
        "const createUser = async (user) => {\n"
        "  return axios.post('/api/users', user);\n"
        "};\n",
        encoding="utf-8",
    )
    (repo / "frontend" / "ui.ts").write_text(
        "export class DashboardView {\n"
        "  renderUsers(users: any[]) { return users.length; }\n"
        "}\n"
        "export function render() { return true; }\n",
        encoding="utf-8",
    )

def test_js_ts_parser_and_fullstack_links(tmp_path: Path):
    repo = tmp_path / "repo"
    make_repo(repo)
    bootstrap(repo)
    docs = parse_repo_js_ts(repo)
    assert len(docs) == 2
    dash = [d for d in docs if d["path"].endswith("dashboard.js")][0]
    assert any(c["endpoint"] == "/api/users" for c in dash["api_calls"])
    idx = build_fullstack_index(repo)
    assert idx["stats"]["python_routes"] >= 2
    assert idx["stats"]["frontend_api_calls"] >= 2
    assert idx["stats"]["backend_frontend_links"] >= 1
    impact = fullstack_impact(repo, "fix /api/users dashboard loadUsers bug")
    files = [x["file"] for x in impact["impacted_files"]]
    assert "backend/api.py" in files
    assert "frontend/dashboard.js" in files
    ctx = fullstack_context(repo, "fix /api/users dashboard loadUsers bug", max_tokens=8000)
    assert ctx["status"] == "ok"
    assert "backend/api.py" in ctx["content"]
    assert "frontend/dashboard.js" in ctx["content"]

def test_fullstack_impact_reasons_are_specific_not_generic(tmp_path: Path):
    # Regression test: every JS/TS match used to be labeled with the same
    # generic "js_keyword_api" reason regardless of whether it matched on
    # file path, function name, or API endpoint — e.g. a pure function-name
    # match was mislabeled "js_keyword_api" even though the task text never
    # mentioned an API at all. Reasons must now say specifically what matched.
    repo = tmp_path / "repo"
    make_repo(repo)
    bootstrap(repo)
    impact = fullstack_impact(repo, "fix loadUsers bug")
    dash = next(x for x in impact["impacted_files"] if x["file"] == "frontend/dashboard.js")
    assert not any(r == "js_keyword_api" for r in dash["reasons"])
    assert any(r.startswith("js_function_name:") for r in dash["reasons"])


def test_compression_summarizes_js_ts(tmp_path: Path):
    repo = tmp_path / "repo"
    make_repo(repo)
    bootstrap(repo)
    cache = build_summary_cache(repo)
    assert cache["file_count"] >= 3
    data = load_compression_cache(repo)
    dash = data["files"]["frontend/dashboard.js"]
    assert dash["kind"] == "js_ts"
    assert "API calls" in dash["summary"]
