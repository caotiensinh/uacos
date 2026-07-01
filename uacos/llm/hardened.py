from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import time
import re
import urllib.request
import urllib.error
import os
from uacos.config import uacos_dir
from uacos.llm.providers import load_llm_config, save_llm_config, init_llm_config, run_llm

SECRET_PATTERNS = [
    (re.compile(r"sk-[A-Za-z0-9_\-]{12,}"), "sk-***REDACTED***"),
    (re.compile(r"Bearer\s+[A-Za-z0-9_\-\.]{12,}", re.I), "Bearer ***REDACTED***"),
    (re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[^'\"\s]+"), r"\1=***REDACTED***"),
]

DEFAULT_PRICING = {
    "dry-run": {"input_per_1k": 0.0, "output_per_1k": 0.0},
    "local": {"input_per_1k": 0.0, "output_per_1k": 0.0},
    "gpt-4o-mini": {"input_per_1k": 0.00015, "output_per_1k": 0.0006},
    "gpt-4.1-mini": {"input_per_1k": 0.0004, "output_per_1k": 0.0016},
    "claude-3-5-sonnet": {"input_per_1k": 0.003, "output_per_1k": 0.015},
}

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def provider_history_path(repo_root: Path) -> Path:
    p = uacos_dir(repo_root)
    p.mkdir(parents=True, exist_ok=True)
    return p / "llm_provider_history.jsonl"

def provider_health_path(repo_root: Path) -> Path:
    p = uacos_dir(repo_root)
    p.mkdir(parents=True, exist_ok=True)
    return p / "llm_provider_health.json"

def redact_text(text: str) -> str:
    out = text or ""
    for pat, repl in SECRET_PATTERNS:
        out = pat.sub(repl, out)
    return out

def estimate_tokens(text: str) -> int:
    # Conservative rough estimate for planning only.
    if not text:
        return 0
    return max(1, int(len(text) / 4))

def estimate_cost(model: str, input_tokens: int, output_tokens: int = 0) -> dict:
    price = DEFAULT_PRICING.get(model) or DEFAULT_PRICING.get("local")
    cost = (input_tokens / 1000.0) * price["input_per_1k"] + (output_tokens / 1000.0) * price["output_per_1k"]
    return {"model": model, "input_tokens": input_tokens, "output_tokens": output_tokens, "estimated_cost_usd": round(cost, 8), "pricing": price}

def append_provider_history(repo_root: Path, record: dict) -> dict:
    rec = dict(record)
    rec.setdefault("ts", utcnow())
    # Redact text fields before writing.
    for k in ["prompt", "response", "content", "error"]:
        if k in rec and isinstance(rec[k], str):
            rec[k] = redact_text(rec[k])
    with provider_history_path(repo_root).open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec

def read_provider_history(repo_root: Path, limit: int = 50) -> list[dict]:
    path = provider_history_path(repo_root)
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows[-limit:]

def configure_model_route(repo_root: Path, route_name: str, provider: str, model: str, task_keywords: list[str] | None = None) -> dict:
    cfg = load_llm_config(repo_root)
    routes = cfg.setdefault("routes", {})
    routes[route_name] = {"provider": provider, "model": model, "task_keywords": task_keywords or [], "updated_at": utcnow()}
    save_llm_config(repo_root, cfg)
    return {"status": "ok", "route": route_name, "config": routes[route_name]}

def route_provider(repo_root: Path, task: str, default_provider: str | None = None) -> dict:
    cfg = load_llm_config(repo_root)
    routes = cfg.get("routes", {})
    low = (task or "").lower()
    for name, route in routes.items():
        for kw in route.get("task_keywords", []):
            if kw.lower() in low:
                return {"status": "ok", "route": name, "provider": route["provider"], "model": route.get("model"), "reason": f"keyword:{kw}"}
    provider = default_provider or cfg.get("default_provider", "dry_run")
    model = cfg.get("providers", {}).get(provider, {}).get("model")
    return {"status": "ok", "route": "default", "provider": provider, "model": model, "reason": "default"}

def provider_health_check(repo_root: Path, provider: str | None = None, dry_run: bool = True) -> dict:
    cfg = load_llm_config(repo_root)
    provider = provider or cfg.get("default_provider", "dry_run")
    pconf = cfg.get("providers", {}).get(provider)
    if not pconf:
        result = {"status": "fail", "provider": provider, "reason": "provider_not_found", "checked_at": utcnow()}
    elif dry_run or pconf.get("type") == "dry_run":
        result = {"status": "ok", "provider": provider, "type": pconf.get("type"), "mode": "dry_run", "checked_at": utcnow()}
    else:
        try:
            # Make a minimal provider call through existing run_llm.
            res = run_llm(repo_root, "health check: reply OK", provider=provider, dry_run=False)
            result = {"status": "ok" if res.get("status") in {"ok", "dry_run"} else "fail", "provider": provider, "run_status": res.get("status"), "checked_at": utcnow()}
        except Exception as exc:
            result = {"status": "fail", "provider": provider, "reason": type(exc).__name__, "message": str(exc), "checked_at": utcnow()}
    health = {}
    path = provider_health_path(repo_root)
    if path.exists():
        try:
            health = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            health = {}
    health[provider] = result
    path.write_text(json.dumps(health, ensure_ascii=False, indent=2), encoding="utf-8")
    return result

def run_llm_hardened(
    repo_root: Path,
    prompt: str,
    provider: str | None = None,
    task: str = "",
    dry_run: bool | None = None,
    retries: int = 2,
    backoff_sec: float = 0.5,
    output_token_estimate: int = 0,
) -> dict:
    route = route_provider(repo_root, task or prompt[:200], default_provider=provider)
    provider = provider or route["provider"]
    cfg = load_llm_config(repo_root)
    pconf = cfg.get("providers", {}).get(provider, {})
    model = pconf.get("model", route.get("model") or "unknown")
    input_tokens = estimate_tokens(prompt)
    pre_cost = estimate_cost(model, input_tokens, output_token_estimate)
    start = time.time()
    attempts = []
    final = None
    for attempt in range(retries + 1):
        try:
            res = run_llm(repo_root, prompt, provider=provider, dry_run=dry_run)
            final = res
            attempts.append({"attempt": attempt + 1, "status": res.get("status")})
            if res.get("status") in {"ok", "dry_run", "blocked"}:
                break
        except Exception as exc:
            attempts.append({"attempt": attempt + 1, "status": "exception", "type": type(exc).__name__, "message": str(exc)})
            if attempt < retries:
                time.sleep(backoff_sec * (2 ** attempt))
            else:
                final = {"status": "error", "provider": provider, "model": model, "error": {"type": type(exc).__name__, "message": str(exc)}}
    elapsed = round(time.time() - start, 4)
    content = (final or {}).get("content", "")
    output_tokens = estimate_tokens(content)
    post_cost = estimate_cost(model, input_tokens, output_tokens)
    record = {
        "event": "llm_run",
        "provider": provider,
        "model": model,
        "route": route,
        "status": (final or {}).get("status"),
        "attempts": attempts,
        "elapsed_sec": elapsed,
        "input_tokens_est": input_tokens,
        "output_tokens_est": output_tokens,
        "estimated_cost": post_cost,
        "prompt": prompt[:2000],
        "response": content[:2000],
    }
    append_provider_history(repo_root, record)
    return {
        "status": (final or {}).get("status"),
        "provider": provider,
        "model": model,
        "route": route,
        "attempts": attempts,
        "elapsed_sec": elapsed,
        "input_tokens_est": input_tokens,
        "output_tokens_est": output_tokens,
        "estimated_cost": post_cost,
        "result": final,
    }

def provider_summary(repo_root: Path) -> dict:
    rows = read_provider_history(repo_root, limit=10000)
    by_provider = {}
    total_cost = 0.0
    for row in rows:
        p = row.get("provider", "unknown")
        item = by_provider.setdefault(p, {"runs": 0, "statuses": {}, "estimated_cost_usd": 0.0})
        item["runs"] += 1
        st = row.get("status", "unknown")
        item["statuses"][st] = item["statuses"].get(st, 0) + 1
        cost = (row.get("estimated_cost") or {}).get("estimated_cost_usd", 0.0)
        item["estimated_cost_usd"] += float(cost)
        total_cost += float(cost)
    return {"status": "ok", "runs": len(rows), "by_provider": by_provider, "estimated_cost_usd": round(total_cost, 8), "recent": rows[-20:]}
