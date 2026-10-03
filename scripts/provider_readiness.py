from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil


PROVIDERS = {
    "codex": {"executable": "codex", "argv_env": "UACOS_CODEX_ARGV_JSON", "auth_envs": ["OPENAI_API_KEY", "CODEX_API_KEY"]},
    "claude_code": {"executable": "claude", "argv_env": "UACOS_CLAUDE_CODE_ARGV_JSON", "auth_envs": ["ANTHROPIC_API_KEY"]},
    "goose": {"executable": "goose", "argv_env": "UACOS_GOOSE_ARGV_JSON", "auth_envs": []},
}


def evaluate_provider_readiness(env: dict[str, str] | None = None) -> dict:
    env = dict(os.environ if env is None else env)
    rows = []
    for name, cfg in PROVIDERS.items():
        resolved = shutil.which(cfg["executable"])
        argv_raw = env.get(cfg["argv_env"], "").strip()
        argv_valid = False
        if argv_raw:
            try:
                parsed = json.loads(argv_raw)
            except json.JSONDecodeError:
                parsed = None
            argv_valid = isinstance(parsed, list) and bool(parsed) and all(isinstance(item, str) and item for item in parsed)
        auth_present = any(bool(env.get(key, "").strip()) for key in cfg["auth_envs"])
        blockers = []
        if not resolved:
            blockers.append("binary_missing")
        if not argv_valid:
            blockers.append("argv_not_configured")
        if cfg["auth_envs"] and not auth_present:
            blockers.append("auth_not_detected")
        rows.append({
            "provider": name,
            "executable": cfg["executable"],
            "resolved_path": resolved,
            "binary_available": bool(resolved),
            "argv_env": cfg["argv_env"],
            "argv_configured": argv_valid,
            "auth_envs_checked": list(cfg["auth_envs"]),
            "auth_detected": auth_present if cfg["auth_envs"] else None,
            "ready_for_real_e2e": not blockers,
            "blockers": blockers,
        })
    ready = [row["provider"] for row in rows if row["ready_for_real_e2e"]]
    return {
        "status": "pass" if ready else "incomplete",
        "ready_providers": ready,
        "providers": rows,
        "claim": "Readiness only means binary/argv/auth prerequisites appear present. It is not a real-provider E2E PASS.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose real coding-agent provider readiness without exposing secret values.")
    parser.add_argument("--output", default="reports/provider_readiness.json")
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()

    report = evaluate_provider_readiness()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if (report["status"] == "pass" or not args.require_ready) else 2


if __name__ == "__main__":
    raise SystemExit(main())
