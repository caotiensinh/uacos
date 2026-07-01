from pathlib import Path
from uacos.mcp.server import mcp_self_test, call_tool, tool_specs

def test_mcp_self_test_and_tools(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    report = mcp_self_test(repo)
    assert report["status"] == "pass", report
    assert "return 42" in (repo / "app.py").read_text(encoding="utf-8")
    assert len(tool_specs()) >= 6

def test_mcp_direct_tool_calls(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    tools = call_tool(repo, "list_tools", {})
    assert tools["status"] == "ok"
    ctx = call_tool(repo, "get_context", {"task": "fix app value", "max_tokens": 3000})
    assert ctx["status"] == "ok"
    assert "content" in ctx
    diff = "diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@ -1,2 +1,2 @@\n def value():\n-    return 1\n+    return 42\n"
    val = call_tool(repo, "ingest_patch", {"diff": diff, "allowed_files": ["app.py"], "apply": False})
    assert val["status"] == "validated"
