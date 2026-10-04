from __future__ import annotations

import argparse
import json
import os
import shlex
import tempfile
import time
from pathlib import Path

from uacos.agent.provider_profiles import create_provider_adapter
from uacos.agent.safe_execution import run_safe_agent_execution
from uacos.benchmarks.jev_ab import evaluate_jev_ab
from uacos.benchmarks.real_provider import ContextOverrideAdapter, build_mode_context
from uacos.judgment.jev import JevJudgmentProvider
from uacos.judgment.protocol import JudgmentRequest
from uacos.judgment.typesafe_http import TypeSafeSystemOneJevTransport
from uacos.llm.hardened import estimate_tokens


ARGV_ENVS = {
    "codex": "UACOS_CODEX_ARGV_JSON",
    "claude_code": "UACOS_CLAUDE_CODE_ARGV_JSON",
    "goose": "UACOS_GOOSE_ARGV_JSON",
}


def _provider_argv(provider: str) -> list[str]:
    env_name = ARGV_ENVS.get(provider)
    if not env_name:
        raise ValueError(f"unsupported_provider:{provider}")
    raw = os.environ.get(env_name, "").strip()
    if not raw:
        raise ValueError(f"provider_argv_missing:{provider}")
    parsed = json.loads(raw)
    if not isinstance(parsed, list) or not parsed or not all(isinstance(item, str) and item for item in parsed):
        raise ValueError(f"provider_argv_invalid:{provider}")
    return parsed


def _model_from_argv(argv: list[str]) -> str:
    for index, item in enumerate(argv):
        if item in {"--model", "-m"} and index + 1 < len(argv):
            value = argv[index + 1].strip()
            if value:
                return value
        if item.startswith("--model=") and item.split("=", 1)[1].strip():
            return item.split("=", 1)[1].strip()
    explicit = os.environ.get("UACOS_JEV_BENCHMARK_MODEL", "").strip()
    if explicit:
        return explicit
    raise ValueError("exact_provider_model_unavailable")


def _typesafe_key() -> str:
    value = os.environ.get("UACOS_TYPESAFE_API_KEY", "").strip() or os.environ.get("TYPESAFE_API_KEY", "").strip()
    if not value:
        raise ValueError("typesafe_api_key_missing")
    return value


def _write_fixture(root: Path) -> None:
    (root / "math_ops.py").write_text(
        "def add(a: int, b: int) -> int:\n    # BUG: addition must not subtract.\n    return a - b\n",
        encoding="utf-8",
    )
    (root / "service.py").write_text(
        "from math_ops import add\n\ndef invoice_total(subtotal: int, tax: int) -> int:\n    return add(subtotal, tax)\n",
        encoding="utf-8",
    )
    (root / "noise.py").write_text(
        "def add_noise(a: int, b: int) -> int:\n    return a + b + 1000\n\n"
        "NOTES = 'add add add invoice total arithmetic helper unrelated benchmark noise'\n",
        encoding="utf-8",
    )
    tests = root / "tests"
    tests.mkdir()
    (tests / "test_math_ops.py").write_text(
        "from math_ops import add\n\ndef test_add():\n    assert add(7, 5) == 12\n",
        encoding="utf-8",
    )


def _provider_metrics(execution: dict, context_tokens: int) -> tuple[int, int]:
    harness = execution.get("harness") or {}
    attempts = harness.get("attempts") or []
    winning = (attempts[-1].get("adapter_result") if attempts else {}) or {}
    tokens_in = int(winning.get("tokens_in") or 0)
    tokens_out = int(winning.get("tokens_out") or 0)
    if not tokens_in:
        tokens_in = context_tokens
    if not tokens_out:
        tokens_out = estimate_tokens(str(winning.get("output") or ""))
    return tokens_in + tokens_out, int((harness.get("metrics") or {}).get("elapsed_ms") or 0)


def _ranking_quality(selected: dict, candidates: list[dict]) -> float:
    target = "math_ops.py"
    if target not in set(selected.get("selected_files") or []):
        return 0.0
    eligible = [row for row in candidates if target in set(row.get("selected_files") or [])]
    if not eligible:
        return 0.0
    minimum = min(int(row.get("input_tokens_est") or 0) for row in eligible)
    selected_tokens = int(selected.get("input_tokens_est") or 0)
    return 1.0 if selected_tokens == minimum else 0.5


def _jev_token_estimate(request: JudgmentRequest, result: dict) -> int:
    # TypeSafe usage shape may vary. Keep token accounting comparable and fail-safe by
    # adding a transparent conservative request/response estimate rather than claiming zero.
    payload = json.dumps(request.to_dict(), sort_keys=True, default=str)
    response = json.dumps(result, sort_keys=True, default=str)
    return estimate_tokens(payload) + estimate_tokens(response)


