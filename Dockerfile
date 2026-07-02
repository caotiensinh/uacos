FROM python:3.11-slim

WORKDIR /repo

COPY pyproject.toml README.md ./
COPY uacos ./uacos

RUN pip install --no-cache-dir -e .

# UACOS's MCP server is localhost-only by design (uacos/mcp/server.py
# refuses to bind anything other than 127.0.0.1/localhost) — it exposes
# repo-scoped tools and is not meant to be reachable from outside the
# host it runs on. Run it against the mounted repo at /repo.
#
# Consequence for container use: this binds 127.0.0.1 *inside* the
# container's own network namespace, so `docker run -p 8769:8769` will
# NOT make it reachable from the host or from an external checker —
# only `docker exec` into the container (or a tool that inspects it
# from inside) can reach it. This is intentional; loosening the bind
# address to make external checks pass would remove the safety
# guarantee the rest of the project relies on.
EXPOSE 8769

ENTRYPOINT ["uacos", "mcp-serve", "--repo", "/repo", "--host", "127.0.0.1", "--port", "8769"]
