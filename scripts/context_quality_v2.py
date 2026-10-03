from __future__ import annotations

import argparse
import json
from pathlib import Path

from uacos.eval.context_quality import evaluate_manifest
from uacos.graph.builder import build_graph


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure UACOS context selection against explicit ground truth."
    )
    parser.add_argument("--repo", default=".")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", default="reports/context_quality_v2_report.json")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = repo_root / manifest_path
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    build_graph(repo_root)
    report = evaluate_manifest(repo_root, manifest)
    report["manifest"] = str(manifest_path)

    output = Path(args.output)
    if not output.is_absolute():
        output = repo_root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.summary:
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "task_count": report["task_count"],
                    "passed_task_count": report["passed_task_count"],
                    "pass_rate": report["pass_rate"],
                    "aggregate": report["aggregate"],
                    "output": str(output),
                },
                ensure_ascii=False,
            )
        )
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
