from __future__ import annotations

from copy import deepcopy

PRODUCT_POSITIONING = {
    "name": "UACOS",
    "category": "repo_brain_and_safety_gate",
    "one_liner": "Local-first repo intelligence, context compression, and patch safety for AI coding agents.",
    "is_not": [
        "a Goose clone",
        "a general-purpose chat agent",
        "a cloud-first coding assistant",
        "an unattended patch applier by default",
    ],
    "integrates_with": [
        "Goose",
        "Claude Code",
        "Codex",
        "OpenClaw",
        "Aider",
        "Cline",
        "manual chat workflows",
    ],
    "core_promise": [
        "select fewer, more relevant files before an AI run",
        "compress project context without hiding safety rules",
        "validate patch scope before changes touch the working tree",
        "scan added lines for secrets",
        "checkpoint and roll back automatically when tests fail",
        "measure token savings with repeatable local reports",
    ],
}

WORKFLOW_MODES = [
    {
        "name": "prepare",
        "purpose": "Build local project state before any AI edit.",
        "commands": [
            "uacos bootstrap --repo .",
            "uacos health --repo .",
            "uacos graph-build --repo .",
            "uacos compress-cache --repo .",
            "uacos auto --repo . --summary",
        ],
        "writes_code": False,
        "release_gate_required": False,
    },
    {
        "name": "assist",
        "purpose": "Give an external AI agent a bounded, task-specific context pack.",
        "commands": [
            "uacos impact --repo . --task '<task>'",
            "uacos context-compressed --repo . --task '<task>' --max-tokens 6000",
            "uacos mcp-serve --repo . --host 127.0.0.1 --port 8769",
        ],
        "writes_code": False,
        "release_gate_required": False,
    },
    {
        "name": "guard",
        "purpose": "Validate, apply, test, and roll back AI patches safely.",
        "commands": [
            "uacos patch-check --repo . --patch change.diff --allowed-file path/to/file.py",
            "uacos impact-alignment-check --repo . --task '<task>' --patch change.diff",
            "uacos autopilot-run --repo . --task-file .uacos/tasks/TASK-xxxx.json --apply --yes",
            "python scripts/release_gate.py",
        ],
        "writes_code": True,
        "release_gate_required": True,
    },
]

MCP_TOOL_CONTRACT = [
    {
        "name": "get_context",
        "priority": 1,
        "role": "Return the bounded context an AI agent should use instead of reading the whole repo.",
        "safe_by_default": True,
    },
    {
        "name": "get_memory",
        "priority": 2,
        "role": "Recall project-local lessons and constraints relevant to a task.",
        "safe_by_default": True,
    },
    {
        "name": "ingest_patch",
        "priority": 3,
        "role": "Validate and optionally apply a unified diff through transaction safety.",
        "safe_by_default": "validate_only_unless_apply_true",
    },
    {
        "name": "create_job",
        "priority": 4,
        "role": "Create a bounded runtime job with allowed files, allowed dirs, tests, and backend.",
        "safe_by_default": True,
    },
    {
        "name": "run_job",
        "priority": 5,
        "role": "Run one bounded job; real execution remains guarded by config.",
        "safe_by_default": "dry_run_unless_real_allowed",
    },
    {
        "name": "product_contract",
        "priority": 6,
        "role": "Expose UACOS positioning, supported workflows, and finite improvement plan to agent clients.",
        "safe_by_default": True,
    },
]

SESSION_PLAN = [
    {
        "session": 1,
        "title": "Positioning and workflow contract",
        "scope": [
            "make UACOS explicitly a repo brain/safety gate, not a general agent clone",
            "publish three product workflows: prepare, assist, guard",
            "expose the workflow contract through MCP for external agents",
        ],
        "files_allowed": [
            "uacos/product/*",
            "uacos/mcp/server.py",
            "docs/*",
            "README.md",
            "tests/*",
        ],
        "out_of_scope": [
            "compression algorithm changes",
            "transaction engine changes",
            "patch gate behavior changes",
            "provider/runtime backend changes",
            "desktop UI",
        ],
        "evidence_required": [
            "unit tests for product contract",
            "MCP self-test still passes",
            "release gate or CI must pass before final done",
        ],
    },
    {
        "session": 2,
        "title": "MCP compatibility hardening",
        "scope": [
            "validate JSON-RPC behavior against MCP-style clients",
            "add stable tool aliases only if they do not break existing tools",
            "add request/response contract tests",
        ],
        "files_allowed": ["uacos/mcp/*", "tests/*", "docs/*"],
        "out_of_scope": ["agent runtime rewrite", "network exposure beyond localhost"],
        "evidence_required": ["HTTP call test", "JSON-RPC call test", "localhost-only safety test"],
    },
    {
        "session": 3,
        "title": "Benchmark suite for real repos",
        "scope": [
            "add repeatable benchmark manifests",
            "measure selected files, raw tokens, compressed tokens, savings, and task success signal",
            "save reports without requiring cloud LLMs",
        ],
        "files_allowed": ["scripts/*", "evals/*", "docs/*", "tests/*"],
        "out_of_scope": ["claim 80-90% savings without benchmark evidence"],
        "evidence_required": ["self-repo benchmark", "sample repo benchmark", "report schema test"],
    },
    {
        "session": 4,
        "title": "Product command simplification",
        "scope": [
            "group the many CLI commands into prepare/assist/guard documentation and optional wrapper commands",
            "keep existing commands backward compatible",
            "make non-CLI onboarding shorter",
        ],
        "files_allowed": ["uacos/cli.py", "docs/*", "tests/*"],
        "out_of_scope": ["remove existing commands", "change working command semantics"],
        "evidence_required": ["CLI help smoke test", "prepare wrapper test", "release gate"],
    },
]


def get_workflow_modes():
    return deepcopy(WORKFLOW_MODES)


def get_session_plan():
    return deepcopy(SESSION_PLAN)


def get_product_contract(section=None):
    contract = {
        "status": "ok",
        "positioning": deepcopy(PRODUCT_POSITIONING),
        "workflow_modes": get_workflow_modes(),
        "mcp_tool_contract": deepcopy(MCP_TOOL_CONTRACT),
        "finite_session_plan": get_session_plan(),
    }
    if section is None:
        return contract
    if section not in contract:
        return {
            "status": "error",
            "reason": "unknown_section",
            "section": section,
            "available_sections": sorted(contract.keys()),
        }
    return {"status": "ok", section: contract[section]}