def _run_one(*, provider: str, argv: list[str], model: str, mode: str, repeat: int, api_key: str) -> tuple[dict, dict]:
    task = "Fix math_ops.add so it performs addition. Change only math_ops.py and make pytest -q pass."
    with tempfile.TemporaryDirectory(prefix=f"uacos-jev-{mode}-{repeat}-") as tmp:
        root = Path(tmp) / "repo"
        root.mkdir()
        _write_fixture(root)
        uacos_context = build_mode_context(root, task, "uacos", max_files=4, max_chars=12000)
        grep_context = build_mode_context(root, task, "grep", max_files=4, max_chars=12000)
        candidates = [uacos_context, grep_context]
        selected = uacos_context
        fallback_used = False
        jev_latency_ms = 0
        jev_tokens = 0
        judgment_dict: dict = {"provider": "disabled", "status": "off", "ranking": ["uacos"]}

        if mode == "jev_on":
            rows = []
            for context in candidates:
                rows.append({
                    "candidate_id": context["mode"],
                    "mode": context["mode"],
                    "selected_files": context["selected_files"],
                    "input_tokens_est": context["input_tokens_est"],
                    "context_excerpt": context["content"][:8000],
                })
            request = JudgmentRequest(
                question="Choose the smallest repository context that contains sufficient evidence to fix the stated coding task correctly.",
                candidates=rows,
                evidence=[{"task": task, "allowed_files": ["math_ops.py"], "required_test": "pytest -q"}],
                task_id="JEV-E2E-MATH-ADD",
                run_id=f"jev-on-{repeat}",
                metadata={"benchmark": "p3.14-real-jev-ab"},
            )
            provider_obj = JevJudgmentProvider(TypeSafeSystemOneJevTransport(api_key), timeout_seconds=20.0)
            started = time.monotonic()
            judgment = provider_obj.judge(request)
            jev_latency_ms = max(1, int((time.monotonic() - started) * 1000))
            judgment_dict = judgment.to_dict()
            fallback_used = bool(judgment.fallback_used)
            if judgment.status != "ok" or fallback_used:
                raise RuntimeError(f"live_jev_unavailable:{judgment.metadata.get('jev_fallback_reason', judgment.status)}")
            if not judgment.ranking:
                raise RuntimeError("live_jev_empty_ranking")
            selected_mode = judgment.ranking[0]
            selected = next((row for row in candidates if row["mode"] == selected_mode), None)
            if selected is None:
                raise RuntimeError(f"live_jev_unknown_context:{selected_mode}")
            jev_tokens = _jev_token_estimate(request, judgment_dict)

        base_adapter = create_provider_adapter(provider, argv=list(argv), version=model, cwd=root)
        adapter = ContextOverrideAdapter(base_adapter, selected["content"], mode=f"jev:{mode}:{selected['mode']}")
        execution = run_safe_agent_execution(
            root,
            task,
            adapter,
            allowed_files=["math_ops.py"],
            tests=["pytest -q"],
            max_iterations=2,
            timeout_seconds=180,
            max_files=4,
            max_context_chars=12000,
        )
        provider_tokens, provider_latency_ms = _provider_metrics(execution, int(selected["input_tokens_est"]))
        observation = {
            "task_id": "JEV-E2E-MATH-ADD",
            "mode": mode,
            "repeat": repeat,
            "provider": provider,
            "model": model,
            "verified_status": "pass" if execution.get("status") == "passed" else "fail",
            "total_tokens": provider_tokens + jev_tokens,
            "latency_ms": provider_latency_ms + jev_latency_ms,
            "ranking_quality": _ranking_quality(selected, candidates),
            "fallback_used": fallback_used,
            "selected_context": selected["mode"],
            "provider_tokens": provider_tokens,
            "jev_tokens_est": jev_tokens,
            "provider_latency_ms": provider_latency_ms,
            "jev_latency_ms": jev_latency_ms,
            "token_source": "provider_or_context_estimate_plus_jev_request_response_estimate",
        }
        evidence = {
            "observation": observation,
            "judgment": judgment_dict,
            "candidate_contexts": [{k: v for k, v in row.items() if k != "content"} for row in candidates],
            "execution": execution,
        }
        return observation, evidence


def main() -> int:
    parser = argparse.ArgumentParser(description="Run real coding-agent Jev OFF/ON A/B E2E with deterministic verification.")
    parser.add_argument("--provider", default=os.environ.get("UACOS_JEV_BENCHMARK_PROVIDER", "codex"))
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output-dir", default="reports/jev-real-ab")
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()
    if args.repeats < 3:
        raise ValueError("jev_real_ab_minimum_repeats_is_3")

    argv = _provider_argv(args.provider)
    model = _model_from_argv(argv)
    api_key = _typesafe_key()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    observations = []
    evidence = []
    for repeat in range(1, args.repeats + 1):
        for mode in ("jev_off", "jev_on"):
            observation, row_evidence = _run_one(
                provider=args.provider,
                argv=argv,
                model=model,
                mode=mode,
                repeat=repeat,
                api_key=api_key,
            )
            observations.append(observation)
            evidence.append(row_evidence)
            print(json.dumps(observation, sort_keys=True))

    report = evaluate_jev_ab(observations, min_repeats=args.repeats)
    report["real_provider_execution"] = True
    report["live_jev_transport"] = True
    report["provider"] = args.provider
    report["model"] = model
    report["repeats"] = args.repeats
    report["all_jev_on_calls_live"] = all(not row["fallback_used"] for row in observations if row["mode"] == "jev_on")
    off = report["summaries"]["jev_off"]
    on = report["summaries"]["jev_on"]
    report["improvement"] = {
        "reliability_delta": None if off["verified_success_rate"] is None else round(on["verified_success_rate"] - off["verified_success_rate"], 6),
        "token_delta_ratio": report["deltas"]["token_delta_ratio"],
        "latency_delta_ratio": report["deltas"]["latency_delta_ratio"],
        "ranking_quality_delta": None if off["avg_ranking_quality"] is None else round(on["avg_ranking_quality"] - off["avg_ranking_quality"], 6),
    }
    (output / "observations.json").write_text(json.dumps(observations, indent=2, sort_keys=True), encoding="utf-8")
    (output / "evidence.json").write_text(json.dumps(evidence, indent=2, sort_keys=True, default=str), encoding="utf-8")
    (output / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.require_pass and report["status"] != "pass":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
