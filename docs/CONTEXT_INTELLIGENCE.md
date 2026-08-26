# Context Intelligence

Context Intelligence makes UACOS context selection reviewable before an AI coding agent edits code.

The goal is not to make a perfect static analyzer. The goal is to give the user enough evidence to decide whether the context pack is likely relevant, incomplete, or risky.

## Current signals

### Selected-file explanations

`uacos-flow assist` returns `selection_explanations` for files included in the compressed context pack.

Each explanation includes:

- confidence
- file roles
- matched task terms
- selection reasons
- impact score
- raw token estimate
- summary token estimate
- quality note

Example:

```json
{
  "file": "auth.py",
  "confidence": "high",
  "roles": ["security_or_auth"],
  "matched_task_terms": ["login"],
  "reasons": [
    "symbol match from task: login",
    "token tradeoff: raw 30 -> summary 20"
  ]
}
```

### Symbol context

`uacos-flow assist` returns `symbol_context` from the existing static Python graph.

The symbol context includes:

- symbols defined in selected files
- task symbol matches
- incoming calls to selected files
- outgoing calls from selected files
- incoming/outgoing import edges
- graph stats

This helps the user see not just which file was selected, but what functions/classes are inside it and which other files call/import it.

### Route/API graph

`uacos-flow assist` also returns `api_graph`.

The graph currently detects:

- Python route decorators such as `@app.get('/path')`, `@router.post('/path')`, and `@bp.route('/path', methods=['POST'])`.
- JS/TS server routes such as `app.get('/path')` and `router.post('/path')`.
- JS/TS client API calls such as `fetch('/path')`, `axios.post('/path')`, and `api.get('/path')`.

The graph includes:

- all detected routes
- all detected client API calls
- route/API items related to the task
- whether a route/API item is already in the selected context

### Test-to-source mapping

`uacos-flow assist` now returns `test_map`.

The map currently detects likely tests through:

- Python test names such as `test_service.py` for `service.py`.
- Python imports/references from test files to source files.
- JS/TS test names such as `client.test.ts`, `client.spec.ts`, and equivalent JS/JSX/TSX patterns.

The map includes:

- selected source files
- likely test files
- mapping confidence
- reasons such as `name_match` and `import_or_reference_match`
- recommended commands such as `python -m pytest -q tests/test_service.py` or `npm test -- client.test.ts`

These commands are candidates for evidence. They are not proof until executed.

### Config/deployment risk map

`uacos-flow assist` now returns `config_risk`.

The map detects files that can affect runtime, deployment, CI, dependency resolution, databases, networking, or secrets, including:

- `.env` and environment-style files
- Dockerfile and compose files
- GitHub Actions workflows
- Kubernetes/Helm/deploy paths
- dependency manifests and lock files
- database migration/config files
- nginx/network/proxy/server config

The map includes:

- risk level: `low`, `medium`, or `high`
- categories such as `secret_or_environment_config`, `ci_release_pipeline`, `container_runtime`, `dependency_surface`, `database_or_migration`, and `network_runtime`
- whether the risky config file is already in the selected context
- recommended review actions

High-risk config findings require human review before a patch should be trusted.

## Example

```bash
uacos-flow assist --repo . --task "fix events endpoint" --max-tokens 6000
```

Expected output includes:

```json
{
  "selection_explanations": {
    "status": "ok",
    "explanations": []
  },
  "symbol_context": {
    "status": "ok",
    "selected_file_symbols": [],
    "incoming_calls_to_selected": [],
    "outgoing_calls_from_selected": []
  },
  "api_graph": {
    "status": "ok",
    "route_count": 1,
    "client_api_call_count": 2,
    "relevant_routes": [],
    "relevant_client_api_calls": []
  },
  "test_map": {
    "status": "ok",
    "mapped_source_count": 1,
    "mappings": []
  },
  "config_risk": {
    "status": "ok",
    "high_risk_count": 1,
    "recommended_review": ["human_review_required_for_high_risk_config"]
  }
}
```

## What this does not prove

- It does not prove runtime routing behavior.
- It does not execute the app.
- It does not guarantee every framework-specific route is detected.
- It does not guarantee every relevant test is detected.
- It does not prove actual production deployment impact.
- It does not replace secret scanning or patch-gate validation.
- Symbol context is currently strongest for Python graph data and does not guarantee complete cross-language symbol coverage.

## Next upgrades

- route/client matching across frontend and backend by normalized path
- optional execution of recommended test commands through guarded evidence flow
- richer cross-language symbol indexing
