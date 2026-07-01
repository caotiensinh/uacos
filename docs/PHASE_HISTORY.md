# UACOS Phase History

This file consolidates phase specifications and phase indexes that used to live as separate docs.

Generated: 2026-05-02T06:10:38.249844+00:00

## Source Files

- `PHASE_0_RESEARCH_MATRIX_UACOS.md` - PHASE 0 — Research Matrix & Architecture Notes
- `PHASE_1_LOCAL_INDEX_MVP.md` - Phase 1 — Local Index MVP
- `PHASE_2_REPO_INTELLIGENCE_MVP.md` - Phase 2 — Repo Intelligence MVP
- `PHASE_3_SECURITY_PATCH_GATE_MVP.md` - Phase 3 — Security + Patch Gate MVP
- `PHASE_4_AGENT_COORDINATION_MVP.md` - Phase 4 — Agent Integration & Coordination MVP
- `PHASE_5_REAL_ADAPTER_LAYER_MVP.md` - Phase 5 — Real Adapter Layer MVP
- `PHASE_6_EXECUTION_EVIDENCE_HARDENING_MVP.md` - Phase 6 — Execution & Evidence Hardening MVP
- `PHASE_7_APPLY_ROLLBACK_WORKSPACE_ISOLATION_MVP.md` - Phase 7 — Apply/Rollback & Workspace Isolation MVP
- `PHASE_8_MEMORY_REGRESSION_BRAIN_MVP.md` - Phase 8 — Memory System & Regression Brain MVP
- `PHASE_9_DASHBOARD_OPERATIONS_UI_MVP.md` - Phase 9 — Dashboard & Operations UI MVP
- `PHASE_10_PRODUCTION_PACKAGING_ONE_COMMAND_RUNNER_MVP.md` - Phase 10 — Production Packaging & One-Command Runner MVP
- `PHASE_11_SKILL_MEMORY_ENGINE.md` - Phase 11 — Skill Memory Engine
- `PHASE_12_VSCODE_INTEGRATION_LAYER.md` - Phase 12 — VSCode Integration Layer
- `PHASE_13_AUTO_LEARNING_LOOP.md` - Phase 13 — Auto-Learning Loop
- `PHASE_14_SEMANTIC_MEMORY_SEARCH.md` - Phase 14 — Semantic Memory / Local Search
- `PHASE_16_LLM_EXECUTION_LAYER.md` - Phase 16 — LLM Execution Layer
- `PHASE_17_SKILL_EXECUTION_ENGINE.md` - Phase 17 — Skill Execution Engine
- `PHASE_18_LEARNING_FEEDBACK_LOOP.md` - Phase 18 — Learning-to-Autopilot Feedback Loop
- `PHASE_19_AST_DEPENDENCY_GRAPH.md` - Phase 19 — AST / Dependency Graph Engine
- `PHASE_20_PRODUCTION_PATCH_ENGINE.md` - Phase 20 — Production Patch Engine
- `PHASE_21_PROVIDER_HARDENING.md` - Phase 21 — Real Provider Hardening
- `PHASE_22_CONTEXT_BUDGET_OPTIMIZER.md` - Phase 22 — Context Budget Optimizer
- `PHASE_23_VSCODE_PRODUCTION_LAYER.md` - Phase 23 — VSCode Production Layer
- `PHASE_24_OPENCLAW_ADAPTER_PRODUCTION.md` - Phase 24 — OpenClaw Adapter Production Layer
- `PHASE_25_PRODUCTION_DASHBOARD_METRICS.md` - Phase 25 — Production Dashboard + Metrics
- `PHASE_26_CONTEXT_COMPRESSION_ENGINE.md` - Phase 26 — Context Compression Engine
- `PHASE_27_TRANSACTIONAL_AUTOPILOT.md` - Phase 27 — Transactional Autopilot Execution + Rollback Chain
- `PHASE_28_TRUE_AGENT_RUNTIME.md` - Phase 28 — True Agent Runtime
- `PHASE_29_TEST_COVERAGE_HARDENING.md` - Phase 29 — Test Coverage Hardening
- `PHASE_30_REALRUN_E2E_VALIDATION.md` - Phase 30 — Real-run E2E Validation Layer
- `PHASE_31_MINIMAL_MCP_SERVER.md` - Phase 31 — Minimal MCP Server
- `PHASE_32_JS_TS_FULLSTACK_IMPACT.md` - Phase 32 — JS/TS AST + Full-stack Impact
- `PHASE_33_REAL_LLM_BUDGET_GUARD.md` - Phase 33 — Real LLM + Budget Guard
- `PHASE_34_TOKEN_CACHE_REUSE_ENGINE.md` - Phase 34 — Token Cache + Response Reuse Engine
- `UACOS_PHASE_INDEX_0_33.md` - UACOS Phase Index 0–33
- `UACOS_PHASE_INDEX_0_34.md` - UACOS Phase Index 0–34

## Consolidated Content

---

## Source: `PHASE_0_RESEARCH_MATRIX_UACOS.md`

# PHASE 0 — Research Matrix & Architecture Notes

**Project:** UACOS — Universal AI Context OS  
**Goal:** Build a lightweight, local-first, cloud-compatible context/memory/security/cost layer that helps AI agents work on large repositories without repeatedly reading the same files, wasting tokens, leaking secrets, or editing outside scope.

---

## 0. Core Principle

This project must **not** clone, download, embed, or vendor external projects into the codebase during Phase 0.

Phase 0 only preserves:

- architectural ideas
- reusable patterns
- security lessons
- cost/token-saving mechanisms
- integration models
- prioritization for later phases

The system should remain lightweight. External projects are references, not dependencies.

---

## 1. Final Direction After Research

The correct target is **not another AI coding agent**.

The correct target is:

```text
Universal AI Context OS
```

A middleware layer between repositories/data and any AI agent:

```text
Repo / Docs / Logs / Issues / DB
        |
        v
UACOS — Universal AI Context OS
        |
        +--> OpenClaw
        +--> Ollama / local LLM
        +--> ChatGPT / Codex
        +--> Claude / Claude Code
        +--> Cline / Roo Code
        +--> Aider / Continue
        +--> Any MCP-compatible agent
```

The agent should not freely read the whole repo. UACOS should scan, index, filter, compress, secure, and serve minimal context.

---

## 2. Phase Priority Scale

| Priority | Meaning | Apply When |
|---:|---|---|
| P0 | Mandatory foundation | MVP / Phase 1 |
| P1 | Strongly recommended | Phase 1–2 |
| P2 | Useful but not blocking | Phase 2–3 |
| P3 | Advanced / enterprise | Phase 4+ |
| Archive | Research only | Store for later, no implementation now |

---

## 3. Implementation Stage Tags

| Stage | Meaning |
|---|---|
| S1 | Local repo scanner + index |
| S2 | Context builder + token saving |
| S3 | Security gate + patch gate |
| S4 | Local LLM / OpenClaw integration |
| S5 | Cloud agent / MCP / REST integration |
| S6 | Observability + eval + enterprise hardening |
| Later | Keep as reference, not MVP |

---

## 4. Research Matrix — 70 Items

