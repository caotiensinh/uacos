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
  }
}
```

## What this does not prove

- It does not prove runtime routing behavior.
- It does not execute the app.
- It does not guarantee every framework-specific route is detected.
- It does not guarantee every relevant test is detected.
- It does not yet map deployment/config risk.

## Next upgrades

- config/deployment risk map
- deeper symbol-level explanation
- route/client matching across frontend and backend by normalized path
- optional execution of recommended test commands through guarded evidence flow
