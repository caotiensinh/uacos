# Production 10/10 Scorecard

This scorecard tracks the UACOS v4 hardening sprint toward a production-ready beta.

| Area | Target | Current Evidence |
| --- | --- | --- |
| CLI compatibility | Existing commands remain callable | `scripts/uacos_self_check.py` |
| MCP endpoints | `/`, `/health`, `/tools`, `/sse` return valid responses | `tests/test_mcp_endpoints.py` |
| Cache correctness | Similarity, TTL pruning, invalidation, and lookup imports work | `tests/test_cache_similarity_and_ttl.py` |
| Documentation hygiene | Root docs are minimal and docs are indexed | `docs/DOCS_CLEANUP_REPORT.md` |
| Release safety | Compile, pytest, and self-check are gated | `scripts/release_gate.py` |

## Out Of Scope For This Sprint

Redis, PostgreSQL, RabbitMQ, Celery, Pinecone, GitHub PR bot automation, and multi-tenant production infrastructure.
