from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from uacos.runtime.resource_lease import SQLiteResourceLeaseStore, resources_conflict


class Clock:
    def __init__(self, value: float = 1000.0):
        self.value = value

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def test_file_and_parent_directory_conflict():
    assert resources_conflict("file", "src/app.py", "dir", "src") is True
    assert resources_conflict("dir", "src", "file", "src/app.py") is True
    assert resources_conflict("file", "src/app.py", "dir", "tests") is False


def test_directory_ancestor_and_descendant_conflict():
    assert resources_conflict("dir", "src", "dir", "src/core") is True
    assert resources_conflict("dir", "src/core", "dir", "src") is True
    assert resources_conflict("dir", "src", "dir", "docs") is False


def test_acquire_blocks_conflicting_owner(tmp_path: Path):
    clock = Clock()
    store = SQLiteResourceLeaseStore(tmp_path, clock=clock)
    first = store.acquire(resource_type="dir", resource_key="src", owner_id="agent-a", ttl_seconds=30)
    second = store.acquire(resource_type="file", resource_key="src/app.py", owner_id="agent-b", ttl_seconds=30)

    assert first["status"] == "ok"
    assert second["status"] == "blocked"
    assert second["reason"] == "resource_lease_conflict"
    assert second["conflict"]["owner_id"] == "agent-a"


def test_same_owner_exact_reacquire_is_idempotent_without_token_rotation(tmp_path: Path):
    clock = Clock()
    store = SQLiteResourceLeaseStore(tmp_path, clock=clock)
    first = store.acquire(resource_type="file", resource_key="src/app.py", owner_id="agent-a", ttl_seconds=30)
    second = store.acquire(resource_type="file", resource_key="src/app.py", owner_id="agent-a", ttl_seconds=30)

    assert second["status"] == "ok"
    assert second["idempotent"] is True
    assert second["lease"]["lease_token"] == first["lease"]["lease_token"]
    assert second["lease"]["expires_at"] == first["lease"]["expires_at"]


def test_expired_lease_can_be_reclaimed_and_old_token_is_fenced(tmp_path: Path):
    clock = Clock()
    store = SQLiteResourceLeaseStore(tmp_path, clock=clock)
    first = store.acquire(resource_type="file", resource_key="src/app.py", owner_id="agent-a", ttl_seconds=5)
    old_token = first["lease"]["lease_token"]

    clock.advance(6)
    second = store.acquire(resource_type="file", resource_key="src/app.py", owner_id="agent-b", ttl_seconds=30)

    assert second["status"] == "ok"
    assert second["lease"]["owner_id"] == "agent-b"
    assert second["lease"]["lease_token"] != old_token

    stale_heartbeat = store.heartbeat(
        resource_type="file",
        resource_key="src/app.py",
        owner_id="agent-a",
        lease_token=old_token,
        ttl_seconds=30,
    )
    stale_release = store.release(
        resource_type="file",
        resource_key="src/app.py",
        owner_id="agent-a",
        lease_token=old_token,
    )
    assert stale_heartbeat["status"] == "lost"
    assert stale_heartbeat["reason"] == "lease_fenced"
    assert stale_release["status"] == "blocked"
    assert stale_release["reason"] == "lease_fenced"


def test_heartbeat_extends_ttl_but_keeps_fencing_token(tmp_path: Path):
    clock = Clock()
    store = SQLiteResourceLeaseStore(tmp_path, clock=clock)
    first = store.acquire(resource_type="task", resource_key="TASK-1", owner_id="agent-a", ttl_seconds=5)
    token = first["lease"]["lease_token"]
    original_expiry = first["lease"]["expires_at"]

    clock.advance(3)
    heartbeat = store.heartbeat(
        resource_type="task",
        resource_key="TASK-1",
        owner_id="agent-a",
        lease_token=token,
        ttl_seconds=10,
    )

    assert heartbeat["status"] == "ok"
    assert heartbeat["lease"]["lease_token"] == token
    assert heartbeat["lease"]["expires_at"] > original_expiry


def test_release_is_idempotent_after_valid_release(tmp_path: Path):
    clock = Clock()
    store = SQLiteResourceLeaseStore(tmp_path, clock=clock)
    lease = store.acquire(resource_type="branch", resource_key="feature/x", owner_id="agent-a", ttl_seconds=30)["lease"]

    first = store.release(
        resource_type="branch",
        resource_key="feature/x",
        owner_id="agent-a",
        lease_token=lease["lease_token"],
    )
    second = store.release(
        resource_type="branch",
        resource_key="feature/x",
        owner_id="agent-a",
        lease_token=lease["lease_token"],
    )

    assert first["reason"] == "lease_released"
    assert second == {"status": "ok", "reason": "no_active_lease", "idempotent": True}


def test_concurrent_acquire_allows_exactly_one_owner(tmp_path: Path):
    db_path = tmp_path / ".uacos" / "lease-test.sqlite3"
    clock = Clock()

    def acquire(owner: str):
        store = SQLiteResourceLeaseStore(tmp_path, clock=clock, db_path=db_path)
        return store.acquire(resource_type="file", resource_key="src/app.py", owner_id=owner, ttl_seconds=30)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(acquire, ["agent-a", "agent-b"]))

    statuses = sorted(result["status"] for result in results)
    assert statuses == ["blocked", "ok"]


def test_invalid_path_and_ttl_fail_closed(tmp_path: Path):
    store = SQLiteResourceLeaseStore(tmp_path)
    with pytest.raises(ValueError, match="repo_relative"):
        store.acquire(resource_type="file", resource_key="../secret", owner_id="agent-a")
    with pytest.raises(ValueError, match="ttl_seconds_must_be_positive"):
        store.acquire(resource_type="task", resource_key="TASK-1", owner_id="agent-a", ttl_seconds=0)


def test_list_active_prunes_expired_leases(tmp_path: Path):
    clock = Clock()
    store = SQLiteResourceLeaseStore(tmp_path, clock=clock)
    store.acquire(resource_type="task", resource_key="TASK-1", owner_id="agent-a", ttl_seconds=1)
    store.acquire(resource_type="branch", resource_key="feature/x", owner_id="agent-b", ttl_seconds=10)

    clock.advance(2)
    active = store.list_active()

    assert len(active) == 1
    assert active[0]["resource_type"] == "branch"
    assert active[0]["resource_key"] == "feature/x"