| # | Project / Skill | Category | Key Advantage to Keep | Avoid / Risk | Priority | Stage |
|---:|---|---|---|---|---:|---|
| 1 | Aider | AI coding agent | Repo map, symbol-level context, git diff workflow | Do not embed full Aider | P0 | S1-S2 |
| 2 | Srclight | Code intelligence | SQLite per repo, FTS5, tree-sitter, local embeddings, MCP | Do not require GPU | P0 | S1-S5 |
| 3 | Continue | AI checks | Source-controlled markdown checks | Do not depend on cloud PR flow | P0 | S3 |
| 4 | AGENTS.md | Agent standard | Portable project-specific instructions | Must avoid huge instruction files | P0 | S2-S5 |
| 5 | LiteLLM | LLM gateway | Unified model API, retry, fallback, budget | Do not add proxy complexity in MVP | P1 | S4-S6 |
| 6 | Gitleaks | Security | Secret scanning before context export | Do not verify secrets over network by default | P0 | S3 |
| 7 | Semgrep | Security | Lightweight rule-based static analysis | Avoid huge rulesets in MVP | P1 | S3-S6 |
| 8 | Mem0 / OpenMemory | Memory | Persistent memory for agents, MCP-friendly | Avoid cloud lock-in | P1 | S4-S5 |
| 9 | Graphiti | Memory | Temporal knowledge graph, evolving facts | Avoid graph DB dependency in MVP | P1 | S2-S4 |
| 10 | LlamaIndex | RAG framework | Ingest/index/retrieve abstraction | Avoid heavy integration sprawl | P2 | S2-S5 |
| 11 | OpenHands | Agent runtime | Runtime separation, workspace, sandbox pattern | Too heavy for MVP | P2 | Later |
| 12 | Cline | AI coding agent | Permissioned actions, MCP usage | Tool execution risk | P1 | S5 |
| 13 | Roo Code | AI coding agent | Mode-based agent roles | Avoid too many modes | P2 | S5 |
| 14 | Promptfoo | Eval | Prompt/agent/RAG regression testing | Not needed before MVP works | P2 | S6 |
| 15 | Langfuse | Observability | Tracing, prompt versioning, eval, cost visibility | Optional/self-host complexity | P2 | S6 |
| 16 | Portkey | Gateway | Guardrails, fallback, routing | Gateway complexity | P3 | S6 |
| 17 | Helicone | Cost | LLM cost analytics | Optional dependency | P2 | S6 |
| 18 | CodeQL | Security | Semantic vulnerability query | Heavy for MVP | P3 | S6 |
| 19 | TruffleHog | Security | Verified secret detection | Network verification disabled by default | P2 | S3-S6 |
| 20 | Microsoft GraphRAG | Knowledge graph | Private data graph reasoning | LLM-heavy indexing cost | P2 | Later |
| 21 | Qdrant | Vector DB | Production vector DB | Server dependency | P3 | Later |
| 22 | LanceDB | Vector DB | Local vector DB | Optional if SQLite enough | P2 | S2 |
| 23 | Chroma | Vector DB | Simple local vector store | Optional dependency | P2 | S2 |
| 24 | LangChain | Agent/RAG | Tool and chain ecosystem | Can become complex and opaque | P3 | Later |
| 25 | Haystack | RAG | Production RAG pipelines | Too broad for MVP | P3 | Later |
| 26 | txtai | Search | Lightweight embedding search | Optional | P2 | S2 |
| 27 | Sourcegraph | Code search | Cross-repo code intelligence | Too large to reproduce | Archive | Later |
| 28 | Zoekt | Code search | Fast trigram code search | Not necessary at small scale | P2 | Later |
| 29 | Tree-sitter | Parser | AST/symbol extraction | Manage language support gradually | P0 | S1 |
| 30 | Universal Ctags | Parser | Fallback symbol extraction | Less semantic than AST | P1 | S1 |
| 31 | ripgrep | Search | Fast keyword search | External binary availability | P0 | S1-S2 |
| 32 | SQLite FTS5 | Search | Local full-text search, zero server | Requires careful schema | P0 | S1-S2 |
| 33 | BM25 / RRF | Ranking | Hybrid keyword/vector ranking | Tune carefully | P0 | S2 |
| 34 | MCP | Protocol | Agent-tool interoperability | Security-sensitive | P1 | S5 |
| 35 | REST API | Protocol | Universal integration | Must protect endpoints | P0 | S5 |
| 36 | CLI | Protocol | Simple local automation | Must be stable | P0 | S1-S6 |
| 37 | OpenAI-compatible API | Protocol | Local/cloud adapter compatibility | Must not pretend to be full OpenAI API | P1 | S5 |
| 38 | OpenTelemetry | Observability | Standard tracing | Not needed early | P3 | S6 |
| 39 | Phoenix / Arize | Eval | LLM app evaluation | Later only | Archive | Later |
| 40 | Braintrust | Eval | Experiment tracking | Later only | Archive | Later |
| 41 | OPA / Rego | Policy | Policy-as-code | Too much for MVP | P3 | S6 |
| 42 | Docker sandbox | Security | Isolated command execution | Heavy on Windows/local dev | P2 | S3-S6 |
| 43 | Firejail / nsjail | Security | Linux sandbox | Linux-only | P3 | Later |
| 44 | pre-commit | Dev/security | Local enforcement hooks | Keep hook set small | P1 | S3 |
| 45 | Syft / Grype | Supply chain | SBOM and vulnerability scan | Enterprise phase | P3 | S6 |
| 46 | SLSA / Sigstore | Supply chain | Provenance and signing | Enterprise phase | P3 | Later |
| 47 | Goose | AI agent | Local-first MCP pattern | Not core dependency | Archive | S5 |
| 48 | Tabby | Local AI | Self-hosted code assistant | Not focused on context OS | Archive | Later |
| 49 | FauxPilot | Local AI | Copilot-compatible local endpoint | Autocomplete not core | Archive | Later |
| 50 | OpenCode | CLI agent | Terminal UX pattern | Not core | Archive | Later |
| 51 | Kilo Code | Coding agent | Multi-mode coding patterns | Not core | Archive | Later |
| 52 | Cursor pattern | IDE UX | Good context UX | Closed platform, pattern only | P2 | S5 |
| 53 | Windsurf pattern | IDE UX | Flow-based coding experience | Closed platform, pattern only | P2 | S5 |
| 54 | LM Studio | Local LLM | OpenAI-compatible local endpoint | User environment dependent | P1 | S4 |
| 55 | Ollama | Local LLM | Local models and embeddings | Model quality varies | P0 | S4 |
| 56 | vLLM | Inference | High-throughput server inference | Heavy for MVP | P3 | Later |
| 57 | llama.cpp | Inference | Lightweight CPU/GPU inference | Integration later | P2 | S4 |
| 58 | OpenRouter | Cloud router | Multi-provider fallback | Cloud cost/control | P1 | S5 |
| 59 | Groq / Together pattern | Inference | Cheap/fast hosted inference | Provider-dependent | P2 | S5 |
| 60 | Git worktree | Dev workflow | Isolated agent branches | Requires discipline | P1 | S3-S4 |
| 61 | Git diff / patch | Dev workflow | Safe patch review/apply | Must enforce scope | P0 | S3 |
| 62 | Git blame / hotspot | Context | Prioritize risky files | Later optimization | P2 | S2 |
| 63 | Test result cache | QA | Avoid rerunning expensive tests blindly | Must avoid stale false pass | P2 | S6 |
| 64 | Error memory | QA/memory | Remember recurring failures | Must invalidate after fix | P0 | S2-S4 |
| 65 | Decision log | Memory | Prevent old decisions resurfacing | Must be curated | P0 | S2 |
| 66 | Context fingerprint | Token saving | Avoid repeated context | Core token-saving feature | P0 | S2 |
| 67 | File hash summary | Token saving | Summary invalidation by hash | Core token-saving feature | P0 | S1-S2 |
| 68 | Scope lock | Safety | Prevent edit sprawl | Core safety gate | P0 | S3 |
| 69 | Command allowlist | Safety | Prevent dangerous shell | Core safety gate | P0 | S3-S5 |
| 70 | Context sanitizer | Safety | Remove secrets and prompt-injection risk | Core security gate | P0 | S2-S3 |

