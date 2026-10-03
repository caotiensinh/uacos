from __future__ import annotations

import argparse
import json
from pathlib import Path

from uacos.benchmarks.comparative import BenchmarkThresholds, evaluate_comparative_benchmark


def main() -> int:
    parser = argparse.ArgumentParser(description="Score full-repo vs grep vs UACOS benchmark observations against hidden ground truth.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--observations", required=True)
    parser.add_argument("--report", default="reports/comparative_ground_truth_benchmark.json")
    parser.add_argument("--min-required-symbol-recall", type=float, default=0.95)
    parser.add_argument("--max-noise-rate", type=float, default=0.20)
    parser.add_argument("--min-repeats", type=int, default=3)
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    observations = json.loads(Path(args.observations).read_text(encoding="utf-8"))
    report = evaluate_comparative_benchmark(
        manifest,
        observations,
        thresholds=BenchmarkThresholds(
            min_required_symbol_recall=args.min_required_symbol_recall,
            max_noise_rate=args.max_noise_rate,
            min_repeats=args.min_repeats,
        ),
    )
    out = Path(args.report)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"status": report["status"], "findings": report["findings"], "target_checks": report["target_checks"], "report": str(out)}, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
