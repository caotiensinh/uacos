from pathlib import Path
from uacos.config import uacos_dir
from uacos.agent.models import save_json, load_json

DEFAULT_CONFIG = {
    "version": 1,
    "default_dry_run": True,
    "adapters": {
        "manual_chat": {
            "enabled": True,
            "type": "export",
            "dry_run": True,
            "description": "Exports context pack for ChatGPT/Claude web/manual paste."
        },
        "openclaw_cli": {
            "enabled": True,
            "type": "cli",
            "dry_run": True,
            "command_template": "/home/aiserver/ai-team/executor/chat.sh {agent} {prompt_file}",
            "default_agent": "leader",
            "timeout_seconds": 120,
            "description": "Runs OpenClaw through a local CLI wrapper."
        },
        "aider_cli": {
            "enabled": True,
            "type": "cli",
            "dry_run": True,
            "command_template": "aider --message-file {prompt_file}",
            "timeout_seconds": 120,
            "description": "Runs Aider CLI with a prompt file."
        },
        "ollama_openai": {
            "enabled": True,
            "type": "openai_compatible",
            "dry_run": True,
            "base_url": "http://localhost:11434/v1/chat/completions",
            "model": "qwen2.5-coder:7b",
            "timeout_seconds": 120,
            "description": "Calls local Ollama/OpenAI-compatible chat endpoint."
        },
        "cline_roo_mcp": {
            "enabled": True,
            "type": "mcp_manifest",
            "dry_run": True,
            "description": "Exports MCP manifest skeleton for Cline/Roo compatible agents."
        }
    }
}

def adapter_config_path(repo_root: Path) -> Path:
    return uacos_dir(repo_root) / "adapters.json"

def init_adapter_config(repo_root: Path) -> Path:
    path = adapter_config_path(repo_root)
    save_json(path, DEFAULT_CONFIG)
    return path

def load_adapter_config(repo_root: Path) -> dict:
    path = adapter_config_path(repo_root)
    if not path.exists():
        init_adapter_config(repo_root)
    return load_json(path)

def get_adapter_config(repo_root: Path, name: str) -> dict:
    cfg = load_adapter_config(repo_root)
    adapters = cfg.get("adapters", {})
    if name not in adapters:
        raise ValueError(f"Unknown adapter config: {name}")
    item = dict(adapters[name])
    item["name"] = name
    if "dry_run" not in item:
        item["dry_run"] = cfg.get("default_dry_run", True)
    return item
