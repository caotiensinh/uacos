from __future__ import annotations

MAX_MCP_REQUEST_BYTES = 4 * 1024 * 1024


def validate_content_length(value: str | None, *, max_bytes: int = MAX_MCP_REQUEST_BYTES) -> int:
    """Parse and validate an MCP HTTP Content-Length header.

    The server is local-only by default, but request bodies are still bounded so a
    malformed or accidental client cannot force an unbounded allocation/read.
    """
    if value is None:
        raise ValueError("content_length_required")
    try:
        length = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("invalid_content_length") from exc
    if length < 0:
        raise ValueError("invalid_content_length")
    if max_bytes <= 0:
        raise ValueError("invalid_max_request_bytes")
    if length > max_bytes:
        raise ValueError("request_too_large")
    return length
