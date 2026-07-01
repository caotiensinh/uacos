from __future__ import annotations

from pathlib import Path
from uacos.config import uacos_dir
from uacos.agent.models import TaskSpec, new_id, dataclass_to_dict, save_json, load_json

def tasks_dir(repo_root: Path) -> Path:
    return uacos_dir(repo_root) / "tasks"

def create_task(
    repo_root: Path,
    title: str,
    objective: str,
    allowed_files: list[str] | None = None,
    allowed_dirs: list[str] | None = None,
    forbidden_files: list[str] | None = None,
    tests: list[str] | None = None,
    commands: list[str] | None = None,
    risk_level: str = "normal",
) -> Path:
    task = TaskSpec(
        id=new_id("TASK"),
        title=title,
        objective=objective,
        allowed_files=allowed_files or [],
        allowed_dirs=allowed_dirs or [],
        forbidden_files=forbidden_files or [],
        tests=tests or [],
        commands=commands or [],
        risk_level=risk_level,
    )
    path = tasks_dir(repo_root) / f"{task.id}.json"
    save_json(path, dataclass_to_dict(task))
    return path

def load_task(path: Path) -> dict:
    return load_json(path)
