from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import uuid
import shutil
import subprocess

from uacos.config import uacos_dir
from uacos.patching.engine import validate_patch, apply_patch as patch20_apply, rollback_patch as patch20_rollback
from uacos.learning.feedback import feedback_summary
from uacos.metrics.production import collect_production_metrics
from uacos.security.diff_parser import parse_unified_diff as parse_diff_for_secret_scan
from uacos.security.secret_scan import scan_text_for_secrets

def scan_patch_text_for_secrets(patch_text: str) -> list:
    """Secret scan for added lines, independent of uacos.patching.engine.validate_patch.

    validate_patch (patching/engine.py) does its own scope/hunk validation but
    has no secret detection at all — unlike uacos.security.patch_gate.validate_patch_text,
    which every apply_patch_with_backup() call goes through. run_transaction()
    uses validate_patch, not validate_patch_text, so without this it would
    commit secrets that the apply_patch_with_backup path would block. Reuses
    the same parser/scanner patch_gate.py uses rather than re-implementing it.
    """
    findings = []
    for fp in parse_diff_for_secret_scan(patch_text):
        added_text = "\n".join(fp.added_lines)
        for secret in scan_text_for_secrets(added_text, fp.path):
            findings.append({
                "severity": secret["severity"],
                "type": "secret_in_added_lines",
                "path": fp.path,
                "line": secret["line"],
                "message": secret["type"],
                "evidence": secret["evidence"],
            })
    return findings

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def new_tx_id() -> str:
    return "TX-" + uuid.uuid4().hex[:12]

def tx_root(repo_root: Path) -> Path:
    p = uacos_dir(repo_root) / "transactions"
    p.mkdir(parents=True, exist_ok=True)
    return p

def tx_dir(repo_root: Path, tx_id: str) -> Path:
    p = tx_root(repo_root) / tx_id
    p.mkdir(parents=True, exist_ok=True)
    return p

def tx_manifest_path(repo_root: Path, tx_id: str) -> Path:
    return tx_dir(repo_root, tx_id) / "manifest.json"

def _safe_rel(rel: str) -> bool:
    p = Path(rel)
    return bool(rel) and not p.is_absolute() and ".." not in p.parts and ".git" not in p.parts

def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def _write_manifest(repo_root: Path, manifest: dict) -> dict:
    path = tx_manifest_path(repo_root, manifest["id"])
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest["manifest_file"] = str(path)
    return manifest

def _append_event(repo_root: Path, manifest: dict, event: str, data: dict | None = None) -> dict:
    row = {"ts": utcnow(), "event": event, "data": data or {}}
    manifest.setdefault("events", []).append(row)
    _write_manifest(repo_root, manifest)
    return row

def create_checkpoint(repo_root: Path, tx_id: str, files: list[str]) -> dict:
    d = tx_dir(repo_root, tx_id) / "checkpoint"
    d.mkdir(parents=True, exist_ok=True)
    saved = []
    missing = []
    for rel in sorted(set(files)):
        if not _safe_rel(rel):
            continue
        src = repo_root / rel
        dst = d / rel
        if src.exists() and src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            saved.append({"path": rel, "checkpoint": str(dst)})
        else:
            missing.append(rel)
    return {"status": "ok", "saved": saved, "missing": missing, "checkpoint_dir": str(d)}

def restore_checkpoint(repo_root: Path, manifest: dict) -> dict:
    cp = Path(manifest["checkpoint"]["checkpoint_dir"])
    restored = []
    # Remove files created by patch stage first
    for item in reversed(manifest.get("patch_manifest", {}).get("changed", [])):
        if item.get("operation") == "new":
            target = repo_root / item["path"]
            if target.exists():
                target.unlink()
    for item in manifest.get("checkpoint", {}).get("saved", []):
        rel = item["path"]
        src = Path(item["checkpoint"])
        dst = repo_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.exists():
            shutil.copy2(src, dst)
            restored.append(rel)
    return {"status": "ok", "restored": restored}

def run_tests(repo_root: Path, tests: list[str]) -> list[dict]:
    results = []
    for cmd in tests or []:
        res = subprocess.run(cmd, cwd=repo_root, shell=True, capture_output=True, text=True, timeout=180)
        row = {"command": cmd, "returncode": res.returncode, "stdout": res.stdout[-4000:], "stderr": res.stderr[-4000:], "ok": res.returncode == 0}
        results.append(row)
        if not row["ok"]:
            break
    return results

