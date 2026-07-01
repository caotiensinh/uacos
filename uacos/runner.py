"""
Compatibility runner for old free-text CLI mode.

Production rule for Phase 42:
- no direct mock answer path
- no separate LLM shortcut
- route through official llm33 runner so budget/cache/provider policy is enforced
"""

from pathlib import Path


def run(repo, task):
    from uacos.runtime.llm33_runner import llm_run_real

    repo_path = Path(repo).resolve()

    return llm_run_real(
        repo_path,
        str(task),
        size="small",
        real=False,
        max_context_tokens=6000,
    )
