
from pathlib import Path
import tempfile
from uacos.ops.packaging import bootstrap
from uacos.transaction.engine import run_transaction, rollback_transaction, list_transactions, transaction_status

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
        bootstrap(repo)

        good = repo / "good.diff"
        good.write_text(
            "diff --git a/app.py b/app.py\n"
            "--- a/app.py\n"
            "+++ b/app.py\n"
            "@@ -1,2 +1,2 @@\n"
            " def value():\n"
            "-    return 1\n"
            "+    return 42\n",
            encoding="utf-8",
        )
        tx = run_transaction(repo, good, title="Good patch", allowed_files=["app.py"], tests=["python -S -c \"from pathlib import Path; assert 'return 42' in Path('app.py').read_text()\""])
        assert tx["status"] == "committed", tx
        assert "return 42" in (repo / "app.py").read_text(encoding="utf-8")

        bad = repo / "bad.diff"
        bad.write_text(
            "diff --git a/app.py b/app.py\n"
            "--- a/app.py\n"
            "+++ b/app.py\n"
            "@@ -1,2 +1,2 @@\n"
            " def value():\n"
            "-    return 42\n"
            "+    return 99\n",
            encoding="utf-8",
        )
        tx2 = run_transaction(repo, bad, title="Bad patch", allowed_files=["app.py"], tests=["python -S -c \"from pathlib import Path; assert 'return 42' in Path('app.py').read_text()\""])
        assert tx2["status"] == "rolled_back", tx2
        assert "return 42" in (repo / "app.py").read_text(encoding="utf-8")

        rb = rollback_transaction(repo, tx["id"])
        assert rb["status"] == "rolled_back"
        assert "return 1" in (repo / "app.py").read_text(encoding="utf-8")

        listed = list_transactions(repo)
        assert listed["count"] >= 2
        st = transaction_status(repo, tx2["id"])
        assert st["status"] == "ok"
        print("PHASE27_SMOKE_OK")
        print("transactions=", listed["count"])
        print("bad_status=", tx2["status"])

if __name__ == "__main__":
    main()
