from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable
import json
import sqlite3
import time
import uuid

from uacos.config import uacos_dir


ALLOWED_RESOURCE_TYPES = {"file", "dir", "branch", "task"}


@dataclass(frozen=True)
class ResourceLease:
    resource_type: str
    resource_key: str
    owner_id: str
    lease_token: str
    acquired_at: float
    heartbeat_at: float
    expires_at: float
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_resource(resource_type: str, resource_key: str) -> tuple[str, str]:
    kind = str(resource_type or "").strip().lower()
    if kind not in ALLOWED_RESOURCE_TYPES:
        raise ValueError("invalid_resource_type")
    key = str(resource_key or "").strip()
    if not key:
        raise ValueError("resource_key_required")
    if kind in {"branch", "task"}:
        return kind, key

    path = PurePosixPath(key.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("resource_path_must_be_repo_relative")
    normalized = path.as_posix()
    if normalized.startswith("./"):
        normalized = normalized[2:]
    if not normalized or normalized == ".":
        raise ValueError("resource_key_required")
    return kind, normalized


def _is_within(path: str, directory: str) -> bool:
    p = PurePosixPath(path)
    d = PurePosixPath(directory)
    return p == d or d in p.parents


def resources_conflict(a_type: str, a_key: str, b_type: str, b_key: str) -> bool:
    a_type, a_key = _normalize_resource(a_type, a_key)
    b_type, b_key = _normalize_resource(b_type, b_key)
    if a_type in {"branch", "task"} or b_type in {"branch", "task"}:
        return a_type == b_type and a_key == b_key
    if a_type == "file" and b_type == "file":
        return a_key == b_key
    if a_type == "dir" and b_type == "dir":
        return _is_within(a_key, b_key) or _is_within(b_key, a_key)
    if a_type == "file" and b_type == "dir":
        return _is_within(a_key, b_key)
    if a_type == "dir" and b_type == "file":
        return _is_within(b_key, a_key)
    return False


class SQLiteResourceLeaseStore:
    """Cross-process resource leases with TTL, heartbeat, and fencing tokens."""

    def __init__(
        self,
        repo_root: Path,
        *,
        clock: Callable[[], float] | None = None,
        db_path: Path | None = None,
    ) -> None:
        self.repo_root = Path(repo_root)
        self.clock = clock or time.time
        root = uacos_dir(self.repo_root)
        root.mkdir(parents=True, exist_ok=True)
        self.db_path = Path(db_path) if db_path is not None else root / "resource_leases.sqlite3"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=5.0, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS resource_leases (
                    resource_type TEXT NOT NULL,
                    resource_key TEXT NOT NULL,
                    owner_id TEXT NOT NULL,
                    lease_token TEXT NOT NULL,
                    acquired_at REAL NOT NULL,
                    heartbeat_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    metadata_json TEXT NOT NULL,
                    PRIMARY KEY(resource_type, resource_key)
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_resource_leases_expiry ON resource_leases(expires_at)")

    @staticmethod
    def _row_to_lease(row: sqlite3.Row) -> ResourceLease:
        try:
            metadata = json.loads(row["metadata_json"] or "{}")
        except (TypeError, ValueError):
            metadata = {}
        if not isinstance(metadata, dict):
            metadata = {}
        return ResourceLease(
            resource_type=str(row["resource_type"]),
            resource_key=str(row["resource_key"]),
            owner_id=str(row["owner_id"]),
            lease_token=str(row["lease_token"]),
            acquired_at=float(row["acquired_at"]),
            heartbeat_at=float(row["heartbeat_at"]),
            expires_at=float(row["expires_at"]),
            metadata=metadata,
        )

    def _active_rows(self, conn: sqlite3.Connection, now: float) -> list[sqlite3.Row]:
        conn.execute("DELETE FROM resource_leases WHERE expires_at <= ?", (now,))
        return list(conn.execute("SELECT * FROM resource_leases ORDER BY resource_type, resource_key"))

    def acquire(
        self,
        *,
        resource_type: str,
        resource_key: str,
        owner_id: str,
        ttl_seconds: float = 30.0,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        kind, key = _normalize_resource(resource_type, resource_key)
        owner = str(owner_id or "").strip()
        if not owner:
            raise ValueError("owner_id_required")
        ttl = float(ttl_seconds)
        if ttl <= 0:
            raise ValueError("ttl_seconds_must_be_positive")
        now = float(self.clock())
        metadata_json = json.dumps(dict(metadata or {}), ensure_ascii=False, sort_keys=True, separators=(",", ":"))

        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                active = self._active_rows(conn, now)
                for row in active:
                    lease = self._row_to_lease(row)
                    if lease.resource_type == kind and lease.resource_key == key and lease.owner_id == owner:
                        conn.execute("COMMIT")
                        return {"status": "ok", "reason": "lease_already_held", "idempotent": True, "lease": lease.to_dict()}
                    if resources_conflict(kind, key, lease.resource_type, lease.resource_key):
                        conn.execute("COMMIT")
                        return {"status": "blocked", "reason": "resource_lease_conflict", "conflict": lease.to_dict()}

                token = uuid.uuid4().hex
                expires = now + ttl
                conn.execute(
                    """
                    INSERT INTO resource_leases(
                        resource_type, resource_key, owner_id, lease_token,
                        acquired_at, heartbeat_at, expires_at, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (kind, key, owner, token, now, now, expires, metadata_json),
                )
                conn.execute("COMMIT")
                lease = ResourceLease(kind, key, owner, token, now, now, expires, dict(metadata or {}))
                return {"status": "ok", "reason": "lease_acquired", "idempotent": False, "lease": lease.to_dict()}
            except Exception:
                conn.execute("ROLLBACK")
                raise

    def heartbeat(
        self,
        *,
        resource_type: str,
        resource_key: str,
        owner_id: str,
        lease_token: str,
        ttl_seconds: float = 30.0,
    ) -> dict[str, Any]:
        kind, key = _normalize_resource(resource_type, resource_key)
        owner = str(owner_id or "").strip()
        token = str(lease_token or "").strip()
        if not owner or not token:
            raise ValueError("owner_id_and_lease_token_required")
        ttl = float(ttl_seconds)
        if ttl <= 0:
            raise ValueError("ttl_seconds_must_be_positive")
        now = float(self.clock())

        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                row = conn.execute(
                    "SELECT * FROM resource_leases WHERE resource_type=? AND resource_key=?",
                    (kind, key),
                ).fetchone()
                if row is None:
                    conn.execute("COMMIT")
                    return {"status": "lost", "reason": "lease_not_found"}
                lease = self._row_to_lease(row)
                if lease.expires_at <= now:
                    conn.execute("DELETE FROM resource_leases WHERE resource_type=? AND resource_key=?", (kind, key))
                    conn.execute("COMMIT")
                    return {"status": "lost", "reason": "lease_expired"}
                if lease.owner_id != owner or lease.lease_token != token:
                    conn.execute("COMMIT")
                    return {"status": "lost", "reason": "lease_fenced", "lease": lease.to_dict()}
                expires = now + ttl
                conn.execute(
                    "UPDATE resource_leases SET heartbeat_at=?, expires_at=? WHERE resource_type=? AND resource_key=?",
                    (now, expires, kind, key),
                )
                conn.execute("COMMIT")
                updated = ResourceLease(kind, key, owner, token, lease.acquired_at, now, expires, lease.metadata)
                return {"status": "ok", "reason": "lease_heartbeat", "lease": updated.to_dict()}
            except Exception:
                conn.execute("ROLLBACK")
                raise

    def release(
        self,
        *,
        resource_type: str,
        resource_key: str,
        owner_id: str,
        lease_token: str,
    ) -> dict[str, Any]:
        kind, key = _normalize_resource(resource_type, resource_key)
        owner = str(owner_id or "").strip()
        token = str(lease_token or "").strip()
        if not owner or not token:
            raise ValueError("owner_id_and_lease_token_required")
        now = float(self.clock())

        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                row = conn.execute(
                    "SELECT * FROM resource_leases WHERE resource_type=? AND resource_key=?",
                    (kind, key),
                ).fetchone()
                if row is None:
                    conn.execute("COMMIT")
                    return {"status": "ok", "reason": "no_active_lease", "idempotent": True}
                lease = self._row_to_lease(row)
                if lease.expires_at <= now:
                    conn.execute("DELETE FROM resource_leases WHERE resource_type=? AND resource_key=?", (kind, key))
                    conn.execute("COMMIT")
                    return {"status": "ok", "reason": "expired_lease_cleared", "idempotent": True}
                if lease.owner_id != owner or lease.lease_token != token:
                    conn.execute("COMMIT")
                    return {"status": "blocked", "reason": "lease_fenced", "lease": lease.to_dict()}
                conn.execute("DELETE FROM resource_leases WHERE resource_type=? AND resource_key=?", (kind, key))
                conn.execute("COMMIT")
                return {"status": "ok", "reason": "lease_released", "idempotent": False}
            except Exception:
                conn.execute("ROLLBACK")
                raise

    def list_active(self) -> list[dict[str, Any]]:
        now = float(self.clock())
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                rows = self._active_rows(conn, now)
                conn.execute("COMMIT")
                return [self._row_to_lease(row).to_dict() for row in rows]
            except Exception:
                conn.execute("ROLLBACK")
                raise