---

## 5. What Goes Into MVP

MVP must stay lightweight:

```text
Python + SQLite + ripgrep + tree-sitter + optional Ollama embeddings
```

Do **not** include in the MVP core:

```text
Qdrant
Milvus
Neo4j
LangChain full framework
OpenHands full runtime
Langfuse self-host
Portkey gateway
GraphRAG full pipeline
large vector infrastructure
```

---

## 6. MVP Modules

| Module | Priority | Stage | Purpose |
|---|---:|---|---|
| `uacos init` | P0 | S1 | Initialize `.uacos/` storage and rules |
| `uacos scan` | P0 | S1 | Index repo files, hashes, symbols |
| `uacos search` | P0 | S2 | Search relevant files/symbols/snippets |
| `uacos context` | P0 | S2 | Build minimal context pack for an agent |
| `uacos patch-check` | P0 | S3 | Validate diff scope/security/test requirements |
| `uacos memory` | P0 | S2 | Store project truths, decisions, errors |
| `uacos token-report` | P0 | S2-S6 | Track token usage and saved context |
| `uacos serve-api` | P1 | S5 | REST integration for agents/tools |
| `uacos serve-mcp` | P1 | S5 | MCP integration for Claude/Cline/Roo/etc. |
| `uacos route` | P1 | S4-S5 | Choose local/cloud model by cost policy |

---

## 7. Core Architecture v0

```text
UACOS
|
├── Repo Intelligence
│   ├── file scanner
│   ├── ignore engine
│   ├── hash/mtime cache
│   ├── tree-sitter symbol index
│   ├── dependency graph
│   └── repo map builder
|
├── Retrieval Engine
│   ├── SQLite FTS5
│   ├── optional local embedding
│   ├── hybrid ranker
│   ├── snippet extractor
│   └── context pack builder
|
├── Memory Engine
│   ├── project truth
│   ├── task memory
│   ├── decision memory
│   ├── error memory
│   ├── temporal facts
│   └── invalidation
|
├── Security Gate
│   ├── secret scanner
│   ├── prompt injection filter
│   ├── command allowlist
│   ├── file scope lock
│   └── patch validator
|
├── Cost Engine
│   ├── token counter
│   ├── model router
│   ├── context fingerprint
│   ├── cache hit tracker
│   └── cost report
|
└── Integration Layer
    ├── CLI
    ├── REST API
    ├── MCP server
    ├── OpenAI-compatible endpoint
    ├── AGENTS.md generator
    └── file-based context export
```

---

## 8. Core Data Model v0

### 8.1 Files

```sql
CREATE TABLE files (
  id INTEGER PRIMARY KEY,
  path TEXT UNIQUE,
  sha256 TEXT,
  mtime REAL,
  language TEXT,
  size_bytes INTEGER,
  is_generated INTEGER DEFAULT 0,
  risk_level TEXT DEFAULT 'normal',
  summary TEXT,
  last_indexed_at TEXT
);
```

### 8.2 Symbols

```sql
CREATE TABLE symbols (
  id INTEGER PRIMARY KEY,
  file_id INTEGER,
  name TEXT,
  kind TEXT,
  start_line INTEGER,
  end_line INTEGER,
  signature TEXT,
  summary TEXT,
  FOREIGN KEY(file_id) REFERENCES files(id)
);
```

### 8.3 Memory

```sql
CREATE TABLE memories (
  id INTEGER PRIMARY KEY,
  kind TEXT,
  key TEXT,
  value TEXT,
  source TEXT,
  confidence REAL,
  valid_at TEXT,
  invalid_at TEXT,
  created_at TEXT,
  updated_at TEXT
);
```

### 8.4 Context Packs

```sql
CREATE TABLE context_packs (
  id TEXT PRIMARY KEY,
  task_hash TEXT,
  files_hash TEXT,
  rules_hash TEXT,
  memory_hash TEXT,
  content TEXT,
  token_count INTEGER,
  created_at TEXT
);
```

### 8.5 Token Ledger

```sql
CREATE TABLE token_usage (
  id INTEGER PRIMARY KEY,
  ts TEXT,
  agent TEXT,
  model TEXT,
  task_id TEXT,
  input_tokens INTEGER,
  output_tokens INTEGER,
  estimated_cost_usd REAL,
  cache_hit INTEGER,
  context_id TEXT
);
```

---

## 9. Security Rules v0

### 9.1 Files Never Sent to LLM by Default

```text
.env
.env.*
*.pem
*.key
*.p12
*.pfx
*.sqlite
*.db
*.dump
id_rsa
id_ed25519
credentials.json
secrets.*
node_modules/
.venv/
venv/
dist/
build/
.git/
__pycache__/
```

### 9.2 Mandatory Gates

```text
1. Context sanitizer before context export.
2. Secret scanner before cloud agent usage.
3. Scope lock before patch apply.
4. Command allowlist before agent shell execution.
5. Patch validator before reporting DONE.
```

### 9.3 Prompt Injection Defense

Repo files, logs, docs, issues, and comments are treated as **data**, not instructions.

Only trusted rule files can issue instructions:

```text
rules/AGENTS.md
rules/security.md
rules/coding_policy.md
rules/token_budget.md
rules/no_placeholder.md
```

---

## 10. Token-Saving Rules v0

```text
1. Never send the full repo to any agent.
2. Build context from file hashes, symbols, summaries, and snippets.
3. Every context pack must have a context_id fingerprint.
4. If context is unchanged, send only delta/diff.
5. Store file summaries by sha256; invalidate when file changes.
6. Use local LLM for classification, summarization, search, and log parsing.
7. Use cloud/premium model only for high-value reasoning or final review.
8. Record all token usage in token_ledger.sqlite.
```

---

## 11. Agent Compatibility Model

UACOS must not depend on a single agent.

Supported integration surfaces:

| Integration | Target |
|---|---|
| CLI | OpenClaw, local scripts, Aider-like workflow |
| REST API | Custom web/agent tools |
| MCP Server | Claude Code, Cline, Roo, Cursor-like tools |
| OpenAI-compatible API | Ollama, LM Studio, vLLM, LiteLLM-style routing |
| Context Pack Export | ChatGPT web, Claude web, manual workflow |
| AGENTS.md | Any coding agent supporting project instructions |
| Git Patch | Universal safe edit format |

---

## 12. Stage Roadmap

### Phase 1 — Local Index MVP

Goal: make the repo searchable and summarizable without reading everything repeatedly.

Deliverables:

```text
- uacos init
- uacos scan
- SQLite file index
- ignore rules
- file hash cache
- tree-sitter symbol extraction for Python/JS/TS/Go first
- FTS5 keyword search
```

### Phase 2 — Context Builder + Memory

Goal: produce minimal context packs for any agent.

Deliverables:

```text
- uacos search
- uacos context
- context fingerprint
- file summary by hash
- project truth memory
- decision memory
- error memory
- temporal invalidation
```

### Phase 3 — Security + Patch Gate

Goal: stop secret leaks and uncontrolled agent edits.

