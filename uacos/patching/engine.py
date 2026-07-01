from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import re
import shutil
import uuid
import subprocess

from uacos.config import uacos_dir

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def new_patch_id() -> str:
    return "PATCH-" + uuid.uuid4().hex[:12]

def patch_runs_dir(repo_root: Path) -> Path:
    p = uacos_dir(repo_root) / "patch_runs"
    p.mkdir(parents=True, exist_ok=True)
    return p

def _norm_path(p: str | None) -> str | None:
    if not p:
        return None
    p = p.strip()
    if p == "/dev/null":
        return None
    if p.startswith("a/") or p.startswith("b/"):
        p = p[2:]
    return p.replace("\\", "/")

def _is_safe_rel(rel: str) -> bool:
    if not rel:
        return False
    pp = Path(rel)
    if pp.is_absolute():
        return False
    if ".." in pp.parts:
        return False
    if rel.startswith(".git/") or "/.git/" in rel:
        return False
    return True

def parse_unified_diff(patch_text: str) -> list[dict]:
    lines = patch_text.splitlines()
    files = []
    current = None
    for line in lines:
        if line.startswith("diff --git "):
            if current:
                files.append(current)
            m = re.match(r"diff --git a/(.*?) b/(.*)$", line)
            old = m.group(1) if m else None
            new = m.group(2) if m else None
            current = {
                "old_path": _norm_path(old),
                "new_path": _norm_path(new),
                "operation": "modify",
                "headers": [line],
                "hunks": [],
                "raw_lines": [line],
                "current_hunk": None,
            }
            continue
        if current is None:
            continue
        current["raw_lines"].append(line)
        if line.startswith("new file mode"):
            current["operation"] = "new"
        elif line.startswith("deleted file mode"):
            current["operation"] = "delete"
        elif line.startswith("rename from "):
            current["old_path"] = _norm_path(line[len("rename from "):])
            current["operation"] = "rename"
        elif line.startswith("rename to "):
            current["new_path"] = _norm_path(line[len("rename to "):])
            current["operation"] = "rename"
        elif line.startswith("--- "):
            oldp = _norm_path(line[4:].strip())
            if oldp is None:
                current["operation"] = "new"
            else:
                current["old_path"] = oldp
            current["headers"].append(line)
        elif line.startswith("+++ "):
            newp = _norm_path(line[4:].strip())
            if newp is None:
                current["operation"] = "delete"
            else:
                current["new_path"] = newp
            current["headers"].append(line)
        elif line.startswith("@@"):
            h = {"header": line, "lines": []}
            current["hunks"].append(h)
            current["current_hunk"] = h
        elif current.get("current_hunk") is not None:
            current["current_hunk"]["lines"].append(line)
    if current:
        files.append(current)
    for f in files:
        f.pop("current_hunk", None)
        if f["operation"] == "modify" and f.get("old_path") != f.get("new_path"):
            f["operation"] = "rename_modify" if f.get("old_path") and f.get("new_path") else f["operation"]
        f["path"] = f.get("new_path") or f.get("old_path")
    return files

def _allowed(rel: str, allowed_files: list[str] | None = None, allowed_dirs: list[str] | None = None) -> bool:
    allowed_files = allowed_files or []
    allowed_dirs = allowed_dirs or []
    if not allowed_files and not allowed_dirs:
        return True
    reln = rel.replace("\\", "/")
    if reln in [f.replace("\\", "/") for f in allowed_files]:
        return True
    for d in allowed_dirs:
        dn = d.replace("\\", "/").rstrip("/") + "/"
        if reln.startswith(dn):
            return True
    return False

