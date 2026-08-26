from __future__ import annotations

from copy import deepcopy

from uacos.orchestrator.contract import get_orchestration_contract

PRODUCT_POSITIONING = {
    "name": "UACOS",
    "category": "repo_brain_orchestration_and_safety_gate",
    "one_liner": "Local-first repo intelligence, prompt/context optimizer, agent-code coordinator, and patch safety gate for AI coding workflows.",
    "is_not": [
        "a Goose clone",
        "a general-purpose chat agent",
        "a cloud-first coding assistant",
        "an unattended patch applier by default",
        "an unbounded autonomous loop",
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
        "save tokens by selecting fewer, more relevant files before an AI run",
        "optimize prompts through bounded context, repo memory, and reusable skills",
        "coordinate external agents and code operations without becoming a general chat agent",
        "validate patch scope before changes touch the working tree",
        "scan added lines for secrets",
        "checkpoint and roll back automatically when tests fail",
        "record each iteration so the loop can improve with evidence",
        "stop when the user spec is satisfied or the finite iteration budget is exhausted",
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
    {
        "name": "orchestrate",
        "purpose": "Coordinate a bounded DevOps-style loop across agents and code until the spec passes or the iteration budget is exhausted.",
        "commands": [
            "uacos mcp-serve --repo . --host 127.0.0.1 --port 8769",
            "MCP tool: orchestration_contract",
            "MCP tool: plan_orchestration_loop",
        ],
        "writes_code": "only_through_guard_mode",
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
    {
        "name": "orchestration_contract",
        "priority": 7,
        "role": "Expose UACOS core pillars and bounded DevOps loop rules for external agents.",
        "safe_by_default": True,
    },
    {
        "name": "plan_orchestration_loop",
        "priority": 8,
        "role": "Create a finite spec-driven loop plan; it does not execute agents or apply patches by itself.",
        "safe_by_default": True,
    },
]

SESSION_PLAN = [
    {
        "session": 1,
        "title": "Positioning and workflow contract",
        "scope": [
            "make UACOS explicitly a repo brain/safety gate, not a general agent clone",
            "publish product workflows: prepare, assist, guard",
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
        "title": "MCP orchestration contract hardening",
        "scope": [
            "validate JSON-RPC behavior against MCP-style clients",
            "publish core UACOS pillars: token/prompt optimization, safe code upgrade, agent-code coordination, and bounded spec-driven DevOps loop",
            "add safe MCP tools for orchestration contract and finite loop planning",
            "add request/response contract tests",
        ],
        "files_allowed": ["uacos/orchestrator/*", "uacos/mcp/*", "uacos/product/*", "tests/*", "docs/*"],
        "out_of_scope": ["agent runtime rewrite", "network exposure beyond localhost", "unbounded autonomous loops", "automatic patch application without guard mode"],
        "evidence_required": ["HTTP call test", "JSON-RPC call test", "localhost-only safety test", "finite-loop contract test"],
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
            "group the many CLI commands into prepare/assist/guard/orchestrate documentation and optional wrapper commands",
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
        "orchestration_contract": get_orchestration_contract(),
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
