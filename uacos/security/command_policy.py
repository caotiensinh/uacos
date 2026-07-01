import shlex

ALLOWED_COMMANDS = {
    "pytest", "python", "python3", "pip", "uv", "node", "npm", "pnpm",
    "yarn", "go", "cargo", "ruff", "mypy", "black", "isort", "git", "curl"
}

DANGEROUS_EXE = {"rm", "del", "erase", "format", "shutdown", "reboot", "mkfs", "dd", "diskpart", "reg", "sudo", "su", "chmod", "chown"}

DANGEROUS_SUBSTRINGS = ["rm -rf", "del /f", "format ", ":(){", ">/dev/sda", "| sh", "| bash", "invoke-expression", "iex "]

def check_command(command: str) -> dict:
    cmd = command.strip()
    if not cmd:
        return {"allowed": False, "reason": "empty_command", "command": command}

    low = cmd.lower()
    for bad in DANGEROUS_SUBSTRINGS:
        if bad in low:
            return {"allowed": False, "reason": f"dangerous_substring:{bad}", "command": command}

    try:
        parts = shlex.split(cmd, posix=False)
    except ValueError as exc:
        return {"allowed": False, "reason": f"parse_error:{exc}", "command": command}

    if not parts:
        return {"allowed": False, "reason": "empty_command", "command": command}

    exe = parts[0].split("/")[-1].split("\\")[-1].lower()

    if exe in DANGEROUS_EXE:
        return {"allowed": False, "reason": f"dangerous_executable:{exe}", "command": command}

    if exe not in ALLOWED_COMMANDS:
        return {"allowed": False, "reason": f"not_in_allowlist:{exe}", "command": command}

    if exe == "git" and len(parts) > 1:
        sub = parts[1].lower()
        allowed_git = {"status", "diff", "log", "show", "branch", "rev-parse", "ls-files", "grep"}
        if sub not in allowed_git:
            return {"allowed": False, "reason": f"git_subcommand_not_allowed:{sub}", "command": command}

    return {"allowed": True, "reason": "allowed", "command": command}
