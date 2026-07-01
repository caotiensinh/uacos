from pathlib import Path
from uacos.ops.packaging import bootstrap, health_check, doctor, backup_uacos, export_uacos, import_uacos, release_check, write_run_scripts, write_systemd_service

def test_phase10_bootstrap_health_doctor(tmp_path: Path):
    repo = tmp_path / "repo"; repo.mkdir()
    (repo / "app.py").write_text("def ok():\n    return True\n", encoding="utf-8")
    boot = bootstrap(repo)
    assert boot["status"] == "ok"
    assert health_check(repo)["status"] == "pass"
    assert doctor(repo, auto_fix=True)["status"] == "pass"

def test_phase10_backup_export_import(tmp_path: Path):
    repo = tmp_path / "repo"; repo.mkdir()
    (repo / "app.py").write_text("x = 1\n", encoding="utf-8")
    bootstrap(repo)
    backup = backup_uacos(repo, tmp_path / "backup.zip")
    assert Path(backup["backup"]).exists()
    exported = export_uacos(repo, tmp_path / "export.zip")
    assert Path(exported["backup"]).exists()
    repo2 = tmp_path / "repo2"; repo2.mkdir()
    imported = import_uacos(repo2, tmp_path / "export.zip")
    assert imported["status"] == "ok"
    assert (repo2 / ".uacos").exists()

def test_phase10_scripts_systemd_release_check(tmp_path: Path):
    repo = tmp_path / "repo"; repo.mkdir()
    (repo / "app.py").write_text("x = 1\n", encoding="utf-8")
    bootstrap(repo)
    scripts = write_run_scripts(repo, tmp_path / "ops", port=9999)
    assert scripts["status"] == "ok"
    for f in scripts["files"]:
        assert Path(f).exists()
    svc = write_systemd_service(repo, tmp_path / "ops" / "uacos-dashboard.service", port=9999, user="aiserver")
    assert Path(svc["service_file"]).exists()
    assert "ExecStart" in Path(svc["service_file"]).read_text(encoding="utf-8")
    rel = release_check(repo)
    assert rel["status"] in {"pass", "warn"}
