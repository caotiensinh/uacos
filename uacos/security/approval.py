from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib


def patch_sha256(patch_text: str) -> str:
    return hashlib.sha256(patch_text.encode("utf-8")).hexdigest()


def create_approval_record(
    patch_text: str,
    policy_decision: dict,
    *,
    approved_by: str,
    ttl_seconds: int | None = None,
    now: datetime | None = None,
) -> dict:
    approver = str(approved_by or "").strip()
    if not approver:
        raise ValueError("approved_by_required")
    if policy_decision.get("action") != "approval_required":
        raise ValueError("approval_not_required_for_decision")

    created = now or datetime.now(timezone.utc)
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    ttl = int(ttl_seconds or policy_decision.get("approval_ttl_seconds") or 3600)
    if ttl <= 0 or ttl > 86400:
        raise ValueError("approval_ttl_seconds_out_of_range")
    expires = created + timedelta(seconds=ttl)

    return {
        "version": 1,
        "approved_by": approver,
        "approved_at": created.astimezone(timezone.utc).isoformat(),
        "expires_at": expires.astimezone(timezone.utc).isoformat(),
        "patch_sha256": patch_sha256(patch_text),
        "policy_sha256": policy_decision.get("policy_sha256"),
        "risk_level": policy_decision.get("risk_level"),
        "categories": list(policy_decision.get("categories") or []),
        "decision_action": policy_decision.get("action"),
    }


def verify_approval_record(
    record: dict | None,
    patch_text: str,
    policy_decision: dict,
    *,
    now: datetime | None = None,
) -> dict:
    findings: list[str] = []
    if not isinstance(record, dict):
        return {"status": "fail", "findings": ["approval_record_missing"]}
    if record.get("version") != 1:
        findings.append("unsupported_approval_version")
    if not str(record.get("approved_by") or "").strip():
        findings.append("approved_by_missing")
    if record.get("patch_sha256") != patch_sha256(patch_text):
        findings.append("patch_hash_mismatch")
    if record.get("policy_sha256") != policy_decision.get("policy_sha256"):
        findings.append("policy_hash_mismatch")
    if record.get("decision_action") != "approval_required":
        findings.append("decision_action_mismatch")

    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    try:
        expires = datetime.fromisoformat(str(record.get("expires_at") or ""))
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if current.astimezone(timezone.utc) >= expires.astimezone(timezone.utc):
            findings.append("approval_expired")
    except Exception:
        findings.append("invalid_expiry")

    return {
        "status": "pass" if not findings else "fail",
        "approved_by": record.get("approved_by"),
        "findings": findings,
    }
