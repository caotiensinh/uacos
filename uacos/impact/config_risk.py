from __future__ import annotations

from pathlib import Path
import re

SKIP_DIRS = {".git", ".uacos", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build", "reports"}
CONFIG_NAMES = {
    ".env",
    ".env.example",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "nginx.conf",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "poetry.lock",
    "alembic.ini",
}
CONFIG_EXTS = {".yaml", ".yml", ".json", ".toml", ".ini", ".conf", ".env"}
DEPLOY_PATH_HINTS = (".github/workflows", "deploy", "deployment", "k8s", "kubernetes", "helm", "docker", "nginx", "terraform", "ansible", "alembic", "migrations")
SECRET_RE = re.compile(r"(?i)(secret|password|passwd|token|api[_-]?key|private[_-]?key|access[_-]?key|credential)")
NETWORK_RE = re.compile(r"(?i)(host|port|url|uri|endpoint|proxy|origin|cors|domain|listen|server_name)")
DB_RE = re.compile(r"(?i)(database|postgres|mysql|sqlite|redis|mongo|dsn|alembic|migration)")
CI_RE = re.compile(r"(?i)(github actions|workflow|release|deploy|publish|docker|pytest|npm test|build)")


def _safe_rel(path: Path, repo_root: Path) -> str:
    return str(path.relative_to(repo_root)).replace("\\", "/")


def _skip(path: Path, repo_root: Path) -> bool:
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        return True
    return any(part in SKIP_DIRS for part in rel.parts)


def is_config_or_deploy_file(path: Path, repo_root: Path) -> bool:
    if not path.is_file() or _skip(path, repo_root):
        return False
    rel = _safe_rel(path, repo_root).lower()
    name = path.name.lower()
    if name in CONFIG_NAMES:
        return True
    if any(hint in rel for hint in DEPLOY_PATH_HINTS):
        return True
    return path.suffix.lower() in CONFIG_EXTS and any(token in rel for token in ("config", "settings", "deploy", "service", "docker", "workflow"))


def classify_config_file(path: Path, repo_root: Path) -> dict:
    rel = _safe_rel(path, repo_root)
    name = path.name.lower()
    try:
        text = path.read_text(encoding="utf-8", errors="replace")[:300000]
    except OSError:
        text = ""
    low_rel = rel.lower()
    categories: list[str] = []
    findings: list[str] = []

    if name.startswith(".env") or SECRET_RE.search(text) or SECRET_RE.search(rel):
        categories.append("secret_or_environment_config")
        findings.append("contains secret/environment style keys or path hints")
    if "docker" in low_rel or name == "dockerfile" or "compose" in name:
        categories.append("container_runtime")
        findings.append("affects Docker/container runtime behavior")
    if ".github/workflows" in low_rel or CI_RE.search(text):
        categories.append("ci_release_pipeline")
        findings.append("affects CI, release, deploy, build, or test automation")
    if "k8s" in low_rel or "kubernetes" in low_rel or "helm" in low_rel:
        categories.append("orchestration_deploy")
        findings.append("affects Kubernetes/Helm deployment behavior")
    if name in {"pyproject.toml", "requirements.txt", "requirements-dev.txt", "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock"}:
        categories.append("dependency_surface")
        findings.append("affects dependency resolution or packaging")
    if DB_RE.search(text) or "migration" in low_rel or "alembic" in low_rel:
        categories.append("database_or_migration")
        findings.append("affects database configuration or schema/migration behavior")
    if NETWORK_RE.search(text) or "nginx" in low_rel:
        categories.append("network_runtime")
        findings.append("affects host/port/proxy/CORS/endpoint/network runtime behavior")

    if not categories:
        categories.append("general_config")
        findings.append("configuration file with no high-risk signal detected")

    high_risk = {"secret_or_environment_config", "ci_release_pipeline", "database_or_migration", "orchestration_deploy"}
    medium_risk = {"container_runtime", "dependency_surface", "network_runtime"}
    if any(cat in high_risk for cat in categories):
        risk_level = "high"
    elif any(cat in medium_risk for cat in categories):
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "file": rel,
        "risk_level": risk_level,
        "categories": sorted(set(categories)),
        "findings": sorted(set(findings)),
        "line_count": text.count("\n") + 1 if text else 0,
    }


def build_config_risk_map(repo_root: Path, selected_files: list[dict] | None = None, max_entries: int = 200) -> dict:
    selected = {item.get("file") or item.get("path") for item in selected_files or [] if item.get("file") or item.get("path")}
    rows = []
    for path in sorted(repo_root.rglob("*")):
        if is_config_or_deploy_file(path, repo_root):
            row = classify_config_file(path, repo_root)
            row["in_selected_context"] = row["file"] in selected
            rows.append(row)

    high = [row for row in rows if row["risk_level"] == "high"]
    medium = [row for row in rows if row["risk_level"] == "medium"]
    selected_risks = [row for row in rows if row["in_selected_context"]]
    recommended_review = []
    if high:
        recommended_review.append("human_review_required_for_high_risk_config")
    if selected_risks:
        recommended_review.append("explain_selected_config_runtime_impact_before_patch")
    if any("secret_or_environment_config" in row["categories"] for row in rows):
        recommended_review.append("verify_no_real_secret_values_are_added_or_exposed")

    return {
        "status": "ok",
        "config_file_count": len(rows),
        "high_risk_count": len(high),
        "medium_risk_count": len(medium),
        "selected_context_config_risks": selected_risks[:max_entries],
        "config_files": rows[:max_entries],
        "recommended_review": recommended_review,
        "claim": "Config/deployment risk map is heuristic. It identifies files that may affect runtime/deploy/security, but it does not prove production impact.",
    }
