from pathlib import Path
import tempfile
from uacos.ops.packaging import bootstrap, health_check, backup_uacos, write_run_scripts, release_check

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"; repo.mkdir()
        (repo / "main.py").write_text("def ok():\n    return True\n", encoding="utf-8")
        boot = bootstrap(repo)
        health = health_check(repo)
        backup = backup_uacos(repo, Path(td) / "backup.zip")
        scripts = write_run_scripts(repo, Path(td) / "ops")
        rel = release_check(repo)
        assert boot["status"] == "ok"
        assert health["status"] == "pass"
        assert Path(backup["backup"]).exists()
        assert scripts["status"] == "ok"
        print("PHASE10_SMOKE_OK")
        print("health=", health["status"])
        print("backup=", backup["backup"])
        print("release=", rel["status"])

if __name__ == "__main__":
    main()
