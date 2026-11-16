"""Small SQLite-backed reference gateway for SFI-04b.

The gateway demonstrates durable acceptance semantics without choosing a production
broker or database. It stores source payloads and delivery state in one transaction;
production deployments can replace the repository while preserving these semantics.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


class IngestionError(ValueError):
    """A delivery failed a structural, authentication, or tenant-boundary check."""


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class IngestionGateway:
    """Durable, at-least-once intake with connection-derived tenant authority."""

    def __init__(self, database: str | Path, schema_path: str | Path, *, max_attempts: int = 5):
        self.database = str(database)
        self.max_attempts = max_attempts
        schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        self.validator = Draft202012Validator(schema, format_checker=FormatChecker())
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS connections (
                    connection_id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL,
                    workspace_id TEXT NOT NULL, source_system TEXT NOT NULL,
                    source_instance_id TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1
                );
                CREATE TABLE IF NOT EXISTS deliveries (
                    delivery_id TEXT PRIMARY KEY, connection_id TEXT NOT NULL,
                    tenant_id TEXT NOT NULL, idempotency_key TEXT NOT NULL,
                    payload_digest TEXT NOT NULL, envelope_json TEXT NOT NULL,
                    payload_bytes BLOB, archive_ref TEXT, status TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0, last_error TEXT,
                    accepted_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    UNIQUE(connection_id, idempotency_key),
                    FOREIGN KEY(connection_id) REFERENCES connections(connection_id)
                );
                CREATE TABLE IF NOT EXISTS checkpoints (
                    connection_id TEXT NOT NULL, partition_key TEXT NOT NULL,
                    cursor_value TEXT NOT NULL, delivery_id TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY(connection_id, partition_key)
                );
            """)

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.database, timeout=30, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA journal_mode=WAL")
        return db

    def register_connection(self, *, connection_id: str, tenant_id: str,
                            workspace_id: str, source_system: str,
                            source_instance_id: str, enabled: bool = True) -> None:
        """Provision trusted connection state out-of-band from delivery envelopes."""
        with self._connect() as db:
            db.execute("""INSERT INTO connections VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(connection_id) DO UPDATE SET tenant_id=excluded.tenant_id,
                workspace_id=excluded.workspace_id, source_system=excluded.source_system,
                source_instance_id=excluded.source_instance_id, enabled=excluded.enabled""",
                (connection_id, tenant_id, workspace_id, source_system,
                 source_instance_id, int(enabled)))

    def accept(self, envelope: dict[str, Any], *, authenticated_connection_id: str) -> dict[str, Any]:
        """Validate, bind tenant from trusted connection state, and durably accept.

        A successful return means the delivery row and payload are committed. It does
        not claim exactly-once transport or successful downstream normalization.
        """
        errors = sorted(self.validator.iter_errors(envelope), key=lambda e: list(map(str, e.path)))
        if errors:
            raise IngestionError("schema-invalid: " + "; ".join(e.message for e in errors[:4]))
        if envelope.get("recordType") != "delivery-envelope":
            raise IngestionError("wrong-record-type")
        if envelope["connectionId"] != authenticated_connection_id:
            raise IngestionError("authenticated-connection-mismatch")
        if envelope["authentication"].get("verified") is not True:
            raise IngestionError("authentication-not-verified")

        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            conn = db.execute("SELECT * FROM connections WHERE connection_id=?",
                              (authenticated_connection_id,)).fetchone()
            if conn is None or not conn["enabled"]:
                db.rollback()
                raise IngestionError("connection-unknown-or-disabled")
            src = envelope["source"]
            if (envelope["tenantId"] != conn["tenant_id"] or
                envelope["workspaceId"] != conn["workspace_id"] or
                src["system"] != conn["source_system"] or
                src["instanceId"] != conn["source_instance_id"]):
                db.rollback()
                raise IngestionError("tenant-workspace-or-source-binding-mismatch")

            payload = envelope["payload"]
            inline = payload.get("inline")
            raw = _canonical(inline) if inline is not None else None
            actual_digest = hashlib.sha256(raw).hexdigest() if raw is not None else None
            declared = payload["digest"]["value"].lower()
            if actual_digest is not None and actual_digest != declared:
                db.rollback()
                raise IngestionError("payload-digest-mismatch")
            if raw is not None and len(raw) != payload["sizeBytes"]:
                db.rollback()
                raise IngestionError("payload-size-mismatch")

            # Prefer stable source event identity, then source revision, then digest.
            idem = src.get("eventId") or (
                f"{src['objectType']}:{src['objectId']}:{src['objectVersion']}"
                if src.get("objectVersion") else
                f"{src['objectType']}:{src['objectId']}:{declared}")
            existing = db.execute("SELECT delivery_id,status FROM deliveries "
                                   "WHERE connection_id=? AND idempotency_key=?",
                                   (authenticated_connection_id, idem)).fetchone()
            if existing:
                db.commit()
                return {"outcome": "duplicate", "deliveryId": existing["delivery_id"],
                        "status": existing["status"], "idempotencyKey": idem}

            now = _utcnow()
            archive_ref = payload.get("archiveRef")
            db.execute("""INSERT INTO deliveries
                (delivery_id,connection_id,tenant_id,idempotency_key,payload_digest,
                 envelope_json,payload_bytes,archive_ref,status,attempts,accepted_at,updated_at)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (envelope["deliveryId"], authenticated_connection_id, conn["tenant_id"],
                 idem, declared, _canonical(envelope).decode("utf-8"), raw,
                 archive_ref, "accepted", 0, now, now))
            # Checkpoint advancement is atomic with durable acceptance, never before it.
            cursor = envelope["delivery"].get("sourceCursor")
            if cursor:
                partition = envelope["delivery"].get("partition", "default")
                db.execute("""INSERT INTO checkpoints VALUES (?,?,?,?,?)
                    ON CONFLICT(connection_id,partition_key) DO UPDATE SET
                    cursor_value=excluded.cursor_value, delivery_id=excluded.delivery_id,
                    updated_at=excluded.updated_at""",
                    (authenticated_connection_id, partition, cursor,
                     envelope["deliveryId"], now))
            db.commit()
            return {"outcome": "accepted", "deliveryId": envelope["deliveryId"],
                    "status": "accepted", "idempotencyKey": idem}

    def mark_processing(self, delivery_id: str) -> None:
        with self._connect() as db:
            cur = db.execute("UPDATE deliveries SET status='processing', updated_at=? "
                             "WHERE delivery_id=? AND status IN ('accepted','retry')",
                             (_utcnow(), delivery_id))
            if cur.rowcount != 1:
                raise IngestionError("delivery-not-ready")

    def mark_failed(self, delivery_id: str, error_code: str) -> dict[str, Any]:
        """Record a bounded retry; terminal failures enter quarantine."""
        if not error_code or len(error_code) > 160:
            raise IngestionError("invalid-error-code")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT attempts,status FROM deliveries WHERE delivery_id=?",
                             (delivery_id,)).fetchone()
            if row is None:
                db.rollback()
                raise IngestionError("delivery-not-found")
            if row["status"] not in ("accepted", "processing", "retry"):
                db.rollback()
                raise IngestionError("delivery-not-retryable")
            attempts = row["attempts"] + 1
            status = "quarantined" if attempts >= self.max_attempts else "retry"
            db.execute("UPDATE deliveries SET attempts=?,status=?,last_error=?,updated_at=? " 
                       "WHERE delivery_id=?",
                       (attempts, status, error_code, _utcnow(), delivery_id))
            db.commit()
            return {"deliveryId": delivery_id, "status": status, "attempts": attempts}

    def replay(self, delivery_id: str) -> dict[str, Any]:
        """Explicitly requeue quarantined work; original evidence/idempotency remain."""
        with self._connect() as db:
            cur = db.execute("UPDATE deliveries SET status='retry',attempts=0,last_error=NULL,updated_at=? "
                             "WHERE delivery_id=? AND status='quarantined'", (_utcnow(), delivery_id))
            if cur.rowcount != 1:
                raise IngestionError("delivery-not-quarantined")
        return {"deliveryId": delivery_id, "status": "retry", "attempts": 0}

    def get_delivery(self, delivery_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute("SELECT delivery_id,tenant_id,status,attempts,last_error,"
                             "payload_digest,archive_ref,accepted_at,updated_at "
                             "FROM deliveries WHERE delivery_id=?", (delivery_id,)).fetchone()
            return dict(row) if row else None

    def get_checkpoint(self, connection_id: str, partition: str = "default") -> str | None:
        with self._connect() as db:
            row = db.execute("SELECT cursor_value FROM checkpoints WHERE connection_id=? AND partition_key=?",
                             (connection_id, partition)).fetchone()
            return row["cursor_value"] if row else None
