from pathlib import Path
import fnmatch
from uacos.memory.store import add_memory, search_memories, read_memories
from uacos.security.diff_parser import parse_unified_diff

def add_regression_rule(repo_root: Path, title: str, pattern: str, severity: str = "medium", reason: str = "", source: str = "user") -> dict:
    value = f"{title} | pattern={pattern} | severity={severity} | reason={reason}"
    return add_memory(repo_root, "regression_rule", title, value, source=source, confidence=1.0, tags=["regression", severity], applies_to=[pattern])

def _rule_matches_path(rule: dict, path: str) -> bool:
    patterns = rule.get("applies_to", [])
    for pat in patterns:
        if fnmatch.fnmatch(path, pat) or path.startswith(pat.rstrip("/") + "/") or pat in path:
            return True
    return False

def regression_check_patch(repo_root: Path, patch_file: Path) -> dict:
    text = patch_file.read_text(encoding="utf-8", errors="replace")
    patches = parse_unified_diff(text)
    rules = [r for r in read_memories(repo_root) if r.get("kind") == "regression_rule"]
    findings = []
    changed = [p.path for p in patches]
    for path in changed:
        for rule in rules:
            if _rule_matches_path(rule, path):
                severity = "medium"
                for tag in rule.get("tags", []):
                    if tag in {"low", "medium", "high", "critical"}:
                        severity = tag
                findings.append({
                    "severity": severity,
                    "type": "regression_rule_match",
                    "path": path,
                    "rule_id": rule["id"],
                    "rule": rule["key"],
                    "message": rule["value"],
                })
    status = "fail" if any(f["severity"] in {"high", "critical"} for f in findings) else "pass"
    return {"status": status, "changed_files": changed, "findings": findings}
