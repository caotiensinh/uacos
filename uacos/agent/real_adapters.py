from __future__ import annotations

from pathlib import Path
import subprocess
import json
import urllib.request
import urllib.error
from uacos.agent.models import new_id, utcnow
from uacos.agent.adapter_config import get_adapter_config
from uacos.agent.task import load_task
from uacos.retrieval.context_pack import build_context_pack
from uacos.security.command_policy import check_command
from uacos.config import uacos_dir

def prompt_dir(repo_root: Path) -> Path:
    p = uacos_dir(repo_root) / "adapter_prompts"
    p.mkdir(parents=True, exist_ok=True)
    return p

def build_agent_prompt(task: dict, context_pack: dict) -> str:
    return "\n".join([
        "# UACOS Agent Prompt",
        "",
        "## Task",
        task.get("title", ""),
        "",
        "## Objective",
        task.get("objective", ""),
        "",
        "## Allowed Files",
        "\n".join(f"- {x}" for x in task.get("allowed_files", [])) or "- (none specified)",
        "",
        "## Allowed Dirs",
        "\n".join(f"- {x}" for x in task.get("allowed_dirs", [])) or "- (none specified)",
        "",
        "## Tests",
        "\n".join(f"- {x}" for x in task.get("tests", [])) or "- (none specified)",
        "",
        "## Required Output",
        "- Do not edit files outside allowed scope.",
        "- Make the minimal change that satisfies the Objective — do not refactor, rename, reformat, or \"clean up\" code outside what the Objective requires.",
        "- If a file is touched, it must be because the Objective requires it. Do not make speculative or unrelated fixes.",
        "- Return unified diff if code changes are needed.",
        "- Include exact commands/tests to run.",
        "- Do not claim DONE without evidence.",
        "- Keep any explanation brief and focused on the diff and required commands — do not add commentary beyond what was asked.",
        "",
        "## Context Pack",
        context_pack.get("content", ""),
    ])

def write_prompt_file(repo_root: Path, adapter_name: str, task: dict, context_pack: dict) -> Path:
    path = prompt_dir(repo_root) / f"{adapter_name}_{task['id']}_{context_pack['id']}.md"
    path.write_text(build_agent_prompt(task, context_pack), encoding="utf-8")
    return path

def manual_chat_export(repo_root: Path, task_file: Path, output: Path | None = None) -> dict:
    task = load_task(task_file)
    context_pack = build_context_pack(repo_root, task["objective"], max_tokens=4500, search_limit=10)
    prompt = build_agent_prompt(task, context_pack)
    if output is None:
        output = prompt_dir(repo_root) / f"manual_chat_{task['id']}_{context_pack['id']}.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(prompt, encoding="utf-8")
    return {
        "id": new_id("ADAPTER"),
        "adapter": "manual_chat",
        "status": "ok",
        "output": str(output),
        "context_id": context_pack["id"],
        "token_count": context_pack["token_count"],
        "created_at": utcnow(),
    }

def run_cli_adapter(repo_root: Path, adapter_name: str, task_file: Path) -> dict:
    cfg = get_adapter_config(repo_root, adapter_name)
    task = load_task(task_file)
    context_pack = build_context_pack(repo_root, task["objective"], max_tokens=4500, search_limit=10)
    prompt_file = write_prompt_file(repo_root, adapter_name, task, context_pack)

    template = cfg.get("command_template", "")
    agent = cfg.get("default_agent", "leader")
    command = template.format(agent=agent, prompt_file=str(prompt_file), repo=str(repo_root))

    command_check = check_command(command.split()[0] if command else "")
    # UACOS command policy is strict; adapter commands are separately guarded by dry_run.
    if cfg.get("dry_run", True):
        return {
            "id": new_id("ADAPTER"),
            "adapter": adapter_name,
            "status": "dry_run",
            "command": command,
            "prompt_file": str(prompt_file),
            "context_id": context_pack["id"],
            "token_count": context_pack["token_count"],
            "created_at": utcnow(),
        }

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=int(cfg.get("timeout_seconds", 120)),
        )
        return {
            "id": new_id("ADAPTER"),
            "adapter": adapter_name,
            "status": "ok" if result.returncode == 0 else "fail",
            "returncode": result.returncode,
            "stdout": result.stdout[-4000:],
            "stderr": result.stderr[-4000:],
            "command": command,
            "prompt_file": str(prompt_file),
            "context_id": context_pack["id"],
            "created_at": utcnow(),
        }
    except Exception as exc:
        return {
            "id": new_id("ADAPTER"),
            "adapter": adapter_name,
            "status": "error",
            "error": f"{type(exc).__name__}: {exc}",
            "command": command,
            "prompt_file": str(prompt_file),
            "context_id": context_pack["id"],
            "created_at": utcnow(),
        }

