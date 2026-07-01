from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timezone
import json
import uuid

def utcnow():
    return datetime.now(timezone.utc).isoformat()

def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"

@dataclass
class AgentSpec:
    name: str
    role: str
    adapter: str
    model: str = "local"
    priority: int = 100
    can_edit: bool = False
    can_run_commands: bool = False
    description: str = ""

@dataclass
class TaskSpec:
    id: str
    title: str
    objective: str
    allowed_files: list[str] = field(default_factory=list)
    allowed_dirs: list[str] = field(default_factory=list)
    forbidden_files: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    risk_level: str = "normal"
    created_at: str = field(default_factory=utcnow)

@dataclass
class Assignment:
    agent: str
    role: str
    responsibility: str

@dataclass
class WorkflowPlan:
    id: str
    task_id: str
    assignments: list[Assignment]
    gates: list[str]
    created_at: str = field(default_factory=utcnow)

def dataclass_to_dict(obj):
    if hasattr(obj, "__dataclass_fields__"):
        out = {}
        for k in obj.__dataclass_fields__:
            v = getattr(obj, k)
            if isinstance(v, list):
                out[k] = [dataclass_to_dict(x) for x in v]
            else:
                out[k] = dataclass_to_dict(v)
        return out
    return obj

def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
