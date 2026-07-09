# UACOS MCP Server

UACOS includes a local MCP-compatible server for AI coding workflows that need repository context, memory, patch validation, orchestration planning, and status information.

The MCP server is designed to support external agents. It does not replace those agents. The external agent proposes or writes code; UACOS provides bounded context, safety checks, and evidence.

## Security boundary

- The server is local-first.
- It should bind only to localhost unless a maintainer explicitly reviews and changes the deployment model.
- Patch ingestion should use Guard Mode or Apply-safe Mode before code is changed.
- The server should not be exposed as a public write endpoint.

## Typical flow

1. External agent asks UACOS for task context.
2. UACOS returns bounded context and selected-file explanations.
3. External agent proposes a patch.
4. UACOS validates patch scope, risk, and secret exposure.
5. Tests and release gate provide evidence before any completion claim.

## Related workflows

Use `uacos-flow` for the supported command-line workflow:

```bash
uacos-flow assist --repo . --task "fix login bug safely" --max-tokens 6000
uacos-flow guard --repo . --patch change.diff --allowed-file app/auth.py --test "pytest -q"
uacos-flow apply-safe --repo . --patch change.diff --allowed-file app/auth.py --test "pytest -q" --yes
```

## Related docs

- [External Agent Integration](EXTERNAL_AGENT_INTEGRATION.md)
- [Patch Lifecycle](PATCH_LIFECYCLE.md)
- [Product Workflows](PRODUCT_WORKFLOWS.md)
- [Security Model](SECURITY_MODEL.md)