Deliverables:

```text
- secret scanner
- context sanitizer
- file scope lock
- command allowlist
- patch validator
- pre-commit integration
```

### Phase 4 — Local Agent Integration

Goal: integrate with OpenClaw and local LLMs.

Deliverables:

```text
- OpenClaw adapter
- Ollama adapter
- local model router
- token ledger
- local-first mode
```

### Phase 5 — Cloud Agent / MCP Integration

Goal: support Claude, ChatGPT/Codex, Cline, Roo, and other external agents.

Deliverables:

```text
- MCP server
- REST API
- OpenAI-compatible endpoint
- context pack export
- AGENTS.md generator
```

### Phase 6 — Observability + Eval + Enterprise

Goal: production quality and measurable cost reduction.

Deliverables:

```text
- token/cost dashboard
- context reuse report
- eval runner
- prompt regression tests
- optional Langfuse/Helicone/LiteLLM integration
- optional Semgrep/CodeQL advanced scanning
```

---

## 13. Keep-for-Later Archive

These are valuable but should not be implemented now:

```text
- Full GraphRAG indexing
- Neo4j graph backend
- Milvus/Qdrant server deployment
- LangChain full orchestration
- OpenHands full runtime clone
- Enterprise SLSA/Sigstore pipeline
- Full CodeQL integration
- Distributed multi-repo index
- IDE UI plugin
- Web dashboard
```

They should remain in research notes and be revisited only after Phase 1–3 are stable.

---

## 14. Final Phase 0 Decisions

1. UACOS is a context/memory/security/cost middleware, not another AI agent.
2. MVP is local-first and lightweight.
3. SQLite is the default storage.
4. Tree-sitter + FTS5 + hash cache are core.
5. Vector search is optional, not mandatory.
6. MCP/REST/OpenAI-compatible API are integration surfaces, not core logic.
7. Security gate is mandatory before cloud agent usage.
8. Patch gate is mandatory before any agent edit is accepted.
9. External projects are references only.
10. Research is preserved here to avoid repeating Phase 0.

---

## 15. Next Action

Proceed to **Phase 1 — Local Index MVP**.

Recommended first implementation order:

```text
1. Create repo skeleton
2. Implement ignore rules
3. Implement file scanner
4. Implement SQLite schema
5. Implement hash cache
6. Implement FTS5 search
7. Add tree-sitter symbol parser
8. Add CLI: init, scan, search
9. Add tests
10. Write Phase 1 evidence report
```

---

## Source: `PHASE_1_LOCAL_INDEX_MVP.md`

# Phase 1 — Local Index MVP

## Objective

Build the first runnable UACOS component: a local repository index that prevents AI agents from repeatedly reading entire repositories.

## Scope

Phase 1 includes:

1. Local `.uacos` storage
2. SQLite database
3. File scanner
4. Ignore rules
5. SHA-256 hash cache
6. Basic language detection
7. SQLite FTS5 full-text search
8. CLI commands:
   - `uacos init`
   - `uacos scan`
   - `uacos search`
   - `uacos stats`

## Explicit Non-goals

Phase 1 does not include:

- Tree-sitter symbol parsing
- Embeddings
- MCP server
- REST API
- Patch gate
- Agent adapters
- Cloud model routing

These are intentionally deferred to avoid making the project heavy.

## Priority

P0 / S1

This phase is foundational. Every later phase depends on the local repo index.

## Acceptance Criteria

- `uacos init --repo <repo>` creates `<repo>/.uacos/repo_index.sqlite`
- `uacos scan --repo <repo>` indexes text/code files
- secret-like filenames are skipped
- generated/heavy folders are ignored
- repeated scans only re-index changed files by SHA-256
- `uacos search --repo <repo> "<query>"` returns matching files/snippets
- `uacos stats --repo <repo>` reports file and language counts

## Security Position

Phase 1 does not send anything to cloud services. It only reads local files and stores local indexes.

Files such as `.env`, `*.pem`, `*.key`, binary files, DB files and large logs are skipped by default.

---

## Source: `PHASE_2_REPO_INTELLIGENCE_MVP.md`

# Phase 2 — Repo Intelligence MVP

## Included from Previous Phases

- Phase 0 research matrix
- Phase 1 local index MVP
- All Phase 1 commands

## New Features

- Symbol extraction
- `symbols` and `symbols_fts`
- Snippet extraction
- Repo map builder
- Context pack builder v0
- New CLI: `symbols`, `snippets`, `repomap`, `context`

## Important Design Choice

Phase 2 uses lightweight regex extraction, not tree-sitter yet.

This is not placeholder-only behavior. It parses real source files, extracts symbols, stores them in SQLite, searches them, and builds repo maps/context packs.

Tree-sitter is deferred so the MVP is easy to run on Windows/Linux with no dependency problems.

## Acceptance Criteria

- `uacos scan` indexes files and symbols
- `uacos stats` reports symbol counts
- `uacos symbols --query <name>` returns symbols
- `uacos snippets` returns line-numbered code snippets
- `uacos repomap` builds compact markdown
- `uacos context` builds and stores context pack
- Tests pass

---

## Source: `PHASE_3_SECURITY_PATCH_GATE_MVP.md`

# Phase 3 — Security + Patch Gate MVP

## Objective

Phase 3 adds local safety gates before AI-generated changes are accepted.

## New Modules

```text
uacos/security/secret_scan.py
uacos/security/diff_parser.py
uacos/security/patch_gate.py
uacos/security/command_policy.py
```

## New CLI

```bash
uacos security-scan --repo <repo>
uacos patch-check --repo <repo> --patch <diff> --allowed-file <path>
uacos command-check "pytest -q"
```

## Detects / Blocks

- secret-like filenames: `.env`, private keys
- generic API key / token assignments
- AWS access keys
- GitHub tokens
- private key blocks
- JWT-like strings
- patch scope violations
- sensitive file edits
- dangerous shell commands

## Limitations

This is a lightweight local-first gate. It does not replace Gitleaks, Semgrep, CodeQL or a real sandbox. Those remain optional integrations for later phases.

---

## Source: `PHASE_4_AGENT_COORDINATION_MVP.md`

# Phase 4 — Agent Integration & Coordination MVP

## Objective

Phase 4 adds an agent coordination layer. It is not just a connector layer.

The goal is to make multiple AI agents work in a controlled workflow:

```text
Task -> Context Pack -> Role Assignments -> Safety Gates -> Agent Steps -> Evidence Report
```

## New Concepts

### Agent Registry

Stored at:

```text
.uacos/agents.json
```

Default agents:

- planner
- coder
- reviewer
- tester

Each agent has:

- role
- adapter
- model
- priority
- edit permission
- command permission

### Task Spec

Stored at:

```text
.uacos/tasks/TASK-*.json
```

Task contains:

- title
- objective
- allowed files
- allowed directories
- forbidden files
- tests
- commands
- risk level

### Workflow Plan

Stored at:

```text
.uacos/plans/PLAN-*.json
```

Plan contains role assignments and gates.

### Workflow Run

Stored at:

```text
.uacos/runs/RUN-*.json
```

Run contains:

- task
- context ID
- context token estimate
- preflight result
- patch check result
- agent step results
- final status

## Adapters

Phase 4 includes two real safe adapters:

- `dry_run`: deterministic safe adapter for orchestration validation
- `local_echo`: local adapter that receives and echoes context preview

No external AI API is called yet. This is deliberate so the coordination layer can be tested safely before connecting OpenClaw/Claude/ChatGPT.

