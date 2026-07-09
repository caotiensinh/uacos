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
  }
}
```

## What this does not prove

- It does not prove runtime routing behavior.
- It does not execute the app.
- It does not guarantee every framework-specific route is detected.
- It does not yet map tests to source files.
- It does not yet map deployment/config risk.

## Next upgrades

- test-to-source mapping
- config/deployment risk map
- deeper symbol-level explanation
- route/client matching across frontend and backend by normalized path
