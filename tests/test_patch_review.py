from pathlib import Path

from uacos.flow_cli import run_guard
from uacos.security.patch_review import classify_file_patch, review_patch_text


def test_patch_review_flags_auth_and_network_risk():
    patch = "diff --git a/auth.py b/auth.py\n--- a/auth.py\n+++ b/auth.py\n@@ -1,2 +1,4 @@\n def login():\n-    return True\n+    import requests\n+    requests.post('https://example.com/audit')\n+    return True\n"

    review = review_patch_text(patch, allowed_files=["auth.py"], tests=["pytest -q"])

    assert review["status"] == "pass"
    assert review["risk_level"] == "high"
    assert "auth_change" in review["risk_categories"]
    assert "network_call" in review["risk_categories"]
    assert "human_review_required" in review["required_next_steps"]
    assert review["writes_code"] is False


def test_patch_review_blocks_scope_violations():
    patch = "diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@ -1,2 +1,2 @@\n def value():\n-    return 1\n+    return 2\n"

    review = review_patch_text(patch, allowed_files=["other.py"])

    assert review["status"] == "fail"
    assert review["risk_level"] == "block"
    assert "fix_patch_gate_failures_before_apply" in review["required_next_steps"]


def test_patch_review_flags_dependency_and_ci_changes():
    dep = classify_file_patch("pyproject.toml", ["requests = '*'"], [])
    ci = classify_file_patch(".github/workflows/ci.yml", ["run: echo unsafe"], [])

    assert "dependency_change" in dep["categories"]
    assert "ci_release_change" in ci["categories"]


def test_uacos_flow_guard_includes_risk_review(tmp_path):
    patch_file = tmp_path / "change.diff"
    patch_file.write_text(
        "diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@ -1,2 +1,2 @@\n def value():\n-    return 1\n+    return 2\n",
        encoding="utf-8",
    )

    result = run_guard(tmp_path, str(patch_file), allowed_files=["app.py"], tests=["python -m pytest -q"])

    assert result["status"] == "pass"
    assert result["risk_review"]["risk_level"] == "low"
    assert result["writes_code"] is False
    assert "risk review" in result["next_step"]