## Safety Gates

Workflow enforces:

- context pack required
- command allowlist required
- patch scope check if patch is provided
- evidence report required

## CLI

```bash
uacos agent-init --repo <repo>
uacos agent-list --repo <repo>
uacos task-create --repo <repo> --title "..." --objective "..." --allowed-file app.py --test "pytest -q"
uacos task-plan --repo <repo> --task-file .uacos/tasks/TASK-xxx.json
uacos workflow-run --repo <repo> --task-file .uacos/tasks/TASK-xxx.json
uacos evidence-report --repo <repo> --run-id RUN-xxx
```

## What This Enables Later

- OpenClaw adapter
- Claude Code adapter
- ChatGPT/Codex adapter
- Cline/Roo MCP adapter
- Aider adapter
- REST API
- MCP server
- dashboard

---

## Source: `PHASE_5_REAL_ADAPTER_LAYER_MVP.md`

# Phase 5 — Real Adapter Layer MVP

## Objective

Phase 5 connects UACOS to external/local AI agents through safe adapter interfaces.

This phase does not yet require real cloud/API calls. It implements the adapter layer with safe dry-run behavior by default.

## New Adapter Types

### manual_chat

Exports a complete agent prompt/context file for ChatGPT, Claude, Gemini, or any web chat.

### openclaw_cli

Creates a prompt file and prepares a command like:

```bash
/home/aiserver/ai-team/executor/chat.sh leader <prompt_file>
```

Default is dry-run.

### aider_cli

Creates a prompt file and prepares:

```bash
aider --message-file <prompt_file>
```

Default is dry-run.

### ollama_openai

Builds an OpenAI-compatible HTTP payload for local Ollama/LM Studio/vLLM endpoints.

Default is dry-run.

### cline_roo_mcp

Exports a MCP manifest skeleton so Cline/Roo-compatible systems can discover UACOS tools later.

## New Files

```text
uacos/agent/adapter_config.py
uacos/agent/real_adapters.py
.uacos/adapters.json
.uacos/adapter_prompts/
.uacos/mcp_manifest.json
```

## New CLI

```bash
uacos adapter-init --repo <repo>
uacos adapter-list --repo <repo>
uacos adapter-export --repo <repo> --adapter manual_chat --task-file <task> --output context.md
uacos adapter-run --repo <repo> --adapter openclaw_cli --task-file <task>
uacos adapter-run --repo <repo> --adapter aider_cli --task-file <task>
uacos adapter-run --repo <repo> --adapter ollama_openai --task-file <task>
uacos mcp-manifest --repo <repo> --output .uacos/mcp_manifest.json
```

## Safety

All real adapters default to `dry_run: true`.

To actually call a local agent/API, edit:

```text
.uacos/adapters.json
```

and set the target adapter `dry_run` to false.

## Integration Principle

UACOS remains the control plane:

```text
repo index -> context pack -> adapter prompt -> external/local agent -> patch/evidence -> UACOS gates
```

Agents do not get raw repo access by default. They receive scoped context packs.

---

## Source: `PHASE_6_EXECUTION_EVIDENCE_HARDENING_MVP.md`

# Phase 6 — Execution & Evidence Hardening MVP

## Objective

Phase 6 closes the loop after an agent produces output.

It adds:

1. Agent output ingestion
2. Unified diff extraction
3. Patch validation against task scope
4. Safe test command execution
5. Token/cost ledger
6. Failed task memory
7. Evidence report v2

## New Modules

```text
uacos/execution/diff_extract.py
uacos/execution/test_runner.py
uacos/execution/token_ledger.py
uacos/execution/failed_memory.py
uacos/execution/artifacts.py
```

## New CLI

```bash
uacos artifact-ingest --repo <repo> --task-file <task> --agent-output <file>
uacos extract-diff --agent-output <file> --output extracted.diff
uacos test-run --repo <repo> --task-file <task>
uacos token-log --repo <repo> --task-id TASK --agent coder --model local --input-tokens 100 --output-tokens 50
uacos token-summary --repo <repo>
uacos failed-memory --repo <repo>
uacos evidence-v2 --repo <repo> --task-file <task> --agent-output <file> --run-tests --output evidence.md
```

## Safety

- Extracted patch is not applied automatically.
- Patch must pass Phase 3 patch gate.
- Tests use command allowlist.
- Dangerous commands are blocked.
- Failures are recorded for future memory.

---

## Source: `PHASE_7_APPLY_ROLLBACK_WORKSPACE_ISOLATION_MVP.md`

# Phase 7 — Apply/Rollback & Workspace Isolation MVP

## Objective

Phase 7 adds controlled patch application with rollback and DONE gating.

## New CLI

```bash
uacos apply-patch --repo <repo> --task-file <task> --patch <diff>
uacos rollback --repo <repo> --manifest <manifest>
uacos done-gate --repo <repo> --manifest <manifest>
uacos manifest-list --repo <repo>
```

## Safety

- Patch is blocked if scope/security check fails.
- Files are backed up before write.
- Post-apply tests run by default.
- Failed tests auto-rollback by default.
- Final DONE gate requires applied status, passed patch check, tests pass, and no rollback.

---

## Source: `PHASE_8_MEMORY_REGRESSION_BRAIN_MVP.md`

# Phase 8 — Memory System & Regression Brain MVP

## Objective

Phase 8 adds long-term memory so AI agents do not repeat research, forget project truths, or break fragile areas again.

## New Modules

```text
uacos/memory/store.py
uacos/memory/regression.py
```

## New CLI

```bash
uacos memory-add --repo <repo> --kind project_truth --key port --value "frontend port is 3035"
uacos memory-list --repo <repo>
uacos memory-search --repo <repo> "barrier"
uacos memory-invalidate --repo <repo> --memory-id MEM-xxx --reason "old spec"
uacos regression-rule-add --repo <repo> --title "Do not touch video pipeline" --pattern "backend/video_pipeline.py" --severity high
uacos regression-check --repo <repo> --patch change.diff
uacos context-memory --repo <repo> --task "fix barrier open"
```

## Memory Kinds

- project_truth
- decision
- error
- failure
- deprecated
- regression_rule
- note

## Context Injection

`build_context_pack()` now injects a `Relevant Memory` section based on task search.

## Regression Brain

Regression rules are stored as memory and checked against patch file paths.
High/critical matches fail the regression check.

---

## Source: `PHASE_9_DASHBOARD_OPERATIONS_UI_MVP.md`

# Phase 9 — Dashboard & Operations UI MVP

## Objective

Phase 9 adds a lightweight local web dashboard so UACOS can be operated without remembering every CLI command.

## New Modules

```text
uacos/dashboard/server.py
uacos/dashboard/ops_summary.py
```

## New CLI

```bash
uacos dashboard --repo <repo> --host 127.0.0.1 --port 8765
uacos ops-summary --repo <repo>
```

## Dashboard Features

- Repo statistics
- Scan button
- Search UI
- Context pack builder
- Memory viewer/search
- Token ledger viewer
- Failed-task memory viewer
- Change manifest viewer
- API endpoint list
- EN/VI/JA language switch

## API Endpoints

```text
/api/summary
/api/stats
/api/scan
/api/search?q=...
/api/context?task=...
/api/memory?q=...
/api/token-ledger
/api/failures
/api/manifests
```

## Design Choice

Uses only Python standard library `http.server`.
No Flask/FastAPI/Dash dependency is added in this phase.

---

