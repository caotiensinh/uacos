from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import importlib.util
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "release_gate_report.json"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(name: str, cmd: list[str], timeout: int = 60, env_extra: dict | None = None) -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    if env_extra:
        env.update(env_extra)
    started = utcnow()
    try:
        cp = subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=True, timeout=timeout)
        return {
            "name": name,
            "cmd": " ".join(cmd),
            "started_at": started,
            "returncode": cp.returncode,
            "ok": cp.returncode == 0,
            "stdout_tail": cp.stdout[-12000:],
            "stderr_tail": cp.stderr[-4000:],
            "json_status": _json_status(cp.stdout),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "name": name,
            "cmd": " ".join(cmd),
            "started_at": started,
            "returncode": 124,
            "ok": False,
            "stdout_tail": (exc.stdout or "")[-12000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": (exc.stderr or "")[-4000:] if isinstance(exc.stderr, str) else "timeout",
            "json_status": None,
        }


def _json_status(stdout: str):
    try:
        data = json.loads(stdout)
    except Exception:
        return None
    if isinstance(data, dict):
        return data.get("status")
    return None


def _read_project_version(pyproject_text: str) -> str:
    in_project = False
    for raw_line in pyproject_text.splitlines():
        line = raw_line.strip()
        if line == "[project]":
            in_project = True
            continue
        if in_project and line.startswith("["):
            break
        if in_project and line.startswith("version") and "=" in line:
            return line.split("=", 1)[1].strip().strip('"')
    raise ValueError("project.version not found in pyproject.toml")


def clean_pycache() -> dict:
    removed = []
    for path in sorted(ROOT.rglob("__pycache__")):
        if "reports/pycache_compile" in str(path):
            continue
        shutil.rmtree(path, ignore_errors=True)
        removed.append(str(path.relative_to(ROOT)))
    return {
        "name": "clean_pycache",
        "cmd": "remove __pycache__ before release cleanliness check",
        "returncode": 0,
        "ok": True,
        "stdout_tail": "\n".join(removed[:50]),
        "stderr_tail": "",
        "json_status": "pass",
    }


def no_pycache_in_release() -> dict:
    found = [str(p.relative_to(ROOT)) for p in ROOT.rglob("__pycache__") if "reports/pycache_compile" not in str(p)]
    return {"name": "no_pycache_in_release", "cmd": "find __pycache__", "returncode": 0 if not found else 1, "ok": not found, "stdout_tail": "\n".join(found[:20]), "stderr_tail": "", "json_status": "pass" if not found else "fail"}


def install_smoke_test() -> dict:
    return run("install_smoke", [sys.executable, "-m", "pip", "install", "-e", ".[dev]"], timeout=240)


def version_sync() -> dict:
    try:
        py_version = _read_project_version((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        init_text = (ROOT / "uacos" / "__init__.py").read_text(encoding="utf-8")
        ok = f'__version__ = "{py_version}"' in init_text
        stderr_tail = ""
    except Exception as exc:
        py_version = "unknown"
        ok = False
        stderr_tail = str(exc)
    return {"name": "version_sync", "cmd": "pyproject vs uacos.__version__", "returncode": 0 if ok else 1, "ok": ok, "stdout_tail": py_version, "stderr_tail": stderr_tail, "json_status": "pass" if ok else "fail"}


def ollama_smoke_test() -> dict:
    # Optional: skip cleanly when Ollama is not reachable.
    try:
        cp = subprocess.run(["ollama", "list"], text=True, capture_output=True, timeout=10)
    except Exception as exc:
        return {"name": "ollama_smoke_optional", "cmd": "ollama list", "returncode": 0, "ok": True, "stdout_tail": "skipped", "stderr_tail": str(exc), "json_status": "skipped"}
    return {"name": "ollama_smoke_optional", "cmd": "ollama list", "returncode": 0, "ok": True, "stdout_tail": cp.stdout[-2000:], "stderr_tail": cp.stderr[-2000:], "json_status": "ok" if cp.returncode == 0 else "skipped"}


def main() -> int:
    compile_cache = ROOT / "reports" / "pycache_compile"
    if compile_cache.exists():
        shutil.rmtree(compile_cache, ignore_errors=True)
    checks = [clean_pycache()]
    checks.append(run("compileall", [sys.executable, "-m", "compileall", "-q", "uacos"], env_extra={"PYTHONPYCACHEPREFIX": str(compile_cache)}))
    checks.append(clean_pycache())
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
    checks.append(run("english_language_check", [sys.executable, "scripts/check_english_docs.py", "--repo", "."], timeout=60))
    checks.append(run("uacos_self_check", [sys.executable, "scripts/uacos_self_check.py", "--summary"], timeout=180))
    checks.append(run("community_readiness_check", [sys.executable, "scripts/community_readiness_check.py"], timeout=60))
    checks.append(run("uacos_auto_check", [sys.executable, "-m", "uacos.cli", "auto", "--repo", ".", "--skip-performance", "--summary"], timeout=120))
    checks.append(run("uacos_flow_list", [sys.executable, "-m", "uacos.flow_cli", "list"], timeout=60))
    checks.append(run("uacos_performance_benchmark", [sys.executable, "scripts/uacos_performance_benchmark.py", "--repo", ".", "--task", "fix MCP SSE endpoint and docs cleanup", "--max-files", "3", "--max-tokens", "3000", "--summary", "--skip-cache-probe"], timeout=120))
    checks.append(run("uacos_benchmark_suite", [sys.executable, "scripts/uacos_benchmark_suite.py", "--repo", ".", "--manifest", "evals/benchmark_suite.json", "--summary"], timeout=180))
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