def begin_transaction(repo_root: Path, title: str, objective: str, files: list[str] | None = None, tests: list[str] | None = None) -> dict:
    tx_id = new_tx_id()
    files = files or []
    manifest = {
        "id": tx_id,
        "status": "created",
        "title": title,
        "objective": objective,
        "repo": str(repo_root),
        "files": files,
        "tests": tests or [],
        "checkpoint": create_checkpoint(repo_root, tx_id, files),
        "patch_manifest": None,
        "test_results": [],
        "events": [],
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    _write_manifest(repo_root, manifest)
    _append_event(repo_root, manifest, "transaction_created", {"files": files, "tests": tests or []})
    return manifest

def run_transaction(repo_root: Path, patch_file: Path, title: str = "Transactional patch", objective: str = "", allowed_files: list[str] | None = None, allowed_dirs: list[str] | None = None, tests: list[str] | None = None, dry_run: bool = False, auto_rollback: bool = True) -> dict:
    allowed_files = allowed_files or []
    tests = tests or []
    patch_text = patch_file.read_text(encoding="utf-8", errors="replace")
    validation = validate_patch(repo_root, patch_text, allowed_files=allowed_files, allowed_dirs=allowed_dirs or [])
    files = []
    for f in validation.get("files", []):
        for key in ["old_path", "new_path", "path"]:
            rel = f.get(key)
            if rel and rel not in files:
                files.append(rel)
    if allowed_files:
        files = sorted(set(files + allowed_files))
    manifest = begin_transaction(repo_root, title=title, objective=objective, files=files, tests=tests)
    manifest["dry_run"] = dry_run
    manifest["patch_file"] = str(patch_file)
    manifest["validation"] = validation
    _append_event(repo_root, manifest, "patch_validated", {"status": validation.get("status"), "file_count": validation.get("file_count")})
    if validation.get("status") != "pass":
        manifest["status"] = "blocked"
        manifest["updated_at"] = utcnow()
        _append_event(repo_root, manifest, "transaction_blocked", {"reason": "patch_validation_failed"})
        return _write_manifest(repo_root, manifest)

    secret_findings = scan_patch_text_for_secrets(patch_text)
    manifest["secret_scan"] = {"findings": secret_findings}
    _append_event(repo_root, manifest, "secret_scan_completed", {"findings_count": len(secret_findings)})
    if any(f["severity"] == "high" for f in secret_findings):
        manifest["status"] = "blocked"
        manifest["updated_at"] = utcnow()
        _append_event(repo_root, manifest, "transaction_blocked", {"reason": "secret_detected_in_patch"})
        return _write_manifest(repo_root, manifest)

    if dry_run:
        manifest["status"] = "planned"
        manifest["updated_at"] = utcnow()
        _append_event(repo_root, manifest, "dry_run_planned", {})
        return _write_manifest(repo_root, manifest)

    patch_manifest = patch20_apply(repo_root, patch_file, allowed_files=allowed_files, allowed_dirs=allowed_dirs or [], tests=[])
    manifest["patch_manifest"] = patch_manifest
    _append_event(repo_root, manifest, "patch_applied", {"status": patch_manifest.get("status")})
    if patch_manifest.get("status") != "applied":
        manifest["status"] = "rolled_back" if patch_manifest.get("status") == "rolled_back" else "failed"
        manifest["updated_at"] = utcnow()
        return _write_manifest(repo_root, manifest)

    test_results = run_tests(repo_root, tests)
    manifest["test_results"] = test_results
    failed = any(not r["ok"] for r in test_results)
    _append_event(repo_root, manifest, "tests_completed", {"failed": failed, "count": len(test_results)})
    if failed and auto_rollback:
        rb = restore_checkpoint(repo_root, manifest)
        manifest["rollback"] = rb
        manifest["status"] = "rolled_back"
        _append_event(repo_root, manifest, "auto_rollback_completed", rb)
    elif failed:
        manifest["status"] = "failed"
    else:
        manifest["status"] = "committed"
        _append_event(repo_root, manifest, "transaction_committed", {})
    manifest["updated_at"] = utcnow()
    try:
        manifest["metrics_after"] = collect_production_metrics(repo_root).get("health")
    except Exception as exc:
        manifest["metrics_after_error"] = str(exc)
    return _write_manifest(repo_root, manifest)

def rollback_transaction(repo_root: Path, tx_id: str) -> dict:
    path = tx_manifest_path(repo_root, tx_id)
    manifest = _read_manifest(path)
    rb = restore_checkpoint(repo_root, manifest)
    manifest["manual_rollback"] = rb
    manifest["status"] = "rolled_back"
    manifest["updated_at"] = utcnow()
    _append_event(repo_root, manifest, "manual_rollback_completed", rb)
    return _write_manifest(repo_root, manifest)

def transaction_status(repo_root: Path, tx_id: str) -> dict:
    path = tx_manifest_path(repo_root, tx_id)
    if not path.exists():
        return {"status": "missing", "tx_id": tx_id}
    manifest = _read_manifest(path)
    return {"status": "ok", "transaction": manifest}

def list_transactions(repo_root: Path) -> dict:
    rows = []
    for p in sorted(tx_root(repo_root).glob("TX-*/manifest.json")):
        try:
            m = _read_manifest(p)
            rows.append({"id": m.get("id"), "status": m.get("status"), "title": m.get("title"), "updated_at": m.get("updated_at"), "manifest_file": str(p)})
        except Exception as exc:
            rows.append({"manifest_file": str(p), "error": str(exc)})
    return {"status": "ok", "count": len(rows), "transactions": rows}

def transaction_report(repo_root: Path, tx_id: str) -> str:
    st = transaction_status(repo_root, tx_id)
    if st["status"] != "ok":
        return f"# Transaction {tx_id}\n\nMissing.\n"
    m = st["transaction"]
    lines = [f"# UACOS Transaction Report — {tx_id}", "", f"Status: **{m.get('status')}**", f"Title: {m.get('title')}", f"Objective: {m.get('objective')}", "", "## Files"]
    for f in m.get("files", []):
        lines.append(f"- {f}")
    lines.append("")
    lines.append("## Tests")
    for t in m.get("test_results", []):
        lines.append(f"- `{t.get('command')}` → {t.get('returncode')}")
    lines.append("")
    lines.append("## Events")
    for e in m.get("events", []):
        lines.append(f"- {e.get('ts')} — {e.get('event')}")
    return "\n".join(lines) + "\n"
