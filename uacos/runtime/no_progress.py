from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import hashlib
import json


def _stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False, default=str, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def attempt_fingerprint(attempt: dict[str, Any]) -> str:
    """Return a stable fingerprint for the meaningful outcome of one agent attempt.

    Volatile telemetry such as elapsed time and token counts is deliberately ignored.
    The fingerprint focuses on whether the agent is producing the same failure class,
    same patch/output and same validation result repeatedly.
    """
    adapter_result = dict(attempt.get("adapter_result") or {})
    evidence = {
        "status": attempt.get("status"),
        "failure_class": attempt.get("failure_class"),
        "patch_present": bool(attempt.get("patch_present")),
        "patch": adapter_result.get("patch"),
        "output": adapter_result.get("output"),
        "adapter_status": adapter_result.get("status"),
        "validation": attempt.get("patch_validation"),
    }
    return _stable_hash(evidence)


@dataclass
class NoProgressTracker:
    threshold: int = 2
    fingerprints: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.threshold < 2:
            raise ValueError("no_progress_threshold_must_be_at_least_2")

    def observe(self, attempt: dict[str, Any]) -> dict[str, Any]:
        fingerprint = attempt_fingerprint(attempt)
        self.fingerprints.append(fingerprint)

        consecutive = 1
        for prior in reversed(self.fingerprints[:-1]):
            if prior != fingerprint:
                break
            consecutive += 1

        stalled = consecutive >= self.threshold
        return {
            "stalled": stalled,
            "consecutive_same_outcome": consecutive,
            "threshold": self.threshold,
            "fingerprint": fingerprint,
            "reason": "repeated_identical_outcome" if stalled else None,
        }


def detect_no_progress(attempts: list[dict[str, Any]], *, threshold: int = 2) -> dict[str, Any]:
    tracker = NoProgressTracker(threshold=threshold)
    result = {
        "stalled": False,
        "consecutive_same_outcome": 0,
        "threshold": threshold,
        "fingerprint": None,
        "reason": None,
    }
    for attempt in attempts:
        result = tracker.observe(attempt)
    return result
