from __future__ import annotations

from pathlib import Path
from typing import Mapping
import os
import subprocess
import time

from uacos.agent.protocol import AgentCapabilities, AgentRunRequest, AgentRunResult


def build_agent_prompt(request: AgentRunRequest) -> str:
    return "\n".join(
        [
            "# UACOS External Agent Run",
            f"Run ID: {request.run_id}",
            f"Iteration: {request.iteration}",
            "",
            "## Task",
            request.task,
            "",
            "## Allowed Files",
            *(f"- {item}" for item in request.allowed_files),
            "",
            "## Allowed Dirs",
            *(f"- {item}" for item in request.allowed_dirs),
            "",
            "## Tests",
            *(f"- {item}" for item in request.tests),
            "",
            "## Required Output",
            "Return a unified diff when changes are required.",
            "Do not modify files outside the allowed scope.",
            "Do not claim success without evidence.",
            "",
            "## Context",
            request.context,
        ]
    )


class SubprocessAgentAdapter:
    """Provider-neutral CLI adapter using argv execution with no shell expansion."""

    capabilities = AgentCapabilities(
        patches=True,
        tool_calls=False,
        streaming=False,
        cancellation=False,
        token_usage=False,
        native_mcp=False,
    )

    def __init__(
        self,
        name: str,
        argv: list[str],
        *,
        version: str | None = None,
        cwd: Path | None = None,
        env: Mapping[str, str] | None = None,
    ) -> None:
        if not name.strip():
            raise ValueError("adapter_name_required")
        if not argv or not all(isinstance(item, str) and item for item in argv):
            raise ValueError("non_empty_argv_required")
        self.name = name
        self.version = version
        self.argv = list(argv)
        self.cwd = cwd
        self.env = dict(env or {})

    def run(self, request: AgentRunRequest) -> AgentRunResult:
        started = time.monotonic()
        prompt = build_agent_prompt(request)
        merged_env = os.environ.copy()
        merged_env.update(self.env)
        try:
            proc = subprocess.run(
                self.argv,
                input=prompt,
                cwd=str(self.cwd) if self.cwd else None,
                env=merged_env,
                capture_output=True,
                text=True,
                timeout=request.timeout_seconds,
                shell=False,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            elapsed = max(0, int((time.monotonic() - started) * 1000))
            stdout = exc.stdout if isinstance(exc.stdout, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
            return AgentRunResult(
                adapter_name=self.name,
                adapter_version=self.version,
                status="timeout",
                output=stdout,
                elapsed_ms=elapsed,
                failure_class="adapter_timeout",
                evidence={"stderr": stderr[-4000:], "argv": list(self.argv)},
            )
        except OSError as exc:
            elapsed = max(0, int((time.monotonic() - started) * 1000))
            return AgentRunResult(
                adapter_name=self.name,
                adapter_version=self.version,
                status="error",
                elapsed_ms=elapsed,
                failure_class="adapter_launch_error",
                evidence={"error": f"{type(exc).__name__}:{exc}", "argv": list(self.argv)},
            )

        elapsed = max(0, int((time.monotonic() - started) * 1000))
        if proc.returncode != 0:
            return AgentRunResult(
                adapter_name=self.name,
                adapter_version=self.version,
                status="failed",
                output=proc.stdout or "",
                elapsed_ms=elapsed,
                exit_code=proc.returncode,
                failure_class="adapter_nonzero_exit",
                evidence={"stderr": (proc.stderr or "")[-4000:], "argv": list(self.argv)},
            )

        return AgentRunResult(
            adapter_name=self.name,
            adapter_version=self.version,
            status="completed",
            output=proc.stdout or "",
            elapsed_ms=elapsed,
            exit_code=proc.returncode,
            evidence={"stderr": (proc.stderr or "")[-4000:], "argv": list(self.argv)},
        )
