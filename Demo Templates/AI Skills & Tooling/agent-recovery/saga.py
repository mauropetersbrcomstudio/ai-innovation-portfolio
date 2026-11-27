"""Bounded sequential execution with reverse-order compensating handlers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class SagaStep:
    step_id: str
    execute: Callable[[dict[str, Any]], Any]
    compensate: Callable[[dict[str, Any], Any], Any] | None = None
    max_attempts: int = 1


def run_saga(steps: list[SagaStep], context: dict[str, Any] | None = None,
             *, max_steps: int = 20) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    completed: list[tuple[SagaStep, Any]] = []
    outputs: dict[str, Any] = {}
    if not steps or len(steps) > max_steps:
        return {"status": "REJECTED", "reason": "INVALID_STEP_COUNT", "events": events, "outputs": outputs}
    ids = [step.step_id for step in steps]
    if any(not item for item in ids) or len(ids) != len(set(ids)):
        return {"status": "REJECTED", "reason": "INVALID_STEP_IDS", "events": events, "outputs": outputs}
    if any(step.max_attempts < 1 or not callable(step.execute) for step in steps):
        return {"status": "REJECTED", "reason": "INVALID_STEP_CONFIGURATION", "events": events, "outputs": outputs}

    base_context = dict(context or {})
    for step in steps:
        success = False
        for attempt in range(1, step.max_attempts + 1):
            events.append({"event": "STEP_STARTED", "step_id": step.step_id, "attempt": attempt})
            try:
                result = step.execute({"context": dict(base_context), "outputs": dict(outputs)})
            except Exception:
                events.append({"event": "STEP_FAILED", "step_id": step.step_id, "attempt": attempt})
                continue
            outputs[step.step_id] = result
            completed.append((step, result))
            events.append({"event": "STEP_COMPLETED", "step_id": step.step_id, "attempt": attempt})
            success = True
            break
        if success:
            continue

        events.append({"event": "SAGA_COMPENSATION_STARTED", "failed_step": step.step_id})
        compensation_errors: list[str] = []
        for completed_step, result in reversed(completed):
            if completed_step.compensate is None:
                events.append({"event": "COMPENSATION_SKIPPED", "step_id": completed_step.step_id})
                continue
            try:
                completed_step.compensate({"context": dict(base_context), "outputs": dict(outputs)}, result)
                events.append({"event": "COMPENSATION_COMPLETED", "step_id": completed_step.step_id})
            except Exception:
                compensation_errors.append(completed_step.step_id)
                events.append({"event": "COMPENSATION_FAILED", "step_id": completed_step.step_id})
        status = "PARTIAL_ROLLBACK" if compensation_errors else "ROLLED_BACK"
        events.append({"event": "SAGA_FINISHED", "status": status})
        return {
            "status": status,
            "failed_step": step.step_id,
            "compensation_errors": compensation_errors,
            "completed_steps": [item.step_id for item, _ in completed],
            "outputs": outputs,
            "events": events,
        }

    events.append({"event": "SAGA_FINISHED", "status": "COMPLETED"})
    return {"status": "COMPLETED", "completed_steps": [item.step_id for item, _ in completed],
            "outputs": outputs, "events": events}