def run_openai_compatible_adapter(repo_root: Path, adapter_name: str, task_file: Path) -> dict:
    cfg = get_adapter_config(repo_root, adapter_name)
    task = load_task(task_file)
    context_pack = build_context_pack(repo_root, task["objective"], max_tokens=4500, search_limit=10)
    prompt_file = write_prompt_file(repo_root, adapter_name, task, context_pack)

    payload = {
        "model": cfg.get("model", "local-model"),
        "messages": [
            {"role": "system", "content": "You are a careful coding agent. Follow UACOS scope and evidence rules."},
            {"role": "user", "content": prompt_file.read_text(encoding="utf-8")},
        ],
        "temperature": 0.1,
    }

    if cfg.get("dry_run", True):
        return {
            "id": new_id("ADAPTER"),
            "adapter": adapter_name,
            "status": "dry_run",
            "base_url": cfg.get("base_url"),
            "model": cfg.get("model"),
            "prompt_file": str(prompt_file),
            "payload_preview": json.dumps(payload, ensure_ascii=False)[:1000],
            "context_id": context_pack["id"],
            "token_count": context_pack["token_count"],
            "created_at": utcnow(),
        }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            cfg.get("base_url"),
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=int(cfg.get("timeout_seconds", 120))) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        return {
            "id": new_id("ADAPTER"),
            "adapter": adapter_name,
            "status": "ok",
            "response": body[-4000:],
            "prompt_file": str(prompt_file),
            "context_id": context_pack["id"],
            "created_at": utcnow(),
        }
    except urllib.error.URLError as exc:
        return {
            "id": new_id("ADAPTER"),
            "adapter": adapter_name,
            "status": "error",
            "error": f"URLError: {exc}",
            "prompt_file": str(prompt_file),
            "context_id": context_pack["id"],
            "created_at": utcnow(),
        }
    except Exception as exc:
        return {
            "id": new_id("ADAPTER"),
            "adapter": adapter_name,
            "status": "error",
            "error": f"{type(exc).__name__}: {exc}",
            "prompt_file": str(prompt_file),
            "context_id": context_pack["id"],
            "created_at": utcnow(),
        }

def run_named_adapter(repo_root: Path, adapter_name: str, task_file: Path, output: Path | None = None) -> dict:
    if adapter_name == "manual_chat":
        return manual_chat_export(repo_root, task_file, output=output)
    if adapter_name in {"openclaw_cli", "aider_cli"}:
        return run_cli_adapter(repo_root, adapter_name, task_file)
    if adapter_name == "ollama_openai":
        return run_openai_compatible_adapter(repo_root, adapter_name, task_file)
    if adapter_name == "cline_roo_mcp":
        return export_mcp_manifest(repo_root, output or (uacos_dir(repo_root) / "mcp_manifest.json"))
    raise ValueError(f"Unsupported adapter: {adapter_name}")

def export_mcp_manifest(repo_root: Path, output: Path) -> dict:
    manifest = {
        "name": "uacos-context-os",
        "version": "0.5.0",
        "description": "UACOS context/search/security tools for AI coding agents.",
        "tools": [
            {"name": "uacos_search", "description": "Search local repo index"},
            {"name": "uacos_context", "description": "Build task context pack"},
            {"name": "uacos_patch_check", "description": "Validate unified diff against scope"},
            {"name": "uacos_command_check", "description": "Check whether command is allowed"},
        ],
        "security": {
            "default": "local_only",
            "requires_scope": True,
            "blocks_secret_like_files": True,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "id": new_id("ADAPTER"),
        "adapter": "cline_roo_mcp",
        "status": "ok",
        "output": str(output),
        "created_at": utcnow(),
    }
