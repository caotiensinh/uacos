
from pathlib import Path
import subprocess
import sys
import json
import os
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
os.environ["PYTHONPATH"] = str(ROOT) + os.pathsep + os.environ.get("PYTHONPATH", "")
# Avoid unrelated environment warmup noise if honored by runtime.
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

PHASE29_TESTS = [
    "tests/test_phase19_ast_graph.py",
    "tests/test_phase20_patch_engine.py",
    "tests/test_phase21_24_provider_openclaw.py",
    "tests/test_phase22_budget_optimizer.py",
    "tests/test_phase26_compression.py",
    "tests/test_phase27_transaction.py",
    "tests/test_phase28_runtime.py",
    "tests/test_e2e_v3_user_flow.py",
]

def run_pytest():
    return subprocess.run([sys.executable, "-m", "pytest", "-q", *PHASE29_TESTS], cwd=ROOT, text=True, capture_output=True, timeout=300)

def run_fallback():
    code = """
import importlib.util, tempfile, pathlib, traceback, sys, os
root = pathlib.Path.cwd()
tests = [root / p for p in %r]
passed = 0
failed = []
for path in tests:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for name in dir(mod):
        if name.startswith('test_'):
            fn = getattr(mod, name)
            try:
                with tempfile.TemporaryDirectory() as td:
                    fn(pathlib.Path(td))
                passed += 1
                print('PASS', path.name, name)
            except Exception:
                failed.append((path.name, name, traceback.format_exc()))
                print('FAIL', path.name, name)
for f in failed:
    print('\\n--- FAILED:', f[0], f[1], '---')
    print(f[2])
print('SUMMARY passed=', passed, 'failed=', len(failed))
sys.exit(1 if failed else 0)
""" % PHASE29_TESTS
    return subprocess.run([sys.executable, "-c", code], cwd=ROOT, text=True, capture_output=True, timeout=300)

def main():
    # Compile targeted tests and uacos first.
    comp = subprocess.run([sys.executable, "-m", "compileall", "-q", "uacos", *PHASE29_TESTS], cwd=ROOT, text=True, capture_output=True, timeout=180)
    if comp.returncode != 0:
        report = {"mode": "compile", "returncode": comp.returncode, "stdout": comp.stdout, "stderr": comp.stderr}
        (ROOT / "test_results_phase29.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(comp.stdout)
        print(comp.stderr)
        raise SystemExit(comp.returncode)

    if importlib.util.find_spec("pytest") is not None:
        res = run_pytest()
        mode = "pytest-targeted"
        if res.returncode != 0:
            # Fallback runner gives direct traceback and avoids collection of inherited legacy tests.
            fb = run_fallback()
            if fb.returncode == 0:
                res = fb
                mode = "fallback-after-pytest"
    else:
        res = run_fallback()
        mode = "fallback"

    report = {"mode": mode, "returncode": res.returncode, "stdout": res.stdout, "stderr": res.stderr}
    out = ROOT / "test_results_phase29.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(res.stdout)
    if res.stderr:
        print(res.stderr)
    print("PHASE29_TEST_MODE=", mode)
    print("PHASE29_TEST_REPORT=", out)
    raise SystemExit(res.returncode)

if __name__ == "__main__":
    main()
