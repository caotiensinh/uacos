from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml


DEFAULT_POLICY = {
    "version": 1,
    "default_action": "allow",
    "approval": {
        "required_risk_levels": ["high", "critical"],
        "required_categories": [],
        "ttl_seconds": 3600,
    },
    "deny": {
        "risk_levels": ["block"],
        "categories": [],
    },
}


def _canonical_hash(value: dict) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_policy(path: Path) -> dict:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError("policy_root_must_be_mapping")

    policy = {
        "version": int(raw.get("version", 1)),
        "default_action": str(raw.get("default_action", "allow")),
        "approval": dict(DEFAULT_POLICY["approval"]),
        "deny": dict(DEFAULT_POLICY["deny"]),
    }
    approval = raw.get("approval") or {}
    deny = raw.get("deny") or {}
    if not isinstance(approval, dict) or not isinstance(deny, dict):
        raise ValueError("policy_sections_must_be_mappings")

    policy["approval"].update(approval)
    policy["deny"].update(deny)

    if policy["version"] != 1:
        raise ValueError("unsupported_policy_version")
    if policy["default_action"] not in {"allow", "deny"}:
        raise ValueError("invalid_default_action")

    for section, key in (("approval", "required_risk_levels"), ("approval", "required_categories"), ("deny", "risk_levels"), ("deny", "categories")):
        value = policy[section].get(key, [])
        if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
            raise ValueError(f"invalid_policy_list:{section}.{key}")
        policy[section][key] = sorted(set(value))

    ttl = int(policy["approval"].get("ttl_seconds", 3600))
    if ttl <= 0 or ttl > 86400:
        raise ValueError("approval_ttl_seconds_out_of_range")
    policy["approval"]["ttl_seconds"] = ttl
    policy["policy_sha256"] = _canonical_hash({k: v for k, v in policy.items() if k != "policy_sha256"})
    return policy


def evaluate_patch_policy(review: dict, policy: dict) -> dict:
    risk_level = str(review.get("risk_level") or "low")
    categories = set(review.get("risk_categories") or [])
    semantic = review.get("semantic_risk") or {}
    categories.update(semantic.get("categories") or [])

    deny_risks = set(policy.get("deny", {}).get("risk_levels") or [])
    deny_categories = set(policy.get("deny", {}).get("categories") or [])
    approval_risks = set(policy.get("approval", {}).get("required_risk_levels") or [])
    approval_categories = set(policy.get("approval", {}).get("required_categories") or [])

    reasons: list[str] = []
    action = "allow"
    denied_categories = sorted(categories & deny_categories)
    approval_category_hits = sorted(categories & approval_categories)

    if risk_level in deny_risks:
        action = "deny"
        reasons.append(f"denied_risk_level:{risk_level}")
    if denied_categories:
        action = "deny"
        reasons.extend(f"denied_category:{item}" for item in denied_categories)

    if action != "deny":
        if risk_level in approval_risks:
            action = "approval_required"
            reasons.append(f"approval_risk_level:{risk_level}")
        if approval_category_hits:
            action = "approval_required"
            reasons.extend(f"approval_category:{item}" for item in approval_category_hits)
        if not reasons and policy.get("default_action") == "deny":
            action = "deny"
            reasons.append("default_deny")

    return {
        "action": action,
        "allowed": action == "allow",
        "requires_approval": action == "approval_required",
        "risk_level": risk_level,
        "categories": sorted(categories),
        "reasons": reasons,
        "policy_sha256": policy.get("policy_sha256"),
        "approval_ttl_seconds": int(policy.get("approval", {}).get("ttl_seconds", 3600)),
    }
