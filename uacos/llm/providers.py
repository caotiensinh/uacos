from __future__ import annotations

from pathlib import Path
import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone
from uacos.config import uacos_dir

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

DEFAULT_LLM_CONFIG = {
    "version": 1,
    "default_provider": "dry_run",
    "providers": {
        "dry_run": {
            "type": "dry_run",
            "model": "dry-run",
            "enabled": True
        },
        "ollama": {
            "type": "ollama",
            "base_url": "http://127.0.0.1:11434",
            "model": "qwen2.5-coder:7b",
            "enabled": False,
            "timeout_sec": 120
        },
        "openai_compatible": {
            "type": "openai_compatible",
            "base_url": "http://127.0.0.1:3000/v1",
            "model": "local-model",
            "api_key_env": "UACOS_OPENAI_API_KEY",
            "enabled": False,
            "timeout_sec": 120
        }
    },
    "safety": {
        "dry_run_default": True,
        "require_provider_enabled": True,
        "max_prompt_chars": 120000
    }
}

def llm_config_path(repo_root: Path) -> Path:
    p = uacos_dir(repo_root)
    p.mkdir(parents=True, exist_ok=True)
    return p / "llm_providers.json"

def init_llm_config(repo_root: Path) -> dict:
    path = llm_config_path(repo_root)
    if not path.exists():
        path.write_text(json.dumps(DEFAULT_LLM_CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "ok", "config": str(path), "config_data": json.loads(path.read_text(encoding="utf-8"))}

def load_llm_config(repo_root: Path) -> dict:
    path = llm_config_path(repo_root)
    if not path.exists():
        init_llm_config(repo_root)
    return json.loads(path.read_text(encoding="utf-8"))

def save_llm_config(repo_root: Path, cfg: dict) -> dict:
    path = llm_config_path(repo_root)
    path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "ok", "config": str(path)}

def set_provider_enabled(repo_root: Path, provider: str, enabled: bool) -> dict:
    cfg = load_llm_config(repo_root)
    if provider not in cfg.get("providers", {}):
        raise KeyError(f"provider_not_found:{provider}")
    cfg["providers"][provider]["enabled"] = bool(enabled)
    save_llm_config(repo_root, cfg)
    return {"status": "ok", "provider": provider, "enabled": bool(enabled)}

def _post_json(url: str, payload: dict, headers: dict | None = None, timeout: int = 120) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **(headers or {})}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"http_error:{e.code}:{detail[:500]}")

def run_llm(repo_root: Path, prompt: str, provider: str | None = None, dry_run: bool | None = None) -> dict:
    cfg = load_llm_config(repo_root)
    provider = provider or cfg.get("default_provider", "dry_run")
    pconf = cfg.get("providers", {}).get(provider)
    if not pconf:
        raise KeyError(f"provider_not_found:{provider}")

    max_chars = int(cfg.get("safety", {}).get("max_prompt_chars", 120000))
    if len(prompt) > max_chars:
        return {"status": "blocked", "reason": "prompt_too_large", "prompt_chars": len(prompt), "max_prompt_chars": max_chars}

    if dry_run is None:
        dry_run = bool(cfg.get("safety", {}).get("dry_run_default", True))
    if dry_run or pconf.get("type") == "dry_run":
        return {
            "status": "dry_run",
            "provider": provider,
            "model": pconf.get("model", "dry-run"),
            "prompt_chars": len(prompt),
            "content": "DRY_RUN: provider not called. Review prompt and enable provider when ready.",
            "created_at": utcnow()
        }

    if cfg.get("safety", {}).get("require_provider_enabled", True) and not pconf.get("enabled", False):
        return {"status": "blocked", "reason": "provider_disabled", "provider": provider}

    ptype = pconf.get("type")
    timeout = int(pconf.get("timeout_sec", 120))
    if ptype == "ollama":
        url = pconf.get("base_url", "http://127.0.0.1:11434").rstrip("/") + "/api/generate"
        payload = {"model": pconf["model"], "prompt": prompt, "stream": False}
        data = _post_json(url, payload, timeout=timeout)
        return {"status": "ok", "provider": provider, "model": pconf["model"], "content": data.get("response", ""), "raw": data, "created_at": utcnow()}

    if ptype == "openai_compatible":
        base = pconf.get("base_url", "").rstrip("/")
        url = base + "/chat/completions"
        key = os.environ.get(pconf.get("api_key_env", "UACOS_OPENAI_API_KEY"), "")
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        payload = {
            "model": pconf["model"],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
        data = _post_json(url, payload, headers=headers, timeout=timeout)
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {"status": "ok", "provider": provider, "model": pconf["model"], "content": content, "raw": data, "created_at": utcnow()}

    raise ValueError(f"unsupported_provider_type:{ptype}")
