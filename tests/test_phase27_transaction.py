from pathlib import Path
from uacos.ops.packaging import bootstrap
from uacos.transaction.engine import run_transaction, rollback_transaction, list_transactions


def test_transaction_blocks_secret_in_added_lines(tmp_path: Path):
    # Regression test: run_transaction() validates scope/hunks via
    # uacos.patching.engine.validate_patch, which has no secret detection at
    # all (unlike uacos.security.patch_gate.validate_patch_text, used by
    # apply_patch_with_backup). Before this fix, a patch adding a real-shaped
    # AWS key committed successfully and wrote the secret to disk.
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "config.py").write_text("SETTING = 1\n", encoding="utf-8")
    bootstrap(repo)

    patch = repo / "change.diff"
    patch.write_text(
        "diff --git a/config.py b/config.py\n--- a/config.py\n+++ b/config.py\n"
        "@@ -1,1 +1,2 @@\n SETTING = 1\n+AWS_ACCESS_KEY = \"AKIAIOSFODNN7EXAMPLE\"\n",
        encoding="utf-8",
    )
    tx = run_transaction(repo, patch, title="add setting", allowed_files=["config.py"], tests=[])
    assert tx["status"] == "blocked", tx
    assert (repo / "config.py").read_text(encoding="utf-8") == "SETTING = 1\n"
    findings = tx["secret_scan"]["findings"]
    assert any(f["type"] == "secret_in_added_lines" for f in findings)

def test_transaction_commit_fail_rollback_manual_rollback(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
    bootstrap(repo)

    good = repo / "good.diff"
    good.write_text(
        "diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@ -1,2 +1,2 @@\n def value():\n-    return 1\n+    return 42\n",
        encoding="utf-8",
    )
    tx = run_transaction(repo, good, title="good", allowed_files=["app.py"], tests=["python -S -c \"from pathlib import Path; assert 'return 42' in Path('app.py').read_text()\""])
    assert tx["status"] == "committed", tx
    assert "return 42" in (repo / "app.py").read_text(encoding="utf-8")

    bad = repo / "bad.diff"
    bad.write_text(
        "diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@ -1,2 +1,2 @@\n def value():\n-    return 42\n+    return 99\n",
        encoding="utf-8",
    )
    tx2 = run_transaction(repo, bad, title="bad", allowed_files=["app.py"], tests=["python -S -c \"from pathlib import Path; assert 'return 42' in Path('app.py').read_text()\""])
    assert tx2["status"] == "rolled_back", tx2
    assert "return 42" in (repo / "app.py").read_text(encoding="utf-8")

    rb = rollback_transaction(repo, tx["id"])
    assert rb["status"] == "rolled_back"
    assert "return 1" in (repo / "app.py").read_text(encoding="utf-8")
    assert list_transactions(repo)["count"] >= 2