## Source: `PHASE_10_PRODUCTION_PACKAGING_ONE_COMMAND_RUNNER_MVP.md`

# Phase 10 — Production Packaging & One-Command Runner MVP

## Objective

Phase 10 makes UACOS easier to deploy, run, backup, and verify.

## New Module

```text
uacos/ops/packaging.py
```

## New CLI

```bash
uacos bootstrap --repo <repo>
uacos health --repo <repo>
uacos doctor --repo <repo> --fix
uacos backup --repo <repo> --output uacos_backup.zip
uacos export --repo <repo> --output uacos_export.zip
uacos import --repo <repo> --input uacos_export.zip --overwrite
uacos release-check --repo <repo>
uacos write-run-scripts --repo <repo> --output-dir ops
uacos write-systemd --repo <repo> --output ops/uacos-dashboard.service
```

---

## Source: `PHASE_11_SKILL_MEMORY_ENGINE.md`

# Phase 11 — Skill Memory Engine

## Objective

Phase 11 upgrades UACOS from project memory to reusable engineering skill memory.

A skill is a reusable structured experience unit:

```text
problem signature -> root cause -> solution steps -> commands -> verification
```

## New Modules

```text
uacos/skill/store.py
uacos/skill/extract.py
```

## New CLI

```bash
uacos skill-add
uacos skill-list
uacos skill-search
uacos skill-suggest
uacos skill-extract
uacos skill-approve
uacos skill-reject
uacos skill-deprecate
uacos skill-use
uacos skill-review
uacos context-skills
```

## Skill Lifecycle

```text
candidate -> approved -> used many times
candidate -> rejected
approved -> deprecated
```

## Context Injection

`uacos context` now injects:

```text
## Relevant Skills
```

This allows AI agents to reuse prior fix patterns without rereading or re-solving everything.

## Phase 11 Safety Rule

Skills are not blindly auto-approved unless explicitly requested with `--auto-approve`.
Default extraction creates `candidate` skills for review.

---

## Source: `PHASE_12_VSCODE_INTEGRATION_LAYER.md`

# Phase 12 — VSCode Integration Layer

## Objective

Phase 12 makes UACOS easier to use inside VSCode.

## New Module

```text
uacos/ide/vscode.py
```

## New CLI

```bash
uacos vscode-init --repo <repo> --port 8765 --overwrite
uacos vscode-extension-skeleton --output-dir vscode-uacos --overwrite
uacos vscode-workspace --repo <repo> --output project.code-workspace
```

## Generated VSCode Files

```text
.vscode/tasks.json
.vscode/settings.json
.vscode/launch.json
```

## Generated Tasks

- UACOS: Bootstrap
- UACOS: Health Check
- UACOS: Scan Repo
- UACOS: Open Dashboard
- UACOS: Ops Summary
- UACOS: Memory List
- UACOS: Skill Review
- UACOS: Manifest List

---

## Source: `PHASE_13_AUTO_LEARNING_LOOP.md`

# Phase 13 — Auto-Learning Loop

## Objective

Phase 13 turns successful/failed work into reusable learning assets.

```text
evidence/failure/manifest
→ classify
→ extract candidate skill
→ create memory
→ detect duplicate skills
→ add learning event
→ review/approve
→ future context reuses skill
```

## New Module

```text
uacos/learning/auto.py
```

## New CLI

```bash
uacos learn-from-evidence --repo <repo> --source-file evidence.md --title "Fix Python venv mismatch"
uacos learn-from-failure --repo <repo> --source-file failure.md --title "Fix failed test"
uacos learn-from-manifest --repo <repo> --manifest .uacos/change_manifests/CHANGE-xxx.json
uacos learn-review --repo <repo>
uacos learn-summary --repo <repo>
uacos learn-event-list --repo <repo>
```

## Safety

- New skills are `candidate` by default.
- Auto-approve requires explicit `--auto-approve`.
- Learning events are logged in `.uacos/learning_events.jsonl`.
- Auto-created memories are tagged with `auto_learning`.

## Why This Matters

UACOS can now learn from real work and prepare reusable skills for future context packs.

---

## Source: `PHASE_14_SEMANTIC_MEMORY_SEARCH.md`

# Phase 14 — Semantic Memory / Local Search

## Objective

Phase 14 adds local semantic search for UACOS memory and skills.

## New Module

```text
uacos/semantic/search.py
```

## New CLI

```bash
uacos semantic-index --repo <repo>
uacos semantic-search --repo <repo> "query"
uacos semantic-skills --repo <repo> "query"
uacos semantic-memories --repo <repo> "query"
uacos semantic-context --repo <repo> --task "task"
```

## Design

- No cloud
- No external package
- Deterministic local TF-IDF sparse vectors
- Stores `.uacos/semantic_index.json`
- Searches both skills and memories
- Context pack now includes semantic results

## Why Not Heavy Vector DB Yet

Phase 14 keeps the system lightweight and portable. A future phase can add optional Ollama embedding or FAISS/SQLite vector support.

---

## Source: `PHASE_16_LLM_EXECUTION_LAYER.md`

# Phase 16 — LLM Execution Layer

## Added

- `uacos/llm/providers.py`
- `uacos/compression/context.py`
- LLM provider config with dry-run default
- Ollama provider
- OpenAI-compatible provider
- Context compression
- Patch apply support for new file creation

## CLI

```bash
uacos llm-init --repo <repo>
uacos llm-config --repo <repo>
uacos llm-enable --repo <repo> --provider ollama
uacos llm-run --repo <repo> --provider ollama --prompt "..."
uacos context-compress --repo <repo> --task "..."
```

---

## Source: `PHASE_17_SKILL_EXECUTION_ENGINE.md`

# Phase 17 — Skill Execution Engine

## Objective

Phase 17 turns approved skills into controlled executable playbooks.

## New Module

```text
uacos/skill/executor.py
```

## New CLI

```bash
uacos skill-plan --repo <repo> --skill-id SKILL-xxx
uacos skill-execute --repo <repo> --skill-id SKILL-xxx
uacos skill-execute --repo <repo> --skill-id SKILL-xxx --yes-run
uacos skill-execute-best --repo <repo> --task "..."
uacos skill-exec-history --repo <repo>
uacos skill-exec-summary --repo <repo>
```

## Safety

- Skills must be `approved`.
- Dry-run by default.
- Commands must match safe allowlist.
- Dangerous shell tokens are blocked.
- Execution evidence is written to `.uacos/skill_executions`.

---

## Source: `PHASE_18_LEARNING_FEEDBACK_LOOP.md`

# Phase 18 — Learning-to-Autopilot Feedback Loop

## Objective

Phase 18 closes the loop between skill execution results and future recommendations.

## New Module

```text
uacos/learning/feedback.py
```

## New CLI

```bash
uacos feedback-ingest-execution --repo <repo> --execution-file <file>
uacos feedback-ingest-execution --repo <repo> --all
uacos feedback-ingest-autopilot --repo <repo> --run-id AUTO-xxxx
uacos feedback-summary --repo <repo>
uacos feedback-skill-score --repo <repo> --skill-id SKILL-xxxx
uacos feedback-recommend --repo <repo> --task "..."
uacos feedback-events --repo <repo>
```

## Scoring

Each skill gets:

- success_count
- failure_count
- blocked_count
- dry_run_count
- reliability
- confidence_delta
- activity

Recommendations combine keyword/skill search score with feedback reliability.

---

## Source: `PHASE_19_AST_DEPENDENCY_GRAPH.md`

