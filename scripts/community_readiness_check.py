from __future__ import annotations

from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REPORT = ROOT / "reports" / "community_readiness_report.json"


REQUIRED_ROOT = [
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "pyproject.toml",
]

REQUIRED_DOCS = [
    "USER_GUIDE.md",
    "AUTO_MODE.md",
    "INSTALLATION.md",
    "SECURITY_MODEL.md",
    "TROUBLESHOOTING.md",
    "RELEASE_CHECKLIST.md",
    "PERFORMANCE_MEASUREMENT.md",
    "DOCUMENTATION_INDEX.md",
]


def check_pyproject() -> list[dict]:
    issues = []
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    required = {
        'name = "uacos"': "project.name must be uacos",
        'requires-python = ">=3.9"': "requires-python must be >=3.9",
        'uacos = "uacos.cli:main"': "uacos console script missing",
        'readme = "README.md"': "README.md must be package readme",
        'Programming Language :: Python :: 3.14': "Python 3.14 classifier missing",
    }
    for needle, detail in required.items():
        if needle not in text:
            issues.append({"type": "pyproject", "detail": detail})
    return issues


def check_files() -> list[dict]:
    issues = []
    for rel in REQUIRED_ROOT:
        if not (ROOT / rel).exists():
            issues.append({"type": "missing_root_file", "file": rel})
    for rel in REQUIRED_DOCS:
        if not (DOCS / rel).exists():
            issues.append({"type": "missing_doc_file", "file": rel})
    return issues


def check_doc_links() -> list[dict]:
    issues = []
    for path in DOCS.glob("*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"\[[^\]]+\]\(([^)]+\.md(?:#[^)]+)?)\)", text):
            target = match.group(1).split("#", 1)[0]
            if target.startswith("../"):
                resolved = (path.parent / target).resolve()
            else:
                resolved = DOCS / target
            if not resolved.exists():
                issues.append({"type": "broken_doc_link", "source": path.name, "target": match.group(1)})
    return issues


def main() -> int:
    issues = []
    issues.extend(check_files())
    issues.extend(check_pyproject())
    issues.extend(check_doc_links())
    status = "pass" if not issues else "fail"
    report = {
        "status": status,
        "issues": issues,
        "required_root": REQUIRED_ROOT,
        "required_docs": REQUIRED_DOCS,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
