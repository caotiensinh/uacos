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
        |
        v
uacos-flow apply-safe -> checkpoint -> apply -> tests -> rollback on failure -> latest evidence report
```

## Guard Mode behavior

`uacos-flow guard` validates a patch and now returns three separate views:

- `validation` — patch gate result: scope, unsafe paths, blocked sensitive files, secret scan, file/line limits.
- `risk_review` — lifecycle risk categories and next required actions.
- `impact_alignment` — task-to-patch alignment when a task is supplied.

`uacos-flow guard` does **not** apply code.

## Safe Apply behavior

`uacos-flow apply-safe` is the guarded apply path. It wraps the existing transaction engine instead of inventing a second patch application system.

It blocks by default unless all of the following are true:

- `--yes` is present.
- at least one `--test` command is present.
- patch review is not blocked.
- high-risk patches use `--allow-high-risk` after human review.

When allowed, it runs:

```text
risk review -> transaction checkpoint -> patch apply -> tests -> rollback on test failure -> latest patch lifecycle report
```

The latest report is written to:

```text
.uacos/patch_lifecycle/latest_patch_lifecycle_report.json
```

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

## Review example

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

## Safe apply example

```bash
uacos-flow apply-safe \
  --repo . \
  --patch change.diff \
  --allowed-file app/auth.py \
  --test "pytest -q" \
  --yes \
  --allow-high-risk
```

Expected output includes:

```json
{
  "status": "pass",
  "writes_code": true,
  "transaction": {
    "status": "committed"
  },
  "report_file": ".uacos/patch_lifecycle/latest_patch_lifecycle_report.json"
}
```

If tests fail, the transaction engine restores the checkpoint and the lifecycle report records the rolled-back transaction.

## What this does not prove

- Risk review does not prove the patch is correct.
- Safe apply does not remove the need for tests.
- High-risk patches still need human review.
- Passing tests do not prove full production readiness.