# Phase 19 — AST / Dependency Graph Engine

## Objective

Phase 19 improves context accuracy by adding Python AST parsing and dependency graph analysis.

## New Modules

```text
uacos/ast_engine/parser.py
uacos/graph/builder.py
uacos/graph/query.py
uacos/impact/analyzer.py
```

## New CLI

```bash
uacos ast-scan --repo <repo>
uacos graph-build --repo <repo>
uacos graph-query --repo <repo> --symbol create_user
uacos graph-related --repo <repo> --file service.py
uacos impact --repo <repo> --symbol create_user
uacos impact --repo <repo> --task "fix db error"
uacos context-smart --repo <repo> --task "fix create_user bug"
```

## Storage

```text
.uacos/graph/ast_index.json
.uacos/graph/dependency_graph.json
.uacos/smart_context/latest_smart_context.md
```

---

## Source: `PHASE_20_PRODUCTION_PATCH_ENGINE.md`

# Phase 20 — Production Patch Engine

## Objective

Phase 20 hardens patch workflows for realistic AI coding tasks.

## New Module

```text
uacos/patching/engine.py
```

## New CLI

```bash
uacos patch20-parse --patch change.diff
uacos patch20-validate --repo <repo> --patch change.diff --allowed-file app.py
uacos patch20-apply --repo <repo> --patch change.diff --dry-run
uacos patch20-apply --repo <repo> --patch change.diff --test "python -m pytest -q"
uacos patch20-rollback --repo <repo> --manifest .uacos/patch_runs/PATCH-xxx/manifest.json
```

## Supported Operations

- modify existing file
- create new file
- delete file
- rename file
- rename + modify
- multi-file patch validation
- dry-run planning
- rollback

---

## Source: `PHASE_21_PROVIDER_HARDENING.md`

# Phase 21 — Real Provider Hardening

## Objective

Phase 21 hardens LLM provider execution for safer production use.

## New Module

```text
uacos/llm/hardened.py
```

## New CLI

```bash
uacos provider-health --repo <repo>
uacos provider-health --repo <repo> --provider ollama --real
uacos llm-run-hardened --repo <repo> --prompt "..." --dry-run
uacos model-route-set --repo <repo> --name coding --provider ollama --model qwen2.5-coder:7b --keyword code
uacos model-route-test --repo <repo> --task "fix code bug"
uacos provider-summary --repo <repo>
uacos provider-history --repo <repo>
uacos token-estimate --text "hello"
uacos redact-test --text "api_key=SECRET"
```

## Safety

- dry-run remains default unless user enables real provider call
- provider must be enabled in llm config for real calls
- logs redact keys/tokens/secrets
- retries/backoff are controlled

---

## Source: `PHASE_22_CONTEXT_BUDGET_OPTIMIZER.md`

# Phase 22 — Context Budget Optimizer

## Objective

Phase 22 makes UACOS context selection token-aware and task-size-aware.

## New Module

```text
uacos/budget/optimizer.py
```

## New CLI

```bash
uacos budget-classify --task "fix db error"
uacos summary-cache --repo <repo>
uacos context-budget --repo <repo> --task "fix db error"
uacos context-budget --repo <repo> --task "refactor pipeline" --profile large --max-tokens 12000
uacos budget-report --repo <repo>
```

## Features

- task classifier: tiny/small/medium/large/architecture
- dynamic token budgets
- file summary cache
- graph/impact based file ranking
- semantic memory/skill integration
- budget report

---

## Source: `PHASE_23_VSCODE_PRODUCTION_LAYER.md`

# Phase 23 — VSCode Production Layer

## New Module

```text
uacos/ide/vscode_pro.py
```

## New CLI

```bash
uacos vscode-pro-init --output-dir ./vscode-uacos --overwrite
uacos vscode-pro-check --output-dir ./vscode-uacos
```

## Commands Generated

Bootstrap, health, scan, context-budget, context-smart, AST graph, semantic index,
skill review, feedback recommend, provider health, autopilot plan/status, patch20 validate, status panel.

---

## Source: `PHASE_24_OPENCLAW_ADAPTER_PRODUCTION.md`

# Phase 24 — OpenClaw Adapter Production Layer

## Objective

Phase 24 makes OpenClaw integration safer and more practical.

## New Module

```text
uacos/adapters/openclaw.py
```

## New CLI

```bash
uacos openclaw-init --repo <repo>
uacos openclaw-config --repo <repo> --default-agent leader --context-mode budget
uacos openclaw-validate --repo <repo>
uacos openclaw-health --repo <repo>
uacos openclaw-prompt --repo <repo> --task "fix bug" --agent leader
uacos openclaw-run --repo <repo> --task "fix bug"
uacos openclaw-run --repo <repo> --task "fix bug" --real
uacos openclaw-history --repo <repo>
uacos openclaw-summary --repo <repo>
```

## Safety

- dry-run by default
- real run requires `allowed_real_run`
- prompt has max char guard
- output is captured into `agent_response.md`
- history stored under `.uacos/openclaw`

---

## Source: `PHASE_25_PRODUCTION_DASHBOARD_METRICS.md`

# Phase 25 — Production Dashboard + Metrics

## Objective

Phase 25 adds a unified metrics and production dashboard layer.

## New Module

```text
uacos/metrics/production.py
```

## New CLI

```bash
uacos prod-metrics --repo <repo>
uacos prod-report --repo <repo>
uacos prod-dashboard --repo <repo>
uacos prod-doctor --repo <repo>
uacos prod-serve --repo <repo> --port 8787
```

## Output

```text
.uacos/metrics/production_metrics.json
.uacos/metrics/production_dashboard.html
```

## Metrics

- health score
- AST graph counts
- semantic index counts
- autopilot status
- patch status
- provider cost estimate
- OpenClaw runs
- skill execution feedback
- budget selected files

---

## Source: `PHASE_26_CONTEXT_COMPRESSION_ENGINE.md`

# Phase 26 — Context Compression Engine

## Objective

Phase 26 reduces token use by replacing raw file context with AST-aware summaries and task-focused compressed context.

## New Module

```text
uacos/compression/engine.py
```

## New CLI

```bash
uacos compress-cache --repo <repo>
uacos project-summary --repo <repo>
uacos context-compressed --repo <repo> --task "fix db bug" --max-tokens 6000
uacos compression-report --repo <repo>
```

## Output

```text
.uacos/compression/summary_cache.json
.uacos/compression/project_compressed_summary.md
.uacos/compression/latest_compressed_context.md
.uacos/compression/latest_compression_report.json
```

## Design

- local-first
- no cloud dependency
- AST-aware Python summaries
- generic summaries for docs/configs
- impact-based file selection
- skill/memory injection
- compression ratio report

---

## Source: `PHASE_27_TRANSACTIONAL_AUTOPILOT.md`

# Phase 27 — Transactional Autopilot Execution + Rollback Chain

## Objective

Phase 27 adds transaction semantics around AI code execution.

## New Module

```text
uacos/transaction/engine.py
```

## New CLI

```bash
uacos tx-begin --repo <repo> --title "Fix bug" --file app.py
uacos tx-run --repo <repo> --patch change.diff --allowed-file app.py --test "python -m pytest -q"
uacos tx-run --repo <repo> --patch change.diff --dry-run
uacos tx-status --repo <repo> --tx-id TX-xxxx
uacos tx-list --repo <repo>
uacos tx-rollback --repo <repo> --tx-id TX-xxxx
uacos tx-report --repo <repo> --tx-id TX-xxxx
```

