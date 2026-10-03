from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys

from uacos.agent.real_e2e import run_real_provider_matrix


PROVIDERS = ("codex", "claude_code", "goose")
ENV_ARGV = {
    "codex": "UACOS_CODEX_ARGV_JSON",
    "claude_code": "UACOS_CLAUDE_CODE_ARGV_JSON",
    "goose": "UACOS_GOOSE_ARGV_JSON",
}
EXECUTABLE = {"codex": "codex", "claude_code": "claude", "goose": "goose"}


def _load_argv(provider: str) -> list[str] | None:
    raw = os.environ.get(ENV_ARGV[provider], "").strip()
    if not raw:
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid {ENV_ARGV[provider]}: {exc}") from exc
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise SystemExit(f"{ENV_ARGV[provider]} must be a non-empty JSON string array")
    return value


def _prepare_case(root: Path, provider: str, argv: list[str]) -> tuple[Path, dict]:
    workspace = root / provider
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
    case = {
        "provider": provider,
        "argv": argv,
        "task": "Change only app.py so VALUE becomes 2. Return a unified diff only.",
        "allowed_files": ["app.py"],
        "tests": [f"{sys.executable} -c \"from pathlib import Path; assert 'VALUE = 2' in Path('app.py').read_text()\""],
        "max_iterations": 2,
        "timeout_seconds": 180,
    }
    return workspace, case


def main() -> int:
    parser = argparse.ArgumentParser(description="Run or probe real coding-agent E2E cases on a self-hosted runner.")
    parser.add_argument("--output", default="reports/real-agent-e2e/summary.json")
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    workspace_root = output.parent / "workspaces"
    workspace_root.mkdir(parents=True, exist_ok=True)

    probes = []
    executed = []
    configured = 0
    for provider in PROVIDERS:
        resolved = shutil.which(EXECUTABLE[provider])
        argv = _load_argv(provider)
        probes.append({
            "provider": provider,
            "executable": EXECUTABLE[provider],
            "resolved_path": resolved,
            "binary_available": bool(resolved),
            "argv_configured": bool(argv),
            "argv_env": ENV_ARGV[provider],
        })
        if not argv:
            continue
        configured += 1
        workspace, case = _prepare_case(workspace_root, provider, argv)
        result = run_real_provider_matrix(workspace, [case])
        executed.extend(result["results"])

    passed = sum(1 for row in executed if row.get("status") == "passed")
    summary = {
        "status": "pass" if executed and passed == len(executed) else "incomplete",
        "probes": probes,
        "configured_count": configured,
        "executed_count": len(executed),
        "passed_count": passed,
        "results": executed,
        "claim": "Binary presence or fixture tests are not real-provider PASS. Only executed configured provider rows with status=passed count as E2E success.",
    }
    output.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))
    if args.require_pass and (not executed or passed != len(executed)):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