def validate_patch(repo_root: Path, patch_text: str, allowed_files: list[str] | None = None, allowed_dirs: list[str] | None = None) -> dict:
    files = parse_unified_diff(patch_text)
    findings = []
    for f in files:
        op = f["operation"]
        paths = [p for p in [f.get("old_path"), f.get("new_path")] if p]
        for rel in paths:
            if not _is_safe_rel(rel):
                findings.append({"severity": "error", "path": rel, "reason": "unsafe_path"})
            if not _allowed(rel, allowed_files, allowed_dirs):
                findings.append({"severity": "error", "path": rel, "reason": "outside_allowed_scope"})
        if op in {"modify", "rename_modify"}:
            old_path = repo_root / f["old_path"]
            if not old_path.exists():
                findings.append({"severity": "error", "path": f["old_path"], "reason": "modify_target_missing"})
        if op == "new":
            new_path = repo_root / f["new_path"]
            if new_path.exists():
                findings.append({"severity": "error", "path": f["new_path"], "reason": "new_file_already_exists"})
        if op == "delete":
            old_path = repo_root / f["old_path"]
            if not old_path.exists():
                findings.append({"severity": "error", "path": f["old_path"], "reason": "delete_target_missing"})
        if op in {"rename", "rename_modify"}:
            old_path = repo_root / f["old_path"]
            new_path = repo_root / f["new_path"]
            if not old_path.exists():
                findings.append({"severity": "error", "path": f["old_path"], "reason": "rename_source_missing"})
            if new_path.exists():
                findings.append({"severity": "error", "path": f["new_path"], "reason": "rename_target_exists"})
    status = "pass" if not any(x["severity"] == "error" for x in findings) else "fail"
    return {"status": status, "file_count": len(files), "files": [{k:v for k,v in f.items() if k != "raw_lines"} for f in files], "findings": findings}

