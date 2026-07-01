from pathlib import Path
import tempfile
import subprocess
import sys
import os
import json

ROOT = Path(__file__).resolve().parents[1]
env = os.environ.copy()
env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        (repo / "backend").mkdir(parents=True)
        (repo / "frontend").mkdir(parents=True)
        (repo / "backend" / "api.py").write_text("from fastapi import FastAPI\napp=FastAPI()\n@app.get('/api/users')\ndef list_users():\n    return []\n", encoding="utf-8")
        (repo / "frontend" / "dashboard.js").write_text("export async function loadUsers(){ return fetch('/api/users'); }\n", encoding="utf-8")
        cmds = [
            [sys.executable, "-m", "uacos.cli", "bootstrap", "--repo", str(repo)],
            [sys.executable, "-m", "uacos.cli", "js-ts-scan", "--repo", str(repo)],
            [sys.executable, "-m", "uacos.cli", "fullstack-index", "--repo", str(repo)],
            [sys.executable, "-m", "uacos.cli", "fullstack-impact", "--repo", str(repo), "--task", "fix /api/users dashboard"],
            [sys.executable, "-m", "uacos.cli", "fullstack-context", "--repo", str(repo), "--task", "fix /api/users dashboard"],
        ]
        results = []
        ok = True
        for cmd in cmds:
            res = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, env=env, timeout=120)
            results.append({"cmd": cmd, "returncode": res.returncode, "stdout": res.stdout[-3000:], "stderr": res.stderr[-1000:]})
            ok = ok and res.returncode == 0
        report = {"status": "pass" if ok else "fail", "results": results}
        out = ROOT / "phase32_validation_result.json"
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        raise SystemExit(0 if ok else 1)

if __name__ == "__main__":
    main()
