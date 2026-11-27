"""Durable human-review decision capture for the Intake Operations Hub."""
from __future__ import annotations
import json, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Demo Templates" / "AI Skills & Tooling" / "agent-state-store"))
from state_store import StateStore
OUTCOMES = {"ACCEPTED_FOR_NEXT_STAGE", "REJECTED", "REQUESTED_INFORMATION"}

class ReviewDecisionStore:
    """Append-only-by-interface review records; reviewer identity is host-asserted."""
    def __init__(self, database: str | Path):
        self.database = str(database)
        self.state_store = StateStore(database)
        with sqlite3.connect(self.database) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS human_review_decisions (
                decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL, item_id TEXT NOT NULL, reviewer_id TEXT NOT NULL,
                outcome TEXT NOT NULL, reason TEXT NOT NULL, created_at TEXT NOT NULL,
                UNIQUE(workflow_id, item_id),
                FOREIGN KEY(workflow_id) REFERENCES workflow_states(workflow_id))""")

    def record(self, workflow_id: str, item_id: str, reviewer_id: str, outcome: str, reason: str) -> dict[str, Any]:
        for field, value in (("workflow_id", workflow_id), ("item_id", item_id), ("reviewer_id", reviewer_id), ("reason", reason)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} must be a non-empty string")
        if outcome not in OUTCOMES:
            raise ValueError("Unsupported review outcome")
        workflow = self.state_store.get(workflow_id)
        if workflow is None:
            raise KeyError(f"Unknown workflow: {workflow_id}")
        if workflow["status"] != "COMPLETED":
            raise ValueError("Decision requires a completed intake workflow")
        queue = workflow["state"].get("outputs", {}).get("prepare_human_review", {})
        if sum(1 for item in queue.get("items", []) if item.get("item_id") == item_id) != 1:
            raise KeyError(f"Unknown review item: {item_id}")
        created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        payload = {"workflow_id": workflow_id, "item_id": item_id, "reviewer_id": reviewer_id,
                   "outcome": outcome, "reason": reason.strip(), "created_at": created_at}
        try:
            with sqlite3.connect(self.database, timeout=10) as db:
                db.execute("PRAGMA foreign_keys = ON")
                cursor = db.execute("""INSERT INTO human_review_decisions
                    (workflow_id,item_id,reviewer_id,outcome,reason,created_at) VALUES(?,?,?,?,?,?)""",
                    (workflow_id, item_id, reviewer_id, outcome, reason.strip(), created_at))
                decision_id = cursor.lastrowid
                db.execute("INSERT INTO workflow_events(workflow_id,event_type,payload_json) VALUES(?,?,?)",
                    (workflow_id, "HUMAN_REVIEW_DECISION_RECORDED",
                     json.dumps({**payload, "decision_id": decision_id}, ensure_ascii=False, sort_keys=True)))
        except sqlite3.IntegrityError as exc:
            raise ValueError("A decision already exists for this workflow review item") from exc
        return {"decision_id": decision_id, **payload}

    def list_for_workflow(self, workflow_id: str) -> list[dict[str, Any]]:
        with sqlite3.connect(self.database) as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT decision_id,workflow_id,item_id,reviewer_id,outcome,reason,created_at FROM human_review_decisions WHERE workflow_id=? ORDER BY decision_id", (workflow_id,)).fetchall()
        return [dict(row) for row in rows]
