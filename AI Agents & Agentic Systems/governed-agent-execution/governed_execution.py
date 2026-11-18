"""Governed execution demo combining policy validation, orchestration, and a tool gateway."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "AI Skills & Tooling"
for component in ("agent-orchestration", "agent-policy-validator", "agent-tool-gateway"):
    sys.path.insert(0, str(SKILLS / component))

from orchestrator import Orchestrator, Step, state_to_dict  # noqa: E402
from validate_policy import validate_policy  # noqa: E402
from gateway import Session, ToolGateway, ToolSpec  # noqa: E402


def run_governed_execution(
    request: str,
    *,
    role: str = "operator",
    approved: bool = False,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a policy, then execute one allowlisted, approval-gated simulated action."""
    manifest = policy or {
        "agents": [{
            "name": "support-review-agent",
            "risk": "MEDIUM",
            "allowed_tools": ["create_review_task"],
            "approval_required_for": ["create_review_task"],
            "max_steps": 3,
        }]
    }
    policy_result = validate_policy(manifest)
    if not policy_result["valid"]:
        return {
            "status": "REJECTED",
            "reason": "INVALID_POLICY",
            "policy": policy_result,
            "tool_audit": [],
            "side_effects": [],
        }

    side_effects: list[dict[str, str]] = []
    gateway = ToolGateway()
    gateway.register(
        ToolSpec(
            name="create_review_task",
            description="Create a local simulated review task",
            input_schema={
                "type": "object",
                "properties": {"request": {"type": "string", "minLength": 1, "maxLength": 500}},
                "required": ["request"],
                "additionalProperties": False,
            },
            allowed_roles=("operator", "reviewer"),
            requires_approval=True,
            max_calls_per_session=1,
        ),
        lambda args: side_effects.append({"queue": "human_review", "request": args["request"]})
        or {"queued": True, "external_action": False},
    )
    session = Session(
        session_id="demo-session",
        role=role,
        approved_tools=("create_review_task",) if approved else (),
    )

    def create_review_task(payload: dict[str, Any]) -> dict[str, Any]:
        result = gateway.invoke(
            "create_review_task",
            {"request": payload["context"]["request"]},
            session,
        )
        if result["status"] != "EXECUTED":
            raise PermissionError(result["reason"])
        return result

    orchestrator = Orchestrator({"create_review_task": create_review_task}, max_workflow_steps=3)
    state = orchestrator.start(
        "governed-execution-demo",
        [Step("review-task", "create_review_task", max_attempts=1)],
        {"request": request},
    )
    return {
        "status": state.status,
        "workflow": state_to_dict(state),
        "policy": policy_result,
        "tool_audit": gateway.audit_log,
        "side_effects": side_effects,
        "notice": "The review task is simulated in memory; no external system is contacted.",
    }
