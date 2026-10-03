from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
import shutil

from uacos.agent.process_adapter import SubprocessAgentAdapter


@dataclass(frozen=True)
class ProviderProfile:
    name: str
    executable: str
    display_name: str
    description: str
    requires_explicit_argv: bool = True


PROVIDER_PROFILES: dict[str, ProviderProfile] = {
    "codex": ProviderProfile(
        name="codex",
        executable="codex",
        display_name="Codex CLI",
        description="OpenAI Codex CLI profile using the provider-neutral subprocess adapter.",
    ),
    "claude_code": ProviderProfile(
        name="claude_code",
        executable="claude",
        display_name="Claude Code",
        description="Anthropic Claude Code CLI profile using the provider-neutral subprocess adapter.",
    ),
    "goose": ProviderProfile(
        name="goose",
        executable="goose",
        display_name="Goose",
        description="Block Goose CLI profile using the provider-neutral subprocess adapter.",
    ),
}


def get_provider_profile(name: str) -> ProviderProfile:
    try:
        return PROVIDER_PROFILES[name]
    except KeyError as exc:
        raise ValueError(f"unknown_provider_profile:{name}") from exc


def probe_provider(name: str) -> dict:
    profile = get_provider_profile(name)
    resolved = shutil.which(profile.executable)
    return {
        "name": profile.name,
        "display_name": profile.display_name,
        "executable": profile.executable,
        "available": bool(resolved),
        "resolved_path": resolved,
        "requires_explicit_argv": profile.requires_explicit_argv,
    }


def create_provider_adapter(
    name: str,
    *,
    argv: list[str] | None,
    version: str | None = None,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
) -> SubprocessAgentAdapter:
    """Build a provider-specific adapter without guessing unstable CLI flags."""
    profile = get_provider_profile(name)
    if not argv:
        raise ValueError(f"provider_argv_required:{name}")
    if Path(argv[0]).name != profile.executable:
        raise ValueError(
            f"provider_executable_mismatch:{name}:expected={profile.executable}:got={Path(argv[0]).name}"
        )
    return SubprocessAgentAdapter(
        profile.name,
        argv,
        version=version,
        cwd=cwd,
        env=env,
    )


def provider_catalog() -> list[dict]:
    return [
        {
            "name": profile.name,
            "display_name": profile.display_name,
            "executable": profile.executable,
            "description": profile.description,
            "requires_explicit_argv": profile.requires_explicit_argv,
        }
        for profile in PROVIDER_PROFILES.values()
    ]
