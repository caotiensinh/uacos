from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from uacos.auto.engine import run_auto_once, summarize_auto_report

if __name__ == "__main__":
    report = run_auto_once(ROOT)
    print(json.dumps(summarize_auto_report(report), ensure_ascii=False, indent=2))
    raise SystemExit(0 if report.get("status") == "pass" else 1)
