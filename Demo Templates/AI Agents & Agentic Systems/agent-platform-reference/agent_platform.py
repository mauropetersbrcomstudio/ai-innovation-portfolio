"""Reference integration of orchestration, SQLite state, and structured observability."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
for component in ("agent-orchestration", "agent-state-store", "agent-observability"):
    sys.path.insert(0, str(ROOT / "Demo Templates" / "AI Skills & Tooling" / component))

from orchestrator import Orchestrator, Step, state_to_dict  # noqa: E402
from state_store import StateStore  # noqa: E402
from observability import JsonlEventLogger  # noqa: E402


def execute_reference_workflow(workflow_id: str, request: str, database: str | Path,
                               event_log: str | Path) -> dict[str, Any]:
    store = StateStore(database)
    logger = JsonlEventLogger(event_log)
    initial = {"status": "PENDING", "request": request, "completed_steps": [], "outputs": {}}
    store.create(workflow_id, initial)
    logger.emit("WORKFLOW_CREATED", workflow_id=workflow_id, details={"request_length": len(request)})

    def validate(payload: dict[str, Any]) -> dict[str, Any]:
        text = payload["context"]["request"]
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Request text is required")
        return {"accepted": True, "request": text.strip()}

    def prepare(payload: dict[str, Any]) -> dict[str, Any]:
        validated = payload["previous_outputs"]["validation"]
        return {"queue": "human_review", "request": validated["request"], "external_action": False}

    engine = Orchestrator({"validate": validate, "prepare": prepare})
    steps = [Step("validation", "validate"), Step("preparation", "prepare")]
    state = engine.start(workflow_id, steps, {"request": request})
    serialized = state_to_dict(state)
    persisted = {
        "status": serialized["status"],
        "request": request,
        "completed_steps": serialized["completed_steps"],
        "outputs": serialized["outputs"],
        "attempts": serialized["attempts"],
    }
    store.save(workflow_id, persisted, expected_version=1)
    for event in serialized["events"]:
        event_type = event["event"]
        store.append_event(workflow_id, event_type, event)
        logger.emit(event_type, workflow_id=workflow_id, details=event)
    return {
        "workflow": store.get(workflow_id),
        "events": store.events(workflow_id),
        "log_events": logger.read_events(),
        "notice": "Reference integration only. No external business system was contacted.",
    }


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Run the reference agent platform integration.")
    parser.add_argument("--workflow-id", default="reference-001")
    parser.add_argument("--request", required=True)
    parser.add_argument("--database", default="runtime/workflows.db")
    parser.add_argument("--event-log", default="runtime/events.jsonl")
    args = parser.parse_args()
    result = execute_reference_workflow(args.workflow_id, args.request, args.database, args.event_log)
    print(json.dumps(result, indent=2, ensure_ascii=False))
