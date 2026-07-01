from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import zipfile


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "release_gate_report.json"
BUILD_CLEAN_RELEASE = ROOT / "scripts" / "build_clean_release.py"


def _tail(value: str, limit: int = 4000) -> str:
    return (value or "")[-limit:]


def _json_status(stdout: str):
    text = (stdout or "").strip()
    if not text or not text.startswith("{"):
        return None
    try:
        return json.loads(text).get("status")
    except Exception:
        return None


def run(name: str, cmd: list[str], timeout: int = 180, env_extra: dict | None = None) -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    if env_extra:
        env.update(env_extra)
    try:
        proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired as exc:
        return {
            "name": name,
            "cmd": " ".join(cmd),
            "returncode": 124,
            "ok": False,
            "stdout_tail": _tail(exc.stdout if isinstance(exc.stdout, str) else ""),
            "stderr_tail": _tail(exc.stderr if isinstance(exc.stderr, str) else ""),
            "json_status": "timeout",
            "timeout_seconds": timeout,
        }
    json_status = _json_status(proc.stdout)
    ok = proc.returncode == 0 and json_status not in {"error", "fail", "timeout"}
    return {
        "name": name,
        "cmd": " ".join(cmd),
        "returncode": proc.returncode,
        "ok": ok,
        "stdout_tail": _tail(proc.stdout),
        "stderr_tail": _tail(proc.stderr),
        "json_status": json_status,
    }


def parse_version_from_pyproject(path: Path) -> str:
    import re

    text = path.read_text(encoding="utf-8")
    project_section = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("["):
            project_section = stripped == "[project]"
            continue
        if project_section and stripped.startswith("version"):
            match = re.search(r"^version\s*=\s*['\"]([^'\"]+)['\"]", stripped)
            if match:
                return match.group(1)
    raise ValueError("Could not read project.version from pyproject.toml")


def no_pycache_in_release() -> dict:
    cmd = [sys.executable, str(BUILD_CLEAN_RELEASE), "--repo", str(ROOT)]
    check = run("no_pycache_in_release", cmd, timeout=180)
    check["cmd"] = " ".join([sys.executable, str(BUILD_CLEAN_RELEASE), "--repo", "."])
    if check["returncode"] != 0:
        check["ok"] = False
        check["json_status"] = "fail"
    return check


def install_smoke_test() -> dict:
    cmd = ["sh", str(ROOT / "scripts" / "install_smoke_test.sh")]
    check = run("install_smoke_test", cmd, timeout=300)
    if check["returncode"] != 0:
        check["ok"] = False
        check["json_status"] = "fail"
    return check


def version_sync() -> dict:
    py_version = parse_version_from_pyproject(ROOT / "pyproject.toml")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    first_header = None
    for line in changelog.splitlines():
        if line.startswith("## "):
            first_header = line[3:].strip()
            break
    ok = first_header == py_version
    return {
        "name": "version_sync",
        "cmd": f"read version from pyproject.toml and compare to CHANGELOG.md first header",
        "returncode": 0 if ok else 1,
        "ok": ok,
        "stdout_tail": f"pyproject={py_version} changelog={first_header}",
        "stderr_tail": "",
        "json_status": "pass" if ok else "fail",
    }


def ollama_smoke_test() -> dict:
    url = "http://localhost:11434/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            reachable = 200 <= int(response.status) < 500
    except (urllib.error.URLError, TimeoutError, OSError):
        return {
            "name": "ollama_smoke_test",
            "cmd": f"GET {url}",
            "returncode": 0,
            "ok": True,
            "stdout_tail": "Ollama not reachable; skipped",
            "stderr_tail": "",
            "json_status": "skipped_no_ollama",
        }
    if not reachable:
        return {
            "name": "ollama_smoke_test",
            "cmd": f"GET {url}",
            "returncode": 0,
            "ok": True,
            "stdout_tail": "Ollama not reachable; skipped",
            "stderr_tail": "",
            "json_status": "skipped_no_ollama",
        }
    check = run("ollama_smoke_test", [sys.executable, "-m", "uacos.cli", "llm33-probe", "--repo", ".", "--provider", "ollama_lan"], timeout=30)
    check["ok"] = check["returncode"] == 0 and check["json_status"] == "ok"
    return check


def main() -> int:
    compile_cache = ROOT / "reports" / "pycache_compile"
    if compile_cache.exists():
        shutil.rmtree(compile_cache, ignore_errors=True)
    checks = [run("compileall", [sys.executable, "-m", "compileall", "-q", "uacos"], env_extra={"PYTHONPYCACHEPREFIX": str(compile_cache)})]
    checks.append(no_pycache_in_release())
    checks.append(install_smoke_test())
    checks.append(version_sync())
    if importlib.util.find_spec("pytest") is not None:
        checks.append(run("pytest", [sys.executable, "-m", "pytest", "-q"], timeout=240))
    else:
        checks.append({
            "name": "pytest",
            "cmd": f"{sys.executable} -m pytest -q",
            "returncode": 0,
            "ok": True,
            "stdout_tail": "pytest not installed; skipped",
            "stderr_tail": "",
            "json_status": None,
        })
    checks.append(run("uacos_self_check", [sys.executable, "scripts/uacos_self_check.py", "--summary"], timeout=180))
    checks.append(run("community_readiness_check", [sys.executable, "scripts/community_readiness_check.py"], timeout=60))
    checks.append(run("uacos_auto_check", [sys.executable, "-m", "uacos.cli", "auto", "--repo", ".", "--skip-performance", "--summary"], timeout=120))
    checks.append(run("uacos_performance_benchmark", [sys.executable, "scripts/uacos_performance_benchmark.py", "--repo", ".", "--task", "fix MCP SSE endpoint and docs cleanup", "--max-files", "3", "--max-tokens", "3000", "--summary", "--skip-cache-probe"], timeout=120))
    checks.append(run("eval_dry_run", [sys.executable, "scripts/eval_run.py", "--repo", ".", "--golden", "evals/golden_tasks.json"], timeout=120))
    checks.append(ollama_smoke_test())
    status = "pass" if all(c["ok"] for c in checks) else "fail"
    report = {"status": status, "checks": checks}
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
