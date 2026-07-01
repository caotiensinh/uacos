from __future__ import annotations

from pathlib import Path
from uacos.config import uacos_dir
from uacos.agent.models import AgentSpec, dataclass_to_dict, save_json, load_json

DEFAULT_AGENTS = [
    AgentSpec(
        name="planner",
        role="planner",
        adapter="dry_run",
        model="local",
        priority=10,
        can_edit=False,
        can_run_commands=False,
        description="Breaks task into safe plan and context requirements.",
    ),
    AgentSpec(
        name="coder",
        role="coder",
        adapter="dry_run",
        model="local",
        priority=20,
        can_edit=True,
        can_run_commands=False,
        description="Produces patch proposal within allowed scope.",
    ),
    AgentSpec(
        name="reviewer",
        role="reviewer",
        adapter="dry_run",
        model="local",
        priority=30,
        can_edit=False,
        can_run_commands=False,
        description="Reviews patch and scope/security risks.",
    ),
    AgentSpec(
        name="tester",
        role="tester",
        adapter="dry_run",
        model="local",
        priority=40,
        can_edit=False,
        can_run_commands=True,
        description="Runs approved tests/commands only.",
    ),
]

def registry_path(repo_root: Path) -> Path:
    return uacos_dir(repo_root) / "agents.json"

def init_agent_registry(repo_root: Path) -> Path:
    data = {"agents": [dataclass_to_dict(a) for a in DEFAULT_AGENTS]}
    path = registry_path(repo_root)
    save_json(path, data)
    return path

def load_agents(repo_root: Path) -> list[dict]:
    path = registry_path(repo_root)
    if not path.exists():
        init_agent_registry(repo_root)
    return load_json(path)["agents"]

def select_agent(repo_root: Path, role: str) -> dict | None:
    agents = [a for a in load_agents(repo_root) if a.get("role") == role]
    if not agents:
        return None
    return sorted(agents, key=lambda a: a.get("priority", 100))[0]
