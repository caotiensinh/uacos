from pathlib import Path
from datetime import datetime, timezone
import json, shutil, uuid
from uacos.agent.task import load_task
from uacos.config import uacos_dir
from uacos.security.patch_gate import validate_patch_text
from uacos.security.diff_parser import parse_unified_diff
from uacos.execution.test_runner import run_task_tests
from uacos.execution.failed_memory import record_failure

def utcnow():
    return datetime.now(timezone.utc).isoformat()

def new_change_id():
    return "CHANGE-" + uuid.uuid4().hex[:12]

def manifests_dir(repo_root: Path) -> Path:
    p = uacos_dir(repo_root) / "change_manifests"
    p.mkdir(parents=True, exist_ok=True)
    return p

def backups_dir(repo_root: Path, change_id: str) -> Path:
    p = uacos_dir(repo_root) / "backups" / change_id
    p.mkdir(parents=True, exist_ok=True)
    return p

def _safe_repo_path(repo_root: Path, rel_path: str) -> Path:
    target = (repo_root / rel_path).resolve()
    target.relative_to(repo_root.resolve())
    return target

def _parse_hunks(lines):
    hunks = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("@@"):
            header = lines[i]
            body = []
            i += 1
            while i < len(lines) and not lines[i].startswith("@@"):
                body.append(lines[i])
                i += 1
            hunks.append((header, body))
        else:
            i += 1
    return hunks

def _old_new_from_hunk(body):
    old, new = [], []
    for line in body:
        if line.startswith("-"):
            old.append(line[1:])
        elif line.startswith("+"):
            new.append(line[1:])
        elif line.startswith(" "):
            old.append(line[1:])
            new.append(line[1:])
        elif line == "":
            old.append("")
            new.append("")
    return old, new

def _apply_file_patch(existing_text: str, diff_lines):
    lines = existing_text.splitlines()
    notes = []
    for header, body in _parse_hunks(diff_lines):
        old, new = _old_new_from_hunk(body)
        pos = None
        if old:
            for idx in range(0, len(lines) - len(old) + 1):
                if lines[idx: idx + len(old)] == old:
                    pos = idx
                    break
        else:
            pos = len(lines)
        if pos is None:
            raise ValueError(f"hunk_old_block_not_found:{header}")
        lines = lines[:pos] + new + lines[pos + len(old):]
        notes.append(f"applied:{header}")
    return "\n".join(lines) + ("\n" if existing_text.endswith("\n") or lines else ""), notes


def _is_new_file_patch(patch_text: str, file_path: str) -> bool:
    lines = _file_diff_lines(patch_text, file_path)
    return any(l.startswith("--- /dev/null") for l in lines) or any(l.startswith("new file mode") for l in lines)

def _apply_new_file_patch(diff_lines):
    new_lines = []
    capture = False
    for line in diff_lines:
        if line.startswith("@@"):
            capture = True
            continue
        if not capture:
            continue
        if line.startswith("+"):
            new_lines.append(line[1:])
        elif line.startswith(" "):
            new_lines.append(line[1:])
        elif line.startswith("-"):
            continue
    return "\n".join(new_lines) + ("\n" if new_lines else "")

def _file_diff_lines(patch_text: str, file_path: str):
    capture = False
    out = []
    for line in patch_text.splitlines():
        if line.startswith("diff --git "):
            capture = file_path in line
            continue
        if capture:
            out.append(line)
    return out

def _restore_changed(repo_root: Path, changed_files):
    for item in changed_files:
        target = _safe_repo_path(repo_root, item["path"])
        backup = Path(item["backup"])
        if item.get("created"):
            if target.exists():
                target.unlink()
        elif backup.exists():
            shutil.copy2(backup, target)

