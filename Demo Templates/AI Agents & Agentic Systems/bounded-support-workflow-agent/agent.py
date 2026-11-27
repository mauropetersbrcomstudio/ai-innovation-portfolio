"""Reference agent combining orchestration and allowlisted tool execution."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Demo Templates" / "AI Skills & Tooling" / "agent-tool-gateway"))
sys.path.insert(0, str(ROOT / "Demo Templates" / "AI Skills & Tooling" / "agent-orchestration"))

from gateway import Session, ToolGateway, ToolSpec  # noqa: E402
from orchestrator import Orchestrator, Step, WorkflowState, state_to_dict  # noqa: E402


TICKET_SCHEMA = {
    "type": "object",
    "properties": {
        "subject": {"type": "string", "minLength": 5, "maxLength": 100},
        "priority": {"type": "string", "enum": ["normal", "urgent"]},
    },
    "required": ["subject", "priority"],
    "additionalProperties": False,
}


def build_agent() -> tuple[ToolGateway, Orchestrator]:
    gateway = ToolGateway()
    gateway.register(
        ToolSpec(
            name="create_support_ticket",
            description="Create a simulated support ticket",
            input_schema=TICKET_SCHEMA,
            allowed_roles=("support", "manager"),
            requires_approval=True,
            max_calls_per_session=1,
        ),
        lambda args: {"ticket_id": "DEMO-001", "subject": args["subject"], "priority": args["priority"]},
    )

    def assess_request(payload: dict[str, Any]) -> dict[str, str]:
        context = payload["context"]
        subject = str(context.get("subject", ""))
        priority = str(context.get("priority", "normal"))
        if not subject.strip():
            raise ValueError("A support subject is required")
        if priority not in {"normal", "urgent"}:
            raise ValueError("Priority must be normal or urgent")
        return {"subject": subject, "priority": priority, "decision": "READY_FOR_REVIEW"}

    def create_ticket(payload: dict[str, Any]) -> dict[str, Any]:
        assessed = payload["previous_outputs"]["assessment"]
        result = gateway.invoke(
            "create_support_ticket",
            {"subject": assessed["subject"], "priority": assessed["priority"]},
            payload["context"]["session"],
        )
        if result["status"] != "EXECUTED":
            raise RuntimeError(result["reason"])
        return result["output"]

    orchestrator = Orchestrator({
        "assess_request": assess_request,
        "create_ticket": create_ticket,
    })
    return gateway, orchestrator


def run_demo(*, subject: str, priority: str = "normal", role: str = "support",
             approval_granted: bool = False) -> dict[str, Any]:
    gateway, orchestrator = build_agent()
    session = Session(
        session_id="demo-session-001",
        role=role,
        approved_tools=("create_support_ticket",) if approval_granted else (),
    )
    context = {"subject": subject, "priority": priority, "session": session}
    steps = [
        Step("assessment", "assess_request"),
        Step("ticket_creation", "create_ticket", requires_approval=True, max_attempts=1),
    ]
    state = orchestrator.start("support-workflow-demo", steps, context)
    if state.status == "WAITING_FOR_APPROVAL" and approval_granted:
        orchestrator.approve_and_resume(state, steps, "ticket_creation")
    return {
        "workflow": state_to_dict(state),
        "tool_audit": gateway.audit_log,
        "notice": "Synthetic demonstration only. No real support system or external service is contacted.",
    }


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Run a bounded support workflow agent demo.")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--priority", choices=["normal", "urgent"], default="normal")
    parser.add_argument("--role", default="support")
    parser.add_argument("--approve", action="store_true", help="Simulate host-provided human approval.")
    args = parser.parse_args()
    print(json.dumps(run_demo(subject=args.subject, priority=args.priority, role=args.role,
                              approval_granted=args.approve), indent=2, default=str))
