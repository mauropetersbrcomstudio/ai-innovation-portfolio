"""SQLite-checkpointed sequential runner with an explicit idempotent-handler contract."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[3]
SKILLS = ROOT / "Demo Templates" / "AI Skills & Tooling"
sys.path.insert(0, str(SKILLS / "agent-state-store"))
sys.path.insert(0, str(SKILLS / "agent-observability"))

from state_store import StateStore  # noqa: E402
from observability import JsonlEventLogger  # noqa: E402


class PlanConflictError(ValueError):
    """Raised when a persisted workflow is resumed with a different plan."""


def _fingerprint(step_ids: list[str], context: dict[str, Any]) -> str:
    encoded = json.dumps({"steps": step_ids, "context": context}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def run_durable_workflow(
    workflow_id: str,
    steps: list[str],
    handlers: dict[str, Callable[[dict[str, Any]], Any]],
    context: dict[str, Any],
    database: str | Path,
    event_log: str | Path,
) -> dict[str, Any]:
    """Run or resume a fixed plan.

    Each handler MUST be idempotent for the supplied idempotency_key. This is
    essential for the crash window between a handler's side effect and its
    completion checkpoint. The runner cannot enforce external idempotency.
    """
    if not isinstance(workflow_id, str) or not workflow_id.strip():
        raise ValueError("workflow_id must be a non-empty string")
    if not isinstance(steps, list) or not steps or len(steps) > 20:
        raise ValueError("steps must contain between 1 and 20 handler names")
    if any(not isinstance(name, str) or not name for name in steps) or len(steps) != len(set(steps)):
        raise ValueError("step handler names must be non-empty and unique")
    if not isinstance(context, dict):
        raise ValueError("context must be an object")
    if any(name not in handlers or not callable(handlers[name]) for name in steps):
        raise ValueError("Every step must have a registered callable handler")

    store = StateStore(database)
    logger = JsonlEventLogger(event_log)
    fingerprint = _fingerprint(steps, context)
    existing = store.get(workflow_id)
    if existing is None:
        state = {
            "status": "RUNNING",
            "plan_fingerprint": fingerprint,
            "steps": steps,
            "context": context,
            "completed_steps": [],
            "outputs": {},
            "attempts": {},
        }
        store.create(workflow_id, state)
        version = 1
        _record(store, logger, workflow_id, "WORKFLOW_CREATED", {"step_count": len(steps)})
    else:
        state = existing["state"]
        version = existing["version"]
        if state.get("plan_fingerprint") != fingerprint:
            raise PlanConflictError("Persisted workflow plan or context does not match this resume request")
        if state.get("status") == "COMPLETED":
            return {"workflow": existing, "events": store.events(workflow_id), "resumed": True}
        if state.get("status") not in {"RUNNING", "FAILED"}:
            raise ValueError(f"Workflow cannot resume from status {state.get('status')!r}")
        state["status"] = "RUNNING"
        saved = store.save(workflow_id, state, expected_version=version)
        version = saved["version"]
        _record(store, logger, workflow_id, "WORKFLOW_RESUMED", {"completed_steps": list(state["completed_steps"])})

    for handler_name in steps:
        if handler_name in state["completed_steps"]:
            continue
        attempt = state["attempts"].get(handler_name, 0) + 1
        state["attempts"][handler_name] = attempt
        state["status"] = "RUNNING"
        saved = store.save(workflow_id, state, expected_version=version)
        version = saved["version"]
        _record(store, logger, workflow_id, "STEP_STARTED", {"step_id": handler_name, "attempt": attempt})

        idempotency_key = hashlib.sha256(f"{workflow_id}:{fingerprint}:{handler_name}".encode()).hexdigest()
        try:
            output = handlers[handler_name]({
                "workflow_id": workflow_id,
                "step_id": handler_name,
                "idempotency_key": idempotency_key,
                "context": dict(context),
                "previous_outputs": dict(state["outputs"]),
            })
            # Validate JSON compatibility before writing a completion checkpoint.
            json.dumps(output, ensure_ascii=False, sort_keys=True)
        except Exception as exc:
            state["status"] = "FAILED"
            saved = store.save(workflow_id, state, expected_version=version)
            version = saved["version"]
            _record(store, logger, workflow_id, "STEP_FAILED", {
                "step_id": handler_name, "attempt": attempt, "error_type": type(exc).__name__,
            }, level="ERROR")
            return {"workflow": store.get(workflow_id), "events": store.events(workflow_id), "resumed": existing is not None}

        state["outputs"][handler_name] = output
        state["completed_steps"].append(handler_name)
        saved = store.save(workflow_id, state, expected_version=version)
        version = saved["version"]
        _record(store, logger, workflow_id, "STEP_COMPLETED", {"step_id": handler_name, "attempt": attempt})

    state["status"] = "COMPLETED"
    store.save(workflow_id, state, expected_version=version)
    _record(store, logger, workflow_id, "WORKFLOW_COMPLETED", {"completed_steps": list(state["completed_steps"])})
    return {"workflow": store.get(workflow_id), "events": store.events(workflow_id), "resumed": existing is not None}


def _record(store: StateStore, logger: JsonlEventLogger, workflow_id: str,
            event_type: str, details: dict[str, Any], *, level: str = "INFO") -> None:
    payload = {"event": event_type, "workflow_id": workflow_id, "details": details}
    store.append_event(workflow_id, event_type, payload)
    logger.emit(event_type, level=level, workflow_id=workflow_id, details=details)
