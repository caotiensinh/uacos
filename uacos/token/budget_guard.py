import json
from pathlib import Path
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).isoformat()


def _dir(repo_root):
    p = Path(repo_root) / ".uacos"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _path(repo_root):
    return _dir(repo_root) / "token_budget.json"


def _default_budget():
    return {
        "enabled": True,
        "cloud_only": True,
        "max_cloud_tokens": 20000,
        "used_cloud_tokens": 0,
        "max_total_tokens": 200000,
        "used_total_tokens": 0,
        "hard_stop": True,
        "updated_at": _now(),
    }


def _save(repo_root, data):
    data["updated_at"] = _now()
    _path(repo_root).write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return data


def load_budget(repo_root):
    path = _path(repo_root)

    if not path.exists():
        return _save(repo_root, _default_budget())

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        data = _default_budget()

    default = _default_budget()
    for key, value in default.items():
        data.setdefault(key, value)

    return data


def set_budget(
    repo_root,
    max_cloud_tokens=None,
    max_total_tokens=None,
    enabled=None,
    cloud_only=None,
    hard_stop=None,
):
    data = load_budget(repo_root)

    if max_cloud_tokens is not None:
        data["max_cloud_tokens"] = int(max_cloud_tokens)

    if max_total_tokens is not None:
        data["max_total_tokens"] = int(max_total_tokens)

    if enabled is not None:
        data["enabled"] = bool(enabled)

    if cloud_only is not None:
        data["cloud_only"] = bool(cloud_only)

    if hard_stop is not None:
        data["hard_stop"] = bool(hard_stop)

    return _save(repo_root, data)


def reset_budget(repo_root):
    data = load_budget(repo_root)
    data["used_cloud_tokens"] = 0
    data["used_total_tokens"] = 0
    return _save(repo_root, data)


def _extract_tokens(args, kwargs):
    for name in ("estimated_tokens", "tokens", "total_tokens", "input_tokens"):
        if name in kwargs and kwargs[name] is not None:
            return int(kwargs[name])

    if args:
        try:
            return int(args[0])
        except Exception:
            return 0

    return 0


def _extract_cloud(args, kwargs):
    if "is_cloud" in kwargs:
        return bool(kwargs["is_cloud"])

    if "cloud" in kwargs:
        return bool(kwargs["cloud"])

    provider = str(kwargs.get("provider", "") or "").lower()
    if not provider and len(args) >= 2:
        provider = str(args[1] or "").lower()

    if provider:
        return provider not in {"ollama", "ollama_lan", "ollama_local", "local"}

    return True


def check_budget(repo_root, *args, **kwargs):
    tokens = _extract_tokens(args, kwargs)
    is_cloud = _extract_cloud(args, kwargs)
    data = load_budget(repo_root)

    result = dict(data)
    result["requested_tokens"] = tokens
    result["is_cloud"] = is_cloud
    result["status"] = "pass"
    result["reason"] = None

    if not data.get("enabled", True):
        return result

    projected_total = int(data.get("used_total_tokens", 0)) + tokens

    if projected_total > int(data.get("max_total_tokens", 200000)):
        result["status"] = "blocked"
        result["reason"] = "max_total_tokens_exceeded"
        result["projected_total_tokens"] = projected_total
        return result

    should_count_cloud = is_cloud or not data.get("cloud_only", True)

    if should_count_cloud:
        projected_cloud = int(data.get("used_cloud_tokens", 0)) + tokens

        if projected_cloud > int(data.get("max_cloud_tokens", 20000)):
            result["status"] = "blocked"
            result["reason"] = "max_cloud_tokens_exceeded"
            result["projected_cloud_tokens"] = projected_cloud
            return result

    return result


def consume_tokens(repo_root, *args, **kwargs):
    tokens = _extract_tokens(args, kwargs)
    is_cloud = _extract_cloud(args, kwargs)
    data = load_budget(repo_root)

    if not data.get("enabled", True):
        result = dict(data)
        result["status"] = "skipped"
        result["reason"] = "budget_disabled"
        result["consumed_tokens"] = 0
        return result

    data["used_total_tokens"] = int(data.get("used_total_tokens", 0)) + tokens

    if is_cloud or not data.get("cloud_only", True):
        data["used_cloud_tokens"] = int(data.get("used_cloud_tokens", 0)) + tokens

    saved = _save(repo_root, data)
    saved["status"] = "ok"
    saved["reason"] = None
    saved["consumed_tokens"] = tokens
    saved["is_cloud"] = is_cloud
    return saved
