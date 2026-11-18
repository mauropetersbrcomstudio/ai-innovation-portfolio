"""SQLite-backed workflow state and append-only event store (stdlib only)."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class StateConflictError(RuntimeError):
    """Raised when an update is based on a stale state version."""


class StateStore:
    def __init__(self, database: str | Path):
        self.database = str(database)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS workflow_states (
                    workflow_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    state_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS workflow_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(workflow_id) REFERENCES workflow_states(workflow_id)
                )
            """)

    @staticmethod
    def _json(value: Any) -> str:
        try:
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        except (TypeError, ValueError) as exc:
            raise ValueError("Value must be JSON-serializable") from exc

    def create(self, workflow_id: str, state: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(workflow_id, str) or not workflow_id.strip():
            raise ValueError("workflow_id must be a non-empty string")
        if not isinstance(state, dict):
            raise ValueError("state must be a JSON object")
        encoded = self._json(state)
        status = state.get("status", "PENDING")
        if not isinstance(status, str) or not status:
            raise ValueError("state.status must be a non-empty string")
        try:
            with self._connect() as db:
                db.execute(
                    "INSERT INTO workflow_states(workflow_id,status,version,state_json) VALUES(?,?,?,?)",
                    (workflow_id, status, 1, encoded),
                )
        except sqlite3.IntegrityError as exc:
            raise ValueError(f"Workflow already exists: {workflow_id}") from exc
        return {"workflow_id": workflow_id, "version": 1, "status": status, "state": state}

    def get(self, workflow_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT workflow_id,status,version,state_json,created_at,updated_at FROM workflow_states WHERE workflow_id=?",
                (workflow_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "workflow_id": row["workflow_id"],
            "status": row["status"],
            "version": row["version"],
            "state": json.loads(row["state_json"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def save(self, workflow_id: str, state: dict[str, Any], *, expected_version: int) -> dict[str, Any]:
        if not isinstance(state, dict):
            raise ValueError("state must be a JSON object")
        if not isinstance(expected_version, int) or expected_version < 1:
            raise ValueError("expected_version must be a positive integer")
        encoded = self._json(state)
        status = state.get("status", "PENDING")
        if not isinstance(status, str) or not status:
            raise ValueError("state.status must be a non-empty string")
        with self._connect() as db:
            cursor = db.execute(
                """UPDATE workflow_states
                   SET status=?, state_json=?, version=version+1, updated_at=CURRENT_TIMESTAMP
                   WHERE workflow_id=? AND version=?""",
                (status, encoded, workflow_id, expected_version),
            )
            if cursor.rowcount != 1:
                current = db.execute(
                    "SELECT version FROM workflow_states WHERE workflow_id=?", (workflow_id,)
                ).fetchone()
                if current is None:
                    raise KeyError(f"Unknown workflow: {workflow_id}")
                raise StateConflictError(
                    f"Stale workflow version: expected {expected_version}, current {current['version']}"
                )
        return {"workflow_id": workflow_id, "version": expected_version + 1, "status": status, "state": state}

    def append_event(self, workflow_id: str, event_type: str, payload: dict[str, Any]) -> int:
        if not isinstance(event_type, str) or not event_type.strip():
            raise ValueError("event_type must be a non-empty string")
        if not isinstance(payload, dict):
            raise ValueError("event payload must be a JSON object")
        encoded = self._json(payload)
        with self._connect() as db:
            cursor = db.execute(
                "INSERT INTO workflow_events(workflow_id,event_type,payload_json) VALUES(?,?,?)",
                (workflow_id, event_type, encoded),
            )
            return int(cursor.lastrowid)

    def events(self, workflow_id: str) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute(
                """SELECT event_id,event_type,payload_json,created_at
                   FROM workflow_events WHERE workflow_id=? ORDER BY event_id""",
                (workflow_id,),
            ).fetchall()
        return [
            {"event_id": row["event_id"], "event_type": row["event_type"],
             "payload": json.loads(row["payload_json"]), "created_at": row["created_at"]}
            for row in rows
        ]
