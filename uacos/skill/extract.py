from __future__ import annotations
from pathlib import Path
import re
from uacos.skill.store import add_skill

ERROR_PATTERNS = [
    r"TypeError:.*", r"ModuleNotFoundError:.*", r"ImportError:.*", r"SyntaxError:.*",
    r"AssertionError:.*", r"FileNotFoundError:.*", r"PermissionError:.*",
    r"Traceback \(most recent call last\):", r"FAILED .*", r"ERROR .*",
]
COMMAND_RE = re.compile(r"(?im)^(?:python|py|pip|pytest|uacos|git|npm|node|go|cargo|ruff|mypy|black|isort)\b.*$")

def extract_problem_signatures(text: str) -> list[str]:
    out = []
    for pat in ERROR_PATTERNS:
        for m in re.finditer(pat, text, flags=re.MULTILINE):
            val = m.group(0).strip()
            if val not in out:
                out.append(val[:240])
    for kw in ["unsupported operand", "No module named", "not recognized", "command not found", "permission denied", "FTS5", "MATCH"]:
        if kw.lower() in text.lower() and kw not in out:
            out.append(kw)
    return out[:10]

def extract_commands(text: str) -> list[str]:
    out = []
    for m in COMMAND_RE.finditer(text):
        cmd = m.group(0).strip()
        if cmd not in out:
            out.append(cmd[:240])
    return out[:20]

def extract_skill_from_text(repo_root: Path, text: str, title: str, category: str = "general", source: str = "evidence", auto_approve: bool = False) -> dict:
    signatures = extract_problem_signatures(text)
    commands = extract_commands(text)
    lines = [line.strip() for line in text.splitlines() if line.strip()][:12]
    root_cause = ""
    solution_steps, verification = [], []
    for line in lines:
        lower = line.lower()
        if not root_cause and any(k in lower for k in ["root cause", "nguyên nhân", "cause", "because"]):
            root_cause = line
        if any(k in lower for k in ["fix", "solution", "sửa", "run ", "chạy ", "use "]):
            solution_steps.append(line)
        if any(k in lower for k in ["verify", "test", "kiểm tra", "uacos --help", "python --version"]):
            verification.append(line)
    if not root_cause and signatures:
        root_cause = "Observed problem signature: " + "; ".join(signatures[:3])
    if not solution_steps and commands:
        solution_steps = ["Run known working command sequence from evidence."]
    return add_skill(
        repo_root, title=title, problem_signatures=signatures, root_cause=root_cause,
        solution_steps=solution_steps, commands=commands, verification=verification,
        applies_to=[], category=category, source=source,
        confidence=0.65 if not auto_approve else 0.9,
        status="approved" if auto_approve else "candidate",
        tags=["auto_extracted"],
    )

def extract_skill_from_file(repo_root: Path, source_file: Path, title: str, category: str = "general", auto_approve: bool = False) -> dict:
    text = source_file.read_text(encoding="utf-8", errors="replace")
    return extract_skill_from_text(repo_root, text, title=title, category=category, source=str(source_file), auto_approve=auto_approve)
