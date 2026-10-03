from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile

from uacos.agent.real_e2e import run_real_provider_e2e


ARGV_ENV = {
    "codex": "UACOS_CODEX_ARGV_JSON",
    "claude_code": "UACOS_CLAUDE_CODE_ARGV_JSON",
    "goose": "UACOS_GOOSE_ARGV_JSON",
}


def _argv(provider: str) -> list[str]:
    raw = os.environ.get(ARGV_ENV[provider], "").strip()
    if not raw:
        raise SystemExit(f"{ARGV_ENV[provider]} is required")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid {ARGV_ENV[provider]}: {exc}") from exc
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise SystemExit(f"{ARGV_ENV[provider]} must be a non-empty JSON string array")
    return value


def _copy_repo(source: Path, destination: Path) -> None:
    def ignore(_path: str, names: list[str]):
        ignored = {".git", ".uacos", "__pycache__", ".pytest_cache"}
        return [name for name in names if name in ignored]

    shutil.copytree(source, destination, ignore=ignore)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one real-provider UACOS smoke E2E from the first comparative-manifest task.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--provider", choices=sorted(ARGV_ENV), required=True)
    parser.add_argument("--output", default="reports/real-agent-e2e/summary.json")
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    tasks = manifest.get("tasks") or []
    if not tasks:
        raise SystemExit("manifest requires at least one task")
    task = tasks[0]
    source = Path(str(task.get("repo") or "")).resolve()
    if not source.is_dir():
        raise SystemExit(f"task repo unavailable: {source}")

    with tempfile.TemporaryDirectory(prefix="uacos-real-e2e-") as temp:
        workspace = Path(temp) / "repo"
        _copy_repo(source, workspace)
        result = run_real_provider_e2e(
            workspace,
            args.provider,
            _argv(args.provider),
            str(task.get("task") or ""),
            allowed_files=list(task.get("allowed_files") or []),
            allowed_dirs=list(task.get("allowed_dirs") or []),
            tests=list(task.get("tests") or []),
            max_iterations=int(task.get("max_iterations", 2)),
            timeout_seconds=int(task.get("timeout_seconds", 180)),
        )

    passed = result.get("status") == "passed"
    summary = {
        "status": "pass" if passed else "incomplete",
        "provider": args.provider,
        "configured_count": 1,
        "executed_count": 1 if result.get("status") != "unavailable" else 0,
        "passed_count": 1 if passed else 0,
        "results": [result],
        "claim": "This report is produced only by an actual provider CLI invocation routed through UACOS safe execution; unavailable providers are never counted as PASS.",
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))
    if args.require_pass and not passed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
