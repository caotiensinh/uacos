from pathlib import Path

from uacos.mcp.server import http_call, jsonrpc_call, start_test_server


def test_mock_external_agent_can_get_context_validate_patch_and_decide_loop(tmp_path):
    repo = tmp_path
    (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")

    server = start_test_server(repo, port=0)
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        tools = http_call(base, "list_tools")
        tool_names = {tool["name"] for tool in tools["result"]["tools"]}

        assert {"get_context", "ingest_patch", "plan_orchestration_loop", "loop_decision"}.issubset(tool_names)

        context = http_call(base, "get_context", {"task": "change app value safely", "max_tokens": 3000, "max_files": 4})
        assert context["result"]["status"] == "ok"
        assert context["result"]["selected_file_count"] >= 1

        plan = jsonrpc_call(base, "plan_orchestration_loop", {
            "spec": "change app value safely and run tests",
            "agents": ["mock-external-agent"],
            "tests": ["python -m pytest -q"],
            "max_iterations": 2,
        })
        assert plan["result"]["status"] == "ok"
        assert plan["result"]["max_iterations"] == 2
        assert plan["result"]["role"] == "orchestrate_agents_and_code_do_not_act_as_general_agent"

        diff = "diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@ -1,2 +1,2 @@\n def value():\n-    return 1\n+    return 42\n"
        validation = http_call(base, "ingest_patch", {"diff": diff, "allowed_files": ["app.py"], "apply": False})
        assert validation["result"]["status"] == "validated"
        assert (repo / "app.py").read_text(encoding="utf-8") == "def value():\n    return 1\n"

        decision = jsonrpc_call(base, "loop_decision", {
            "iteration": 1,
            "max_iterations": 2,
            "spec_satisfied": False,
            "tests_passed": False,
        })
        assert decision["result"]["status"] == "continue"

        unsafe = jsonrpc_call(base, "loop_decision", {
            "iteration": 1,
            "max_iterations": 2,
            "spec_satisfied": False,
            "tests_passed": False,
            "unsafe_blocked": True,
        })
        assert unsafe["result"]["status"] == "stop"
        assert unsafe["result"]["reason"] == "unsafe_patch_blocked"
    finally:
        server.shutdown()
        server.server_close()
