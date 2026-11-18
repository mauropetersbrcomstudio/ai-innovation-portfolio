"""Local reference control plane for agent registration, lifecycle, policy and audit."""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


LIFECYCLE = {"REGISTERED", "ACTIVE", "PAUSED", "RETIRED"}
HEALTH = {"UNKNOWN", "HEALTHY", "DEGRADED", "UNHEALTHY"}


@dataclass(frozen=True)
class AgentSpec:
    agent_id: str
    role: str
    allowed_tools: tuple[str, ...]
    approval_required_for: tuple[str, ...] = ()
    max_invocations: int = 10


class RuntimeControlPlane:
    """SQLite-backed control plane. Tool handlers remain local to the host process."""

    def __init__(self, database: str | Path, handlers: dict[str, Callable[[dict[str, Any]], Any]]):
        self.database = str(database)
        self.handlers = dict(handlers)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.database, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY,
                    role TEXT NOT NULL,
                    allowed_tools TEXT NOT NULL,
                    approval_required_for TEXT NOT NULL,
                    max_invocations INTEGER NOT NULL,
                    invocation_count INTEGER NOT NULL DEFAULT 0,
                    lifecycle TEXT NOT NULL,
                    health TEXT NOT NULL DEFAULT 'UNKNOWN',
                    last_heartbeat TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS runtime_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS escalations (
                    escalation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    context TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'OPEN',
                    resolution TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TEXT
                )
            """)

    @staticmethod
    def _encode(value: Any) -> str:
        try:
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        except (TypeError, ValueError) as exc:
            raise ValueError("Value must be JSON-serializable") from exc

    def _event(self, db: sqlite3.Connection, agent_id: str | None,
               event_type: str, payload: dict[str, Any]) -> None:
        db.execute(
            "INSERT INTO runtime_events(agent_id,event_type,payload) VALUES(?,?,?)",
            (agent_id, event_type, self._encode(payload)),
        )

    def register(self, spec: AgentSpec) -> dict[str, Any]:
        if not isinstance(spec.agent_id, str) or not spec.agent_id.strip():
            raise ValueError("agent_id must be a non-empty string")
        if not isinstance(spec.role, str) or not spec.role.strip():
            raise ValueError("role must be a non-empty string")
        if not spec.allowed_tools or len(set(spec.allowed_tools)) != len(spec.allowed_tools):
            raise ValueError("allowed_tools must be non-empty and unique")
        if any(not isinstance(tool, str) or not tool.strip() or tool == "*" for tool in spec.allowed_tools):
            raise ValueError("allowed_tools must contain explicit non-wildcard tool names")
        if not set(spec.approval_required_for).issubset(set(spec.allowed_tools)):
            raise ValueError("approval_required_for must be a subset of allowed_tools")
        if not isinstance(spec.max_invocations, int) or isinstance(spec.max_invocations, bool) or spec.max_invocations < 1:
            raise ValueError("max_invocations must be a positive integer")
        missing = set(spec.allowed_tools) - set(self.handlers)
        if missing:
            raise ValueError(f"Handlers are not registered for tools: {sorted(missing)}")
        with self._connect() as db:
            db.execute(
                """INSERT INTO agents(agent_id,role,allowed_tools,approval_required_for,
                   max_invocations,lifecycle) VALUES(?,?,?,?,?,'REGISTERED')""",
                (spec.agent_id, spec.role, self._encode(list(spec.allowed_tools)),
                 self._encode(list(spec.approval_required_for)), spec.max_invocations),
            )
            self._event(db, spec.agent_id, "AGENT_REGISTERED", {"role": spec.role})
        return self.get_agent(spec.agent_id)

    def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM agents WHERE agent_id=?", (agent_id,)).fetchone()
        if row is None:
            return None
        return {
            "agent_id": row["agent_id"], "role": row["role"],
            "allowed_tools": json.loads(row["allowed_tools"]),
            "approval_required_for": json.loads(row["approval_required_for"]),
            "max_invocations": row["max_invocations"],
            "invocation_count": row["invocation_count"],
            "lifecycle": row["lifecycle"], "health": row["health"],
            "last_heartbeat": row["last_heartbeat"],
        }

    def transition(self, agent_id: str, target: str) -> dict[str, Any]:
        allowed = {
            "REGISTERED": {"ACTIVE", "RETIRED"},
            "ACTIVE": {"PAUSED", "RETIRED"},
            "PAUSED": {"ACTIVE", "RETIRED"},
            "RETIRED": set(),
        }
        with self._connect() as db:
            row = db.execute("SELECT lifecycle FROM agents WHERE agent_id=?", (agent_id,)).fetchone()
            if row is None:
                raise KeyError(f"Unknown agent: {agent_id}")
            current = row["lifecycle"]
            if target not in allowed[current]:
                raise ValueError(f"Invalid lifecycle transition: {current} -> {target}")
            db.execute("UPDATE agents SET lifecycle=?,updated_at=CURRENT_TIMESTAMP WHERE agent_id=?",
                       (target, agent_id))
            self._event(db, agent_id, "LIFECYCLE_CHANGED", {"from": current, "to": target})
        return self.get_agent(agent_id)

    def heartbeat(self, agent_id: str, health: str) -> dict[str, Any]:
        if health not in HEALTH - {"UNKNOWN"}:
            raise ValueError("health must be HEALTHY, DEGRADED, or UNHEALTHY")
        with self._connect() as db:
            row = db.execute("SELECT lifecycle FROM agents WHERE agent_id=?", (agent_id,)).fetchone()
            if row is None:
                raise KeyError(f"Unknown agent: {agent_id}")
            db.execute(
                "UPDATE agents SET health=?,last_heartbeat=CURRENT_TIMESTAMP,updated_at=CURRENT_TIMESTAMP WHERE agent_id=?",
                (health, agent_id),
            )
            self._event(db, agent_id, "HEALTH_REPORTED", {"health": health})
        if health == "UNHEALTHY":
            self.escalate(agent_id, "AGENT_REPORTED_UNHEALTHY", {"health": health})
        return self.get_agent(agent_id)

    def invoke(self, agent_id: str, tool: str, arguments: dict[str, Any], *,
               approved_tools: tuple[str, ...] = ()) -> dict[str, Any]:
        with self._connect() as db:
            row = db.execute("SELECT * FROM agents WHERE agent_id=?", (agent_id,)).fetchone()
            if row is None:
                raise KeyError(f"Unknown agent: {agent_id}")
            allowed = json.loads(row["allowed_tools"])
            approval_required = json.loads(row["approval_required_for"])
            count = row["invocation_count"]
            reason = None
            if row["lifecycle"] != "ACTIVE":
                reason = "AGENT_NOT_ACTIVE"
            elif row["health"] in {"DEGRADED", "UNHEALTHY"}:
                reason = "AGENT_HEALTH_BLOCKED"
            elif tool not in allowed:
                reason = "TOOL_NOT_ALLOWLISTED"
            elif tool not in self.handlers:
                reason = "TOOL_HANDLER_UNAVAILABLE"
            elif tool in approval_required and tool not in approved_tools:
                reason = "HUMAN_APPROVAL_REQUIRED"
            elif count >= row["max_invocations"]:
                reason = "INVOCATION_LIMIT_REACHED"
            if reason:
                self._event(db, agent_id, "INVOCATION_DENIED", {"tool": tool, "reason": reason})
                return {"status": "DENIED", "reason": reason}
            db.execute("UPDATE agents SET invocation_count=invocation_count+1,updated_at=CURRENT_TIMESTAMP WHERE agent_id=?",
                       (agent_id,))
            self._event(db, agent_id, "INVOCATION_ACCEPTED", {"tool": tool, "role": row["role"]})

        try:
            output = self.handlers[tool](dict(arguments))
            self._encode(output)
        except Exception as exc:
            with self._connect() as db:
                self._event(db, agent_id, "INVOCATION_FAILED", {"tool": tool, "error_type": type(exc).__name__})
            return {"status": "ERROR", "reason": "HANDLER_FAILED"}
        with self._connect() as db:
            self._event(db, agent_id, "INVOCATION_COMPLETED", {"tool": tool})
        return {"status": "EXECUTED", "tool": tool, "output": output}

    def escalate(self, agent_id: str, reason: str, context: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("reason must be a non-empty string")
        encoded = self._encode(context)
        with self._connect() as db:
            if db.execute("SELECT 1 FROM agents WHERE agent_id=?", (agent_id,)).fetchone() is None:
                raise KeyError(f"Unknown agent: {agent_id}")
            cursor = db.execute(
                "INSERT INTO escalations(agent_id,reason,context) VALUES(?,?,?)",
                (agent_id, reason, encoded),
            )
            escalation_id = int(cursor.lastrowid)
            self._event(db, agent_id, "HUMAN_ESCALATION_OPENED",
                        {"escalation_id": escalation_id, "reason": reason})
        return self.get_escalation(escalation_id)

    def get_escalation(self, escalation_id: int) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM escalations WHERE escalation_id=?", (escalation_id,)).fetchone()
        if row is None:
            return None
        return {
            "escalation_id": row["escalation_id"], "agent_id": row["agent_id"],
            "reason": row["reason"], "context": json.loads(row["context"]),
            "status": row["status"], "resolution": row["resolution"],
        }

    def resolve_escalation(self, escalation_id: int, resolution: str) -> dict[str, Any]:
        if not isinstance(resolution, str) or not resolution.strip():
            raise ValueError("resolution must be a non-empty string")
        with self._connect() as db:
            row = db.execute("SELECT agent_id,status FROM escalations WHERE escalation_id=?",
                             (escalation_id,)).fetchone()
            if row is None:
                raise KeyError(f"Unknown escalation: {escalation_id}")
            if row["status"] != "OPEN":
                raise ValueError("Escalation is already resolved")
            db.execute(
                "UPDATE escalations SET status='RESOLVED',resolution=?,resolved_at=CURRENT_TIMESTAMP WHERE escalation_id=?",
                (resolution, escalation_id),
            )
            self._event(db, row["agent_id"], "HUMAN_ESCALATION_RESOLVED",
                        {"escalation_id": escalation_id, "resolution": resolution})
        return self.get_escalation(escalation_id)

    def audit_report(self, agent_id: str) -> dict[str, Any]:
        """Read-only audit projection, separate from command methods."""
        with self._connect() as db:
            agent = db.execute("SELECT * FROM agents WHERE agent_id=?", (agent_id,)).fetchone()
            if agent is None:
                raise KeyError(f"Unknown agent: {agent_id}")
            events = db.execute(
                "SELECT event_id,event_type,payload,created_at FROM runtime_events WHERE agent_id=? ORDER BY event_id",
                (agent_id,),
            ).fetchall()
            open_escalations = db.execute(
                "SELECT COUNT(*) AS n FROM escalations WHERE agent_id=? AND status='OPEN'", (agent_id,)
            ).fetchone()["n"]
        event_items = [{"event_id": row["event_id"], "event_type": row["event_type"],
                        "payload": json.loads(row["payload"]), "created_at": row["created_at"]}
                       for row in events]
        return {
            "agent_id": agent_id,
            "lifecycle": agent["lifecycle"],
            "health": agent["health"],
            "invocation_count": agent["invocation_count"],
            "open_escalations": open_escalations,
            "event_count": len(event_items),
            "events": event_items,
        }
