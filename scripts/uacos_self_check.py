from __future__ import annotations

from pathlib import Path
import json
import os
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "uacos_self_check_report.json"


CHECKS = [
    ("uacos --help", ["uacos", "--help"]),
    ("uacos init --repo . --skip-performance", ["uacos", "init", "--repo", ".", "--skip-performance"]),
    ("uacos bootstrap --repo .", ["uacos", "bootstrap", "--repo", "."]),
    ("uacos graph-build --repo .", ["uacos", "graph-build", "--repo", "."]),
    ("uacos impact --repo . --task \"fix MCP SSE endpoint and docs cleanup\"", ["uacos", "impact", "--repo", ".", "--task", "fix MCP SSE endpoint and docs cleanup"]),
    ("uacos llm-run-real --repo . --task \"analyze repo quality\" --size small", ["uacos", "llm-run-real", "--repo", ".", "--task", "analyze repo quality", "--size", "small"]),
    ("uacos cache-status", ["uacos", "cache-status"]),
    ("uacos skill35-status --repo .", ["uacos", "skill35-status", "--repo", "."]),
]


def _tail(value: str, limit: int = 4000) -> str:
    return (value or "")[-limit:]


def _command(argv: list[str]) -> list[str]:
    exe = shutil.which(argv[0])
    if exe:
        return [exe, *argv[1:]]
    if argv[0] == "uacos":
        return [sys.executable, "-m", "uacos.cli", *argv[1:]]
    return argv


def _json_status(stdout: str):
    text = (stdout or "").strip()
    if not text or not text.startswith("{"):
        return None
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data.get("status")


def run_check(name: str, argv: list[str]) -> dict:
    cmd = _command(argv)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    try:
        proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=180, env=env)
        json_status = _json_status(proc.stdout)
        ok = proc.returncode == 0 and json_status != "error"
        return {
            "name": name,
            "cmd": " ".join(argv),
            "actual_cmd": " ".join(cmd),
            "returncode": proc.returncode,
            "ok": ok,
            "stdout_tail": _tail(proc.stdout),
            "stderr_tail": _tail(proc.stderr),
            "json_status": json_status,
        }
    except Exception as exc:
        return {
            "name": name,
            "cmd": " ".join(argv),
            "actual_cmd": " ".join(cmd),
            "returncode": -1,
            "ok": False,
            "stdout_tail": "",
            "stderr_tail": f"{type(exc).__name__}: {exc}",
            "json_status": None,
        }


def summarize_report(report: dict) -> dict:
    tests = report.get("tests", [])
    return {
        "status": report.get("status"),
        "test_count": len(tests),
        "failed": [t.get("name") for t in tests if not t.get("ok")],
        "json_statuses": {t.get("name"): t.get("json_status") for t in tests},
        "report_file": str(REPORT),
    }


def main() -> int:
    summary = "--summary" in sys.argv
    tests = [run_check(name, argv) for name, argv in CHECKS]
    status = "pass" if all(t["ok"] for t in tests) else "fail"
    report = {"status": status, "tests": tests}
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summarize_report(report) if summary else report, ensure_ascii=False, indent=2))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
