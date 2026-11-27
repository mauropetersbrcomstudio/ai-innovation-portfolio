"""Trusted-host adapter joining deny-by-default policy and allowlisted dispatch.

This module does not authenticate users or establish approval authenticity. A trusted
host must construct Principal values after authentication and inject an authoritative
approval verifier into SecurityPolicyEngine.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SKILLS = ROOT / "Demo Templates" / "AI Skills & Tooling"
for component in ("agent-security-governance", "agent-tool-gateway"):
    component_path = str(SKILLS / component)
    if component_path not in sys.path:
        sys.path.insert(0, component_path)

from security_governance import (  # noqa: E402
    ApprovalEvidence,
    Decision,
    Principal,
    SecurityPolicyEngine,
)
from gateway import Session, ToolGateway, ToolSpec  # noqa: E402


@dataclass
class _SessionBinding:
    subject_id: str
    role: str
    session: Session


class GovernedToolHost:
    """Authorize first, then derive a gateway session from trusted host context.

    Session bindings and consumed approval identifiers are in-memory and local to
    this host instance. This is a synchronous single-process demonstration.
    """

    def __init__(self, security: SecurityPolicyEngine, gateway: ToolGateway):
        self.security = security
        self.gateway = gateway
        self._sessions: dict[str, _SessionBinding] = {}
        self._used_approval_ids: set[str] = set()
        self.audit_events: list[dict[str, Any]] = []

    @staticmethod
    def _decision_payload(decision: Decision) -> dict[str, Any]:
        return {
            "allowed": decision.allowed,
            "reason": decision.reason,
            "subject_id": decision.subject_id,
            "agent_id": decision.agent_id,
            "tool": decision.tool,
            "risk": decision.risk,
        }

    def invoke(
        self,
        *,
        session_id: str,
        principal: Principal,
        agent_id: str,
        tool_name: str,
        risk: str,
        arguments: Any,
        approval: ApprovalEvidence | None = None,
    ) -> dict[str, Any]:
        """Run policy authorization before any allowlisted handler can be reached."""
        safe_session_id = session_id if isinstance(session_id, str) else ""
        safe_agent_id = agent_id if isinstance(agent_id, str) else ""
        safe_tool = tool_name if isinstance(tool_name, str) else ""
        safe_risk = risk if isinstance(risk, str) else ""

        def finish(
            status: str,
            reason: str,
            decision: Decision | None = None,
            dispatch: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            self.audit_events.append({
                "event": "GOVERNED_TOOL_INVOCATION",
                "session_id": safe_session_id,
                "agent_id": safe_agent_id,
                "tool": safe_tool,
                "risk": safe_risk,
                "authorization_reason": decision.reason if decision else "NOT_EVALUATED",
                "status": status,
                "reason": reason,
                "dispatch_status": dispatch.get("status") if dispatch else "NOT_ATTEMPTED",
            })
            return {
                "status": status,
                "reason": reason,
                "authorization": self._decision_payload(decision) if decision else None,
                "dispatch": dispatch,
            }

        if not isinstance(session_id, str) or not session_id.strip() or len(session_id) > 128:
            return finish("DENIED", "INVALID_SESSION_ID")

        decision = self.security.authorize(
            principal, agent_id, tool_name, risk, approval
        )
        if not decision.allowed:
            return finish("DENIED", decision.reason, decision)

        agent_policy = self.security.policy["agents"].get(agent_id)
        grant = agent_policy["tools"].get(tool_name) if agent_policy else None
        spec = self.gateway.get_tool_spec(tool_name)
        if spec is None:
            return finish("DENIED", "TOOL_NOT_REGISTERED", decision)
        if grant is None:
            return finish("DENIED", "POLICY_GRANT_NOT_FOUND", decision)
        if spec.requires_approval != grant["approval_required"]:
            return finish("DENIED", "APPROVAL_CONFIGURATION_MISMATCH", decision)

        if grant["approval_required"]:
            # A successful policy decision implies a correctly scoped evidence object
            # passed the injected verifier. Consume its opaque ID after handler entry,
            # including a handler error, to avoid same-process replay.
            if not isinstance(approval, ApprovalEvidence):
                return finish("DENIED", "INVALID_APPROVAL_EVIDENCE", decision)
            if approval.approval_id in self._used_approval_ids:
                return finish("DENIED", "APPROVAL_ALREADY_USED", decision)

        policy_roles = agent_policy["roles"]
        principal_roles = principal.roles
        candidate_roles = [
            role for role in policy_roles
            if role in principal_roles and (not spec.allowed_roles or role in spec.allowed_roles)
        ]
        if not candidate_roles:
            return finish("DENIED", "GATEWAY_ROLE_MISMATCH", decision)
        selected_role = candidate_roles[0]

        binding = self._sessions.get(session_id)
        if binding is not None:
            if binding.subject_id != principal.subject_id:
                return finish("DENIED", "SESSION_SUBJECT_MISMATCH", decision)
            if binding.role != selected_role:
                return finish("DENIED", "SESSION_ROLE_MISMATCH", decision)
            session = binding.session
        else:
            session = Session(session_id=session_id, role=selected_role)
            self._sessions[session_id] = _SessionBinding(
                subject_id=principal.subject_id,
                role=selected_role,
                session=session,
            )

        if spec.requires_approval:
            # Only this adapter adds the gateway marker, and only after the policy
            # engine has allowed the separately verified approval evidence.
            session.approved_tools = tuple(sorted(set(session.approved_tools) | {tool_name}))

        dispatch = self.gateway.invoke(tool_name, arguments, session)
        dispatch_status = dispatch.get("status")
        if grant["approval_required"] and dispatch_status in {"EXECUTED", "ERROR"}:
            self._used_approval_ids.add(approval.approval_id)

        if dispatch_status == "EXECUTED":
            return finish("EXECUTED", "DISPATCHED", decision, dispatch)
        if dispatch_status == "ERROR":
            return finish("ERROR", "HANDLER_FAILED", decision, dispatch)
        if dispatch_status == "DENIED":
            return finish("DENIED", dispatch.get("reason", "DISPATCH_DENIED"), decision, dispatch)
        return finish("ERROR", "UNEXPECTED_GATEWAY_RESPONSE", decision, dispatch)


def run_demo(approval_present: bool = False) -> dict[str, Any]:
    """Run the adapter with synthetic identity and approval fixtures only."""
    if not isinstance(approval_present, bool):
        raise ValueError("approval_present must be boolean")

    policy = {
        "agents": {
            "support-review-agent": {
                "roles": ["support_operator", "supervisor"],
                "tools": {
                    "create_review_task": {
                        "risks": ["MEDIUM"],
                        "approval_required": True,
                    }
                },
            }
        }
    }

    def verify_demo_approval(evidence: ApprovalEvidence) -> bool:
        return (
            evidence.approval_id == "demo-approval-001"
            and evidence.approver_id == "demo-supervisor"
        )

    security = SecurityPolicyEngine(policy, approval_verifier=verify_demo_approval)
    gateway = ToolGateway()
    side_effects: list[dict[str, Any]] = []
    gateway.register(
        ToolSpec(
            name="create_review_task",
            description="Create a synthetic local review task",
            input_schema={
                "type": "object",
                "properties": {
                    "request": {"type": "string", "minLength": 1, "maxLength": 500}
                },
                "required": ["request"],
                "additionalProperties": False,
            },
            allowed_roles=("support_operator", "supervisor"),
            requires_approval=True,
            max_calls_per_session=1,
        ),
        lambda args: side_effects.append({
            "queue": "human_review",
            "request": args["request"],
        }) or {"queued": True, "external_action": False},
    )
    host = GovernedToolHost(security, gateway)
    evidence = ApprovalEvidence(
        approval_id="demo-approval-001",
        approver_id="demo-supervisor",
        agent_id="support-review-agent",
        tool="create_review_task",
        risk="MEDIUM",
        subject_id="demo-operator",
    ) if approval_present else None

    invocation = host.invoke(
        session_id="demo-session-001",
        principal=Principal("demo-operator", ("support_operator",), True),
        agent_id="support-review-agent",
        tool_name="create_review_task",
        risk="MEDIUM",
        arguments={"request": "Review synthetic support request"},
        approval=evidence,
    )
    return {
        "invocation": invocation,
        "side_effects": side_effects,
        "host_audit": host.audit_events,
        "authorization_audit": security.audit_events,
        "gateway_audit": gateway.audit_log,
        "notice": (
            "Synthetic in-memory demonstration only. Identity and approval fixtures "
            "are not production authentication or cryptographic approval."
        ),
    }