def _apply_modify_text(old_text: str, file_diff: dict) -> tuple[str, list[str]]:
    old_lines = old_text.splitlines()
    result = []
    idx = 0
    notes = []
    for h in file_diff.get("hunks", []):
        m = re.match(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@", h["header"])
        if not m:
            notes.append("hunk_header_parse_failed")
            continue
        old_start = int(m.group(1)) - 1
        while idx < old_start and idx < len(old_lines):
            result.append(old_lines[idx])
            idx += 1
        for line in h["lines"]:
            if line.startswith(" "):
                expected = line[1:]
                if idx < len(old_lines):
                    # tolerate exact line, otherwise keep moving but note mismatch
                    if old_lines[idx] != expected:
                        notes.append(f"context_mismatch_at:{idx+1}")
                    result.append(old_lines[idx])
                    idx += 1
                else:
                    result.append(expected)
            elif line.startswith("-"):
                expected = line[1:]
                if idx < len(old_lines):
                    if old_lines[idx] != expected:
                        notes.append(f"delete_mismatch_at:{idx+1}")
                    idx += 1
            elif line.startswith("+"):
                result.append(line[1:])
            elif line.startswith("\\"):
                continue
    while idx < len(old_lines):
        result.append(old_lines[idx])
        idx += 1
    return "\n".join(result) + ("\n" if old_text.endswith("\n") or result else ""), notes

def _new_file_text(file_diff: dict) -> str:
    lines = []
    for h in file_diff.get("hunks", []):
        for line in h["lines"]:
            if line.startswith("+"):
                lines.append(line[1:])
            elif line.startswith(" "):
                lines.append(line[1:])
    return "\n".join(lines) + ("\n" if lines else "")

def _run_tests(repo_root: Path, tests: list[str] | None = None) -> list[dict]:
    results = []
    for cmd in tests or []:
        res = subprocess.run(cmd, cwd=repo_root, shell=True, capture_output=True, text=True, timeout=180)
        results.append({"command": cmd, "returncode": res.returncode, "stdout": res.stdout[-3000:], "stderr": res.stderr[-3000:], "ok": res.returncode == 0})
        if res.returncode != 0:
            break
    return results

def apply_patch(repo_root: Path, patch_file: Path, allowed_files: list[str] | None = None, allowed_dirs: list[str] | None = None, tests: list[str] | None = None, dry_run: bool = False) -> dict:
    patch_text = patch_file.read_text(encoding="utf-8", errors="replace")
    validation = validate_patch(repo_root, patch_text, allowed_files=allowed_files, allowed_dirs=allowed_dirs)
    run_id = new_patch_id()
    run_dir = patch_runs_dir(repo_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "id": run_id,
        "status": "planned" if dry_run else "started",
        "patch_file": str(patch_file),
        "validation": validation,
        "dry_run": dry_run,
        "changed": [],
        "tests": [],
        "created_at": utcnow(),
        "run_dir": str(run_dir),
    }
    if validation["status"] != "pass":
        manifest["status"] = "blocked"
        (run_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest["manifest_file"] = str(run_dir / "manifest.json")
        return manifest
    if dry_run:
        (run_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest["manifest_file"] = str(run_dir / "manifest.json")
        return manifest

    try:
        files = parse_unified_diff(patch_text)
        backup_dir = run_dir / "backup"
        backup_dir.mkdir()
        for f in files:
            op = f["operation"]
            if op == "new":
                target = repo_root / f["new_path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(_new_file_text(f), encoding="utf-8")
                manifest["changed"].append({"operation": "new", "path": f["new_path"]})
            elif op == "delete":
                target = repo_root / f["old_path"]
                backup = backup_dir / f["old_path"]
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, backup)
                target.unlink()
                manifest["changed"].append({"operation": "delete", "path": f["old_path"], "backup": str(backup)})
            elif op in {"rename", "rename_modify"}:
                src = repo_root / f["old_path"]
                dst = repo_root / f["new_path"]
                backup = backup_dir / f["old_path"]
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, backup)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                notes = []
                if op == "rename_modify" and f.get("hunks"):
                    old_text = dst.read_text(encoding="utf-8", errors="replace")
                    new_text, notes = _apply_modify_text(old_text, f)
                    dst.write_text(new_text, encoding="utf-8")
                manifest["changed"].append({"operation": op, "old_path": f["old_path"], "new_path": f["new_path"], "backup": str(backup), "notes": notes})
            else:
                target = repo_root / f["old_path"]
                backup = backup_dir / f["old_path"]
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, backup)
                old_text = target.read_text(encoding="utf-8", errors="replace")
                new_text, notes = _apply_modify_text(old_text, f)
                target.write_text(new_text, encoding="utf-8")
                manifest["changed"].append({"operation": "modify", "path": f["old_path"], "backup": str(backup), "notes": notes})
        manifest["tests"] = _run_tests(repo_root, tests)
        if any(not t["ok"] for t in manifest["tests"]):
            rollback_patch(repo_root, manifest)
            manifest["status"] = "rolled_back"
        else:
            manifest["status"] = "applied"
    except Exception as exc:
        manifest["status"] = "error"
        manifest["error"] = {"type": type(exc).__name__, "message": str(exc)}
        try:
            rollback_patch(repo_root, manifest)
            manifest["rollback_after_error"] = True
        except Exception as rex:
            manifest["rollback_error"] = {"type": type(rex).__name__, "message": str(rex)}
    (run_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest["manifest_file"] = str(run_dir / "manifest.json")
    return manifest

def rollback_patch(repo_root: Path, manifest: dict | Path) -> dict:
    if isinstance(manifest, Path):
        manifest = json.loads(manifest.read_text(encoding="utf-8"))
    for item in reversed(manifest.get("changed", [])):
        op = item.get("operation")
        if op == "new":
            target = repo_root / item["path"]
            if target.exists():
                target.unlink()
        elif op == "delete":
            backup = Path(item["backup"])
            target = repo_root / item["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup, target)
        elif op in {"rename", "rename_modify"}:
            dst = repo_root / item["new_path"]
            src = repo_root / item["old_path"]
            if dst.exists():
                if src.exists():
                    src.unlink()
                shutil.move(str(dst), str(src))
            backup = Path(item["backup"])
            if backup.exists():
                shutil.copy2(backup, src)
        elif op == "modify":
            backup = Path(item["backup"])
            target = repo_root / item["path"]
            if backup.exists():
                shutil.copy2(backup, target)
    return {"status": "ok", "rolled_back": len(manifest.get("changed", []))}
