import pytest

from uacos.mcp.http_limits import MAX_MCP_REQUEST_BYTES, validate_content_length


def test_content_length_accepts_zero_and_limit():
    assert validate_content_length("0") == 0
    assert validate_content_length(str(MAX_MCP_REQUEST_BYTES)) == MAX_MCP_REQUEST_BYTES


def test_content_length_requires_header():
    with pytest.raises(ValueError, match="content_length_required"):
        validate_content_length(None)


def test_content_length_rejects_invalid_and_negative_values():
    for value in ("abc", "1.5", "-1"):
        with pytest.raises(ValueError, match="invalid_content_length"):
            validate_content_length(value)


def test_content_length_rejects_oversized_request():
    with pytest.raises(ValueError, match="request_too_large"):
        validate_content_length(str(MAX_MCP_REQUEST_BYTES + 1))


def test_content_length_rejects_invalid_limit():
    with pytest.raises(ValueError, match="invalid_max_request_bytes"):
        validate_content_length("0", max_bytes=0)
