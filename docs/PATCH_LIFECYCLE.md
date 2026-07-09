# Patch Lifecycle

UACOS treats every AI-generated patch as untrusted input.

The safe path is:

```text
agent proposes patch
        |
        v
uacos-flow guard / MCP ingest_patch(apply=false)
        |
        v
scope validation -> secret scan -> risk review -> task alignment -> tests required -> guarded apply only
```

## Guard Mode behavior

`uacos-flow guard` validates a patch and now returns three separate views:

- `validation` — patch gate result: scope, unsafe paths, blocked sensitive files, secret scan, file/line limits.
- `risk_review` — lifecycle risk categories and next required actions.
- `impact_alignment` — task-to-patch alignment when a task is supplied.

`uacos-flow guard` does **not** apply code.

## Risk categories

| Category | Meaning |
|---|---|
| `auth_change` | Patch touches authentication, login, session, token, password, permission, or RBAC logic. |
| `network_call` | Patch adds network/process-call behavior such as `requests`, `urllib`, `httpx`, sockets, subprocess, curl, or wget. |
| `ci_release_change` | Patch touches CI, release, or release-gate paths. |
| `dependency_change` | Patch touches dependency manifests or lock files. |
| `sensitive_config_change` | Patch touches config/settings/secrets/credentials/key paths. |
| `broad_rewrite` | Patch adds/removes a large amount of code. |
| `many_removed_lines` | Patch removes many lines and may hide destructive changes. |

## Risk levels

| Level | Meaning | Required behavior |
|---|---|---|
| `low` | No obvious high-risk category detected and patch gate passes. | Can proceed only through guarded apply/test flow. |
| `medium` | Broad or destructive-looking rewrite detected. | Requires careful review and tests before apply. |
| `high` | Auth/network/CI/dependency/config risk detected. | Human review required before apply. |
| `block` | Patch gate failed, for example scope violation or sensitive path. | Must fix failures before apply. |

## Required next steps

A patch review may require:

- `fix_patch_gate_failures_before_apply`
- `human_review_required`
- `explain_risk_categories_before_apply`
- `tests_required_before_safe_apply`
- `apply_only_through_guarded_transaction_or_explicit_mcp_apply`

## Example

```bash
uacos-flow guard \
  --repo . \
  --patch change.diff \
  --task "fix login bug" \
  --allowed-file app/auth.py \
  --test "pytest -q"
```

Expected output includes:

```json
{
  "status": "pass",
  "risk_review": {
    "risk_level": "high",
    "risk_categories": ["auth_change"],
    "writes_code": false,
    "required_next_steps": ["human_review_required"]
  }
}
```

## What this does not prove

- Risk review does not prove the patch is correct.
- Risk review does not replace tests or human review.
- Risk review does not apply code.
- High-risk patches can still be valid, but they need stronger review evidence.
