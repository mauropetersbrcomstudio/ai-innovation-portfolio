"""Deterministic, bounded workflow orchestrator with approval gates and event traces."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class Step:
    step_id: str
    handler_name: str
    requires_approval: bool = False
    max_attempts: int = 1


@dataclass
class WorkflowState:
    workflow_id: str
    status: str = "PENDING"
    current_step: str | None = None
    completed_steps: list[str] = field(default_factory=list)
    outputs: dict[str, Any] = field(default_factory=dict)
    attempts: dict[str, int] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)


class Orchestrator:
    TERMINAL = {"COMPLETED", "FAILED", "CANCELLED"}

    def __init__(self, handlers: dict[str, Callable[[dict[str, Any]], Any]], *, max_workflow_steps: int = 20):
        if max_workflow_steps < 1:
            raise ValueError("max_workflow_steps must be positive")
        self.handlers = dict(handlers)
        self.max_workflow_steps = max_workflow_steps

    def _event(self, state: WorkflowState, event: str, **details: Any) -> None:
        state.events.append({"event": event, "workflow_id": state.workflow_id, **details})

    def start(self, workflow_id: str, steps: list[Step], context: dict[str, Any] | None = None,
              approved_steps: tuple[str, ...] = ()) -> WorkflowState:
        state = WorkflowState(workflow_id=workflow_id, outputs={"context": dict(context or {})})
        self._event(state, "WORKFLOW_CREATED", step_count=len(steps))
        if not workflow_id:
            state.status = "FAILED"
            self._event(state, "WORKFLOW_REJECTED", reason="EMPTY_WORKFLOW_ID")
            return state
        if not steps:
            state.status = "FAILED"
            self._event(state, "WORKFLOW_REJECTED", reason="EMPTY_STEP_LIST")
            return state
        if len(steps) > self.max_workflow_steps:
            state.status = "FAILED"
            self._event(state, "WORKFLOW_REJECTED", reason="STEP_LIMIT_EXCEEDED")
            return state
        ids = [step.step_id for step in steps]
        if any(not item for item in ids) or len(ids) != len(set(ids)):
            state.status = "FAILED"
            self._event(state, "WORKFLOW_REJECTED", reason="INVALID_OR_DUPLICATE_STEP_ID")
            return state
        for step in steps:
            if step.handler_name not in self.handlers or step.max_attempts < 1:
                state.status = "FAILED"
                self._event(state, "WORKFLOW_REJECTED", reason="INVALID_STEP_CONFIGURATION", step_id=step.step_id)
                return state
        state.status = "RUNNING"
        self._event(state, "WORKFLOW_STARTED")
        self._advance(state, steps, set(approved_steps))
        return state

    def approve_and_resume(self, state: WorkflowState, steps: list[Step], step_id: str) -> WorkflowState:
        if state.status != "WAITING_FOR_APPROVAL" or state.current_step != step_id:
            self._event(state, "RESUME_REJECTED", reason="NO_MATCHING_APPROVAL_GATE", step_id=step_id)
            return state
        self._event(state, "APPROVAL_RECORDED", step_id=step_id)
        state.status = "RUNNING"
        self._advance(state, steps, {step_id})
        return state

    def cancel(self, state: WorkflowState) -> WorkflowState:
        if state.status in self.TERMINAL:
            self._event(state, "CANCEL_IGNORED", reason="ALREADY_TERMINAL")
            return state
        state.status = "CANCELLED"
        self._event(state, "WORKFLOW_CANCELLED", step_id=state.current_step)
        return state

    def _advance(self, state: WorkflowState, steps: list[Step], approved_steps: set[str]) -> None:
        for step in steps:
            if step.step_id in state.completed_steps:
                continue
            state.current_step = step.step_id
            if step.requires_approval and step.step_id not in approved_steps:
                state.status = "WAITING_FOR_APPROVAL"
                self._event(state, "APPROVAL_REQUIRED", step_id=step.step_id)
                return

            handler = self.handlers[step.handler_name]
            success = False
            for attempt in range(1, step.max_attempts + 1):
                state.attempts[step.step_id] = attempt
                self._event(state, "STEP_STARTED", step_id=step.step_id, attempt=attempt)
                try:
                    result = handler({
                        "workflow_id": state.workflow_id,
                        "step_id": step.step_id,
                        "context": dict(state.outputs["context"]),
                        "previous_outputs": dict(state.outputs),
                    })
                except Exception:
                    self._event(state, "STEP_FAILED", step_id=step.step_id, attempt=attempt, reason="HANDLER_ERROR")
                    continue
                state.outputs[step.step_id] = result
                state.completed_steps.append(step.step_id)
                self._event(state, "STEP_COMPLETED", step_id=step.step_id, attempt=attempt)
                success = True
                break
            if not success:
                state.status = "FAILED"
                self._event(state, "WORKFLOW_FAILED", step_id=step.step_id)
                return
        state.current_step = None
        state.status = "COMPLETED"
        self._event(state, "WORKFLOW_COMPLETED")


def state_to_dict(state: WorkflowState) -> dict[str, Any]:
    return {
        "workflow_id": state.workflow_id,
        "status": state.status,
        "current_step": state.current_step,
        "completed_steps": list(state.completed_steps),
        "outputs": state.outputs,
        "attempts": state.attempts,
        "events": state.events,
    }
