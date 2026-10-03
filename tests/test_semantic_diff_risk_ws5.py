from pathlib import Path

from uacos.graph.builder import build_graph
from uacos.security.diff_parser import parse_unified_diff
from uacos.security.patch_review import review_patch_text
from uacos.security.semantic_diff_risk import assess_semantic_diff_risk


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_diff_parser_tracks_old_and_new_changed_lines():
    patch = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -10,4 +10,4 @@
 keep
-old
+new
 keep2
 keep3
"""
    parsed = parse_unified_diff(patch)
    assert len(parsed) == 1
    assert parsed[0].old_changed_lines == [11]
    assert parsed[0].new_changed_lines == [11]


def test_semantic_risk_maps_changed_hunk_to_existing_symbol(tmp_path: Path):
    _write(
        tmp_path,
        "app.py",
        "def safe():\n    return 1\n\n"
        "def login_user(token):\n    if not token:\n        raise ValueError('missing')\n    return True\n",
    )
    build_graph(tmp_path)
    patch = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -4,4 +4,4 @@
 def login_user(token):
-    if not token:
+    if token is None:
         raise ValueError('missing')
     return True
"""
    result = assess_semantic_diff_risk(tmp_path, patch)
    assert any(row["symbol_id"].endswith(":login_user") for row in result["affected_symbols"])
    assert "security_sensitive_symbol" in result["categories"]
    assert result["risk_level"] in {"medium", "high", "critical"}


def test_semantic_risk_flags_critical_path_and_structural_addition(tmp_path: Path):
    _write(tmp_path, ".github/workflows/ci.py", "def run():\n    return 1\n")
    build_graph(tmp_path)
    patch = """diff --git a/.github/workflows/ci.py b/.github/workflows/ci.py
--- a/.github/workflows/ci.py
+++ b/.github/workflows/ci.py
@@ -1,2 +1,5 @@
 def run():
     return 1
+
+def deploy():
+    return 2
"""
    result = assess_semantic_diff_risk(tmp_path, patch)
    assert "critical_path" in result["categories"]
    assert "structural_addition" in result["categories"]
    assert result["risk_level"] in {"high", "critical"}
    assert result["requires_human_review"] is True


def test_patch_review_includes_semantic_evidence_when_repo_root_supplied(tmp_path: Path):
    _write(tmp_path, "auth.py", "def login(token):\n    return bool(token)\n")
    build_graph(tmp_path)
    patch = """diff --git a/auth.py b/auth.py
--- a/auth.py
+++ b/auth.py
@@ -1,2 +1,2 @@
 def login(token):
-    return bool(token)
+    return token is not None
"""
    review = review_patch_text(patch, repo_root=tmp_path, tests=["pytest"])
    assert review["semantic_risk"] is not None
    assert review["semantic_risk_error"] is None
    assert review["risk_level"] in {"high", "critical"}
    assert "human_review_required" in review["required_next_steps"]


def test_unmapped_hunk_is_reported_without_inventing_symbol(tmp_path: Path):
    _write(tmp_path, "notes.txt", "one\ntwo\nthree\n")
    build_graph(tmp_path)
    patch = """diff --git a/notes.txt b/notes.txt
--- a/notes.txt
+++ b/notes.txt
@@ -1,3 +1,3 @@
 one
-two
+changed
 three
"""
    result = assess_semantic_diff_risk(tmp_path, patch)
    assert result["affected_symbols"] == []
    assert result["unmapped_old_hunks"]
    assert "unmapped_changed_hunk" in result["categories"]