## Safety

- checkpoint before patch
- patch20 validation
- test gate
- auto rollback on failed tests
- manual rollback
- manifest audit trail

---

## Source: `PHASE_28_TRUE_AGENT_RUNTIME.md`

# Phase 28 — True Agent Runtime

## Objective

Phase 28 introduces a local-first runtime for AI agent jobs.

## New Module

```text
uacos/runtime/agent_runtime.py
```

## New CLI

```bash
uacos runtime-init --repo <repo>
uacos runtime-config --repo <repo> --default-backend manual
uacos runtime-validate --repo <repo>
uacos job-create --repo <repo> --task "fix bug" --allowed-file app.py --test "python -m pytest -q"
uacos job-run-once --repo <repo>
uacos job-list --repo <repo>
uacos job-status --repo <repo> --job-id JOB-xxxx
uacos job-report --repo <repo> --job-id JOB-xxxx
uacos runtime-status --repo <repo>
```

## Runtime Backends

- manual: prepares prompt/context and waits for human/agent output
- provider: calls hardened LLM provider
- openclaw: calls OpenClaw adapter

## Safety

- dry-run default
- real-run requires allowed_real_run
- compressed context by default
- transaction wrapper for patch apply
- job history/status persisted

---

## Source: `PHASE_29_TEST_COVERAGE_HARDENING.md`

# Phase 29 — Test Coverage Hardening

## Objective

Phase 29 adds automated safety tests for the critical V3 modules that were previously only smoke-tested per phase.

## New/Expanded Tests

```text
tests/test_phase19_ast_graph.py
tests/test_phase20_patch_engine.py
tests/test_phase21_24_provider_openclaw.py
tests/test_phase22_budget_optimizer.py
tests/test_phase26_compression.py
tests/test_phase27_transaction.py
tests/test_phase28_runtime.py
tests/test_e2e_v3_user_flow.py
scripts/run_phase29_tests.py
```

## Coverage Focus

- AST graph and impact analysis
- Patch20 modify/new/delete + rollback
- Out-of-scope patch rejection
- Budget optimizer token budget
- Compression context budget
- Transaction commit/fail/auto rollback/manual rollback
- Provider dry-run redaction
- OpenClaw dry-run prompt generation
- Runtime manual job flow
- Full V3 user flow

---

## Source: `PHASE_30_REALRUN_E2E_VALIDATION.md`

# Phase 30 — Real-run E2E Validation Layer

## Objective

Phase 30 validates the production pipeline under real-run-like conditions without spending API money by using a local OpenAI-compatible mock provider.

## New Module

```text
uacos/validation/realrun.py
```

## New CLI

```bash
uacos realrun-preflight --repo <repo>
uacos mock-provider-e2e --repo <repo>
uacos runtime-mock-e2e --repo <repo>
uacos phase30-validate --repo <repo>
uacos ollama-realrun-check --repo <repo> --model qwen2.5-coder:7b --real
uacos openclaw-realrun-check --repo <repo> --agent leader --real
```

## What is tested

- compressed context generation
- OpenAI-compatible real provider path
- hardened provider call
- runtime provider backend
- diff extraction
- transaction apply
- test gate
- final app file mutation
- OpenClaw dry/real guard
- Ollama dry/real guard

## Safety

- no real cloud calls by default
- mock server runs locally
- Ollama/OpenClaw real-run requires explicit `--real`

---

## Source: `PHASE_31_MINIMAL_MCP_SERVER.md`

# Phase 31 — Minimal MCP Server

## Objective

Phase 31 allows external agents to call UACOS directly through a local HTTP/JSON-RPC MCP-style bridge.

## New Module

```text
uacos/mcp/server.py
```

## New CLI

```bash
uacos mcp-serve --repo <repo> --host 127.0.0.1 --port 8769
uacos mcp-self-test --repo <repo>
uacos mcp-call --repo <repo> --tool get_context --args "{"task":"fix bug"}"
```

## Endpoints

```text
GET  /health
GET  /tools
POST /call
POST /jsonrpc
```

## Tools

- list_tools
- get_context
- get_memory
- ingest_patch
- create_job
- run_job
- status

## Safety

- localhost-only by default
- patch application uses transaction engine
- external agents can validate patch without applying

---

## Source: `PHASE_32_JS_TS_FULLSTACK_IMPACT.md`

# Phase 32 — JS/TS AST + Full-stack Impact

## Objective

Phase 32 closes the P1 gap that UACOS only understood Python.

## New Modules

```text
uacos/ast_engine/js_parser.py
uacos/fullstack/impact.py
```

## New CLI

```bash
uacos js-ts-scan --repo <repo>
uacos fullstack-index --repo <repo>
uacos fullstack-impact --repo <repo> --task "fix /api/users dashboard"
uacos fullstack-context --repo <repo> --task "fix /api/users dashboard"
```

## Capabilities

- JS/TS imports
- functions/classes
- fetch/axios API endpoint detection
- Python FastAPI route detection
- backend route ↔ frontend API usage links
- full-stack context that includes backend + frontend files

---

## Source: `PHASE_33_REAL_LLM_BUDGET_GUARD.md`

# Phase 33 — Real LLM + Budget Guard

Adds Ollama LAN/local routing, optional OpenRouter fallback, and hard token budget guard.

---

## Source: `PHASE_34_TOKEN_CACHE_REUSE_ENGINE.md`

# Phase 34 — Token Cache + Response Reuse Engine

## Objective

Reduce repeated LLM calls by caching exact and similar task responses.

## New Modules

```text
uacos/cache/llm_cache.py
uacos/cache/similarity.py
```

## New CLI

```bash
uacos cache34-status --repo .
uacos cache34-list --repo .
uacos cache34-clear --repo .
uacos cache34-benchmark --repo . --task "fix app value"
uacos llm-run-real --repo . --task "fix app value"
uacos llm-run-real --repo . --task "fix app value" --no-cache
```

## Expected Result

First call stores cache. Second call returns `cache_hit` with zero tokens.

---

## Source: `UACOS_PHASE_INDEX_0_33.md`

# UACOS Phase Index 0–33

- 0–18: foundations, V1/V2, skill/memory improvements
- 19: AST/dependency graph
- 20: production patch engine
- 21: provider hardening
- 22: context budget optimizer
- 23: VSCode production layer
- 24: OpenClaw adapter
- 25: production metrics/dashboard
- 26: context compression
- 27: transactional autopilot rollback
- 28: true agent runtime
- 29: test coverage hardening
- 30: real-run E2E validation
- 31: minimal MCP server
- 32: JS/TS full-stack impact
- 33: real LLM routing + budget guard

---

## Source: `UACOS_PHASE_INDEX_0_34.md`

# UACOS Phase Index 0–34

- Phase 0–18: core memory, workflow, provider, V2 foundations
- Phase 19: AST/dependency graph
- Phase 20: production patch engine
- Phase 21: provider hardening
- Phase 22: context budget optimizer
- Phase 23: VSCode production layer
- Phase 24: OpenClaw adapter
- Phase 25: production metrics/dashboard
- Phase 26: context compression
- Phase 27: transactional autopilot rollback
- Phase 28: true agent runtime
- Phase 29: test coverage hardening
- Phase 30: real-run E2E validation
- Phase 31: minimal MCP server
- Phase 32: JS/TS full-stack impact
- Phase 33: real LLM + budget guard
- Phase 34: token cache + response reuse engine
