from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
import time
import uuid


TERMINAL_STATUSES = {"passed", "failed", "blocked", "timeout", "cancelled", "error"}


@dataclass(frozen=True)
class AgentCapabilities:
    patches: bool = True
    tool_calls: bool = False
    streaming: bool = False
    cancellation: bool = False
    token_usage: bool = False
    native_mcp: bool = False


@dataclass
class AgentRunRequest:
    task: str
    context: str
    allowed_files: list[str] = field(default_factory=list)
    allowed_dirs: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)
    run_id: str = field(default_factory=lambda: "RUN-" + uuid.uuid4().hex[:12])
    iteration: int = 1
    timeout_seconds: int = 120
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AgentRunResult:
    adapter_name: str
    status: str
    output: str = ""
    patch: str | None = None
    elapsed_ms: int = 0
    tokens_in: int | None = None
    tokens_out: int | None = None
    tool_calls: int | None = None
    exit_code: int | None = None
    failure_class: str | None = None
    adapter_version: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status not in TERMINAL_STATUSES | {"completed", "diff_ready", "no_diff"}:
            raise ValueError(f"invalid_agent_run_status:{self.status}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_agent_result(adapter: Any, raw: AgentRunResult | dict[str, Any], started_monotonic: float) -> AgentRunResult:
    """Normalize provider-specific output into one stable runtime contract."""
    if isinstance(raw, AgentRunResult):
        result = raw
    else:
        result = AgentRunResult(
            adapter_name=str(raw.get("adapter_name") or getattr(adapter, "name", type(adapter).__name__)),
            adapter_version=raw.get("adapter_version") or getattr(adapter, "version", None),
            status=str(raw.get("status") or "completed"),
            output=str(raw.get("output") or raw.get("content") or ""),
            patch=raw.get("patch") or raw.get("diff"),
            tokens_in=raw.get("tokens_in"),
            tokens_out=raw.get("tokens_out"),
            tool_calls=raw.get("tool_calls"),
            exit_code=raw.get("exit_code"),
            failure_class=raw.get("failure_class"),
            evidence=dict(raw.get("evidence") or {}),
        )
    if result.elapsed_ms <= 0:
        result.elapsed_ms = max(0, int((time.monotonic() - started_monotonic) * 1000))
    return result
