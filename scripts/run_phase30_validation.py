from pathlib import Path
import subprocess, sys, json, tempfile, os

ROOT = Path(__file__).resolve().parents[1]
env = os.environ.copy()
env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")

def main():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        repo.mkdir()
        (repo / "app.py").write_text("def value():\n    return 1\n", encoding="utf-8")
        cmd = [sys.executable, "-m", "uacos.cli", "phase30-validate", "--repo", str(repo)]
        res = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, env=env, timeout=120)
        print(res.stdout)
        if res.stderr:
            print(res.stderr)
        out = ROOT / "phase30_validation_result.json"
        try:
            data = json.loads(res.stdout)
        except Exception:
            data = {"status": "parse_error", "stdout": res.stdout, "stderr": res.stderr}
        out.write_text(json.dumps({"returncode": res.returncode, "result": data}, ensure_ascii=False, indent=2), encoding="utf-8")
        print("PHASE30_VALIDATION_REPORT=", out)
        raise SystemExit(0 if res.returncode == 0 and data.get("status") == "pass" else 1)

if __name__ == "__main__":
    main()