def apply_patch_with_backup(repo_root: Path, task_file: Path, patch_file: Path, run_tests: bool = True, auto_rollback: bool = True):
    task = load_task(task_file)
    patch_text = patch_file.read_text(encoding="utf-8", errors="replace")
    patch_check = validate_patch_text(patch_text, allowed_files=task.get("allowed_files", []), allowed_dirs=task.get("allowed_dirs", []))
    if patch_check["status"] != "pass":
        record_failure(repo_root, task["id"], "apply_blocked_patch_check_failed", patch_check)
        return {"status": "blocked", "reason": "patch_check_failed", "patch_check": patch_check}

    change_id = new_change_id()
    bdir = backups_dir(repo_root, change_id)
    changed, notes = [], []
    patches = parse_unified_diff(patch_text)
    try:
        for fp in patches:
            rel = fp.path
            target = _safe_repo_path(repo_root, rel)
            diff_lines = _file_diff_lines(patch_text, rel)
            backup_path = bdir / rel
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if _is_new_file_patch(patch_text, rel):
                if target.exists():
                    raise FileExistsError(f"new_file_target_already_exists:{rel}")
                target.parent.mkdir(parents=True, exist_ok=True)
                new_text = _apply_new_file_patch(diff_lines)
                target.write_text(new_text, encoding="utf-8")
                changed.append({"path": rel, "backup": str(backup_path), "created": True})
                notes.append(f"created_new_file:{rel}")
            else:
                if not target.exists():
                    raise FileNotFoundError(f"target_file_missing:{rel}")
                shutil.copy2(target, backup_path)
                existing = target.read_text(encoding="utf-8", errors="replace")
                new_text, ns = _apply_file_patch(existing, diff_lines)
                target.write_text(new_text, encoding="utf-8")
                changed.append({"path": rel, "backup": str(backup_path), "created": False})
                notes.extend(ns)

        test_result = run_task_tests(repo_root, task_file) if run_tests else None
        final_status, rolled_back = "applied", False
        if test_result and test_result["status"] != "pass":
            final_status = "rolled_back"
            if auto_rollback:
                _restore_changed(repo_root, changed)
                rolled_back = True
                record_failure(repo_root, task["id"], "post_apply_tests_failed_auto_rollback", test_result)

        manifest = {
            "id": change_id, "task_id": task["id"], "patch_file": str(patch_file),
            "status": final_status, "rolled_back": rolled_back, "changed_files": changed,
            "patch_check": patch_check, "test_result": test_result, "applied_notes": notes,
            "created_at": utcnow(),
        }
    except Exception as exc:
        _restore_changed(repo_root, changed)
        detail = {"error": f"{type(exc).__name__}:{exc}", "changed_files": changed}
        record_failure(repo_root, task["id"], "apply_exception_rollback", detail)
        manifest = {
            "id": change_id, "task_id": task["id"], "patch_file": str(patch_file),
            "status": "rolled_back", "rolled_back": True, "changed_files": changed,
            "error": detail, "patch_check": patch_check, "created_at": utcnow(),
        }

    manifest_path = manifests_dir(repo_root) / f"{change_id}.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest["manifest_file"] = str(manifest_path)
    return manifest

def rollback_manifest(repo_root: Path, manifest_file: Path):
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    _restore_changed(repo_root, manifest.get("changed_files", []))
    manifest["status"] = "rolled_back"
    manifest["rolled_back"] = True
    manifest["rolled_back_at"] = utcnow()
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest

def done_gate(repo_root: Path, manifest_file: Path):
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    findings = []
    if manifest.get("status") != "applied":
        findings.append({"type": "not_applied", "message": f"status={manifest.get('status')}"})
    if manifest.get("rolled_back"):
        findings.append({"type": "rolled_back", "message": "change was rolled back"})
    pc = manifest.get("patch_check")
    if not pc or pc.get("status") != "pass":
        findings.append({"type": "patch_check_not_passed", "message": "patch check missing or failed"})
    tr = manifest.get("test_result")
    if not tr:
        findings.append({"type": "tests_missing", "message": "no post-apply tests recorded"})
    elif tr.get("status") != "pass":
        findings.append({"type": "tests_not_passed", "message": f"test_status={tr.get('status')}"})
    return {"status": "done" if not findings else "not_done", "manifest": str(manifest_file), "findings": findings}

def list_manifests(repo_root: Path):
    items = []
    for path in sorted(manifests_dir(repo_root).glob("CHANGE-*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            items.append({"id": data.get("id"), "status": data.get("status"), "task_id": data.get("task_id"), "created_at": data.get("created_at"), "manifest_file": str(path)})
        except Exception as exc:
            items.append({"manifest_file": str(path), "error": str(exc)})
    return {"count": len(items), "manifests": items}
