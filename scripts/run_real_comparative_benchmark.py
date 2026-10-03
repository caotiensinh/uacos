from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil

from uacos.benchmarks.real_provider import run_real_comparative_suite


ARGV_ENV = {
    "codex": "UACOS_CODEX_ARGV_JSON",
    "claude_code": "UACOS_CLAUDE_CODE_ARGV_JSON",
    "goose": "UACOS_GOOSE_ARGV_JSON",
}
EXECUTABLE = {"codex": "codex", "claude_code": "claude", "goose": "goose"}


def _load_argv(provider: str) -> list[str]:
    env_name = ARGV_ENV.get(provider)
    if not env_name:
        raise SystemExit(f"unsupported provider: {provider}")
    raw = os.environ.get(env_name, "").strip()
    if not raw:
        raise SystemExit(f"{env_name} is required")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid {env_name}: {exc}") from exc
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise SystemExit(f"{env_name} must be a non-empty JSON string array")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run real-provider full_repo vs grep vs UACOS comparisons with repeated isolated workspaces."
    )
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--provider", choices=sorted(ARGV_ENV), required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output-dir", default="reports/real-comparative")
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()

    executable = EXECUTABLE[args.provider]
    resolved = shutil.which(executable)
    if not resolved:
        print(json.dumps({"status": "unavailable", "provider": args.provider, "reason": "provider_executable_unavailable"}, indent=2))
        return 2

    argv = _load_argv(args.provider)
    if Path(argv[0]).name != executable:
        raise SystemExit(f"provider executable mismatch: expected {executable}, got {Path(argv[0]).name}")

    manifest_path = Path(args.manifest).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = run_real_comparative_suite(
        manifest,
        provider=args.provider,
        argv=argv,
        model=args.model,
        output_dir=Path(args.output_dir),
    )
    summary = {
        "status": result["status"],
        "provider": args.provider,
        "model": args.model,
        "report": result["report_path"],
        "observations": result["observations_path"],
        "evidence": result["evidence_path"],
        "claim": "A real comparative PASS still depends on the evaluator targets and archived provider execution evidence. Token source is recorded per observation.",
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.require_pass and result["status"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
