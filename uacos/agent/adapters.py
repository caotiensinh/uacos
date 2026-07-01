from __future__ import annotations
from pathlib import Path
from uacos.agent.models import new_id, utcnow

class AgentAdapter:
    name = "base"

    def run(self, repo_root: Path, agent: dict, task: dict, context_pack: dict, phase: str) -> dict:
        raise NotImplementedError

class DryRunAdapter(AgentAdapter):
    name = "dry_run"

    def run(self, repo_root: Path, agent: dict, task: dict, context_pack: dict, phase: str) -> dict:
        # This does not call external AI. It validates orchestration and produces deterministic evidence.
        return {
            "id": new_id("STEP"),
            "adapter": self.name,
            "agent": agent["name"],
            "role": agent["role"],
            "phase": phase,
            "status": "ok",
            "created_at": utcnow(),
            "message": f"Dry-run completed for {agent['role']} on task {task['id']}",
            "context_id": context_pack.get("id"),
            "evidence": {
                "task_title": task.get("title"),
                "allowed_files": task.get("allowed_files", []),
                "tests": task.get("tests", []),
            },
        }

class LocalEchoAdapter(AgentAdapter):
    name = "local_echo"

    def run(self, repo_root: Path, agent: dict, task: dict, context_pack: dict, phase: str) -> dict:
        content = context_pack.get("content", "")
        return {
            "id": new_id("STEP"),
            "adapter": self.name,
            "agent": agent["name"],
            "role": agent["role"],
            "phase": phase,
            "status": "ok",
            "created_at": utcnow(),
            "message": "Local echo adapter received context pack.",
            "context_preview": content[:500],
            "context_id": context_pack.get("id"),
        }

ADAPTERS = {
    "dry_run": DryRunAdapter(),
    "local_echo": LocalEchoAdapter(),
}

def get_adapter(name: str) -> AgentAdapter:
    if name not in ADAPTERS:
        raise ValueError(f"Unknown adapter: {name}")
    return ADAPTERS[name]
