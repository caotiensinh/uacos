from __future__ import annotations

from pathlib import Path

from uacos.runtime.resource_lease import SQLiteResourceLeaseStore, resources_conflict


def test_dot_prefixed_repo_path_is_preserved(tmp_path: Path):
    store = SQLiteResourceLeaseStore(tmp_path)
    result = store.acquire(
        resource_type="file",
        resource_key=".github/workflows/ci.yml",
        owner_id="agent-a",
        ttl_seconds=30,
    )

    assert result["status"] == "ok"
    assert result["lease"]["resource_key"] == ".github/workflows/ci.yml"


def test_dot_prefixed_directory_conflicts_with_child_file():
    assert resources_conflict(
        "dir",
        ".github/workflows",
        "file",
        ".github/workflows/ci.yml",
    ) is True
