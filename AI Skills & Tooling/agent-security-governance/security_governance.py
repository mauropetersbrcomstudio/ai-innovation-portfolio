"""Deterministic, deny-by-default authorization contracts for agent tools.

Authentication and approval verification are trusted-host responsibilities. This
module validates the host-supplied principal and delegates approval evidence
verification to an injected verifier; it does not authenticate users itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


VALID_RISKS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


@dataclass(frozen=True)
class Principal:
    subject_id: str
    roles: tuple[str, ...]
    authenticated: bool


@dataclass(frozen=True)
class ApprovalEvidence:
    approval_id: str
    approver_id: str
    agent_id: str
    tool: str
    risk: str
    subject_id: str


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str
    subject_id: str
    agent_id: str
    tool: str
    risk: str


class SecurityPolicyError(ValueError):
    """Raised when a policy manifest is structurally invalid."""


class SecurityPolicyEngine:
    """Evaluate explicit agent/tool/risk grants and separately verify approvals."""

    def __init__(
        self,
        policy: dict[str, Any],
        approval_verifier: Callable[[ApprovalEvidence], bool] | None = None,
    ):
        self.policy = self._validate_policy(policy)
        self.approval_verifier = approval_verifier
        self.audit_events: list[dict[str, Any]] = []

    @staticmethod
    def _validate_policy(policy: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(policy, dict) or set(policy) != {"agents"}:
            raise SecurityPolicyError("policy must contain only an agents mapping")
        agents = policy["agents"]
        if not isinstance(agents, dict) or not agents:
            raise SecurityPolicyError("agents must be a non-empty mapping")
        normalized: dict[str, Any] = {}
        for agent_id, spec in agents.items():
            if not isinstance(agent_id, str) or not agent_id.strip():
                raise SecurityPolicyError("agent identifiers must be non-empty strings")
            if not isinstance(spec, dict) or set(spec) != {"roles", "tools"}:
                raise SecurityPolicyError(f"{agent_id}: expected roles and tools only")
            roles, tools = spec["roles"], spec["tools"]
            if not isinstance(roles, list) or not roles or any(
                not isinstance(role, str) or not role.strip() or role == "*" for role in roles
            ) or len(set(roles)) != len(roles):
                raise SecurityPolicyError(f"{agent_id}: roles must be unique explicit strings")
            if not isinstance(tools, dict) or not tools:
                raise SecurityPolicyError(f"{agent_id}: tools must be a non-empty mapping")
            clean_tools = {}
            for tool, grant in tools.items():
                if not isinstance(tool, str) or not tool.strip() or tool == "*":
                    raise SecurityPolicyError(f"{agent_id}: tool names must be explicit")
                if not isinstance(grant, dict) or set(grant) != {"risks", "approval_required"}:
                    raise SecurityPolicyError(f"{agent_id}/{tool}: invalid grant shape")
                risks = grant["risks"]
                required = grant["approval_required"]
                if not isinstance(risks, list) or not risks or any(r not in VALID_RISKS for r in risks):
                    raise SecurityPolicyError(f"{agent_id}/{tool}: risks must be valid and non-empty")
                if len(set(risks)) != len(risks):
                    raise SecurityPolicyError(f"{agent_id}/{tool}: duplicate risk")
                if not isinstance(required, bool):
                    raise SecurityPolicyError(f"{agent_id}/{tool}: approval_required must be boolean")
                clean_tools[tool] = {"risks": tuple(risks), "approval_required": required}
            normalized[agent_id] = {"roles": tuple(roles), "tools": clean_tools}
        return {"agents": normalized}

    def authorize(
        self,
        principal: Principal,
        agent_id: str,
        tool: str,
        risk: str,
        approval: ApprovalEvidence | None = None,
    ) -> Decision:
        subject = principal.subject_id if isinstance(principal, Principal) else ""
        reason = self._deny_reason(principal, agent_id, tool, risk, approval)
        decision = Decision(
            allowed=reason == "AUTHORIZED",
            reason=reason,
            subject_id=subject,
            agent_id=agent_id if isinstance(agent_id, str) else "",
            tool=tool if isinstance(tool, str) else "",
            risk=risk if isinstance(risk, str) else "",
        )
        self.audit_events.append({
            "event": "AUTHORIZATION_DECISION",
            "allowed": decision.allowed,
            "reason": decision.reason,
            "subject_id": decision.subject_id,
            "agent_id": decision.agent_id,
            "tool": decision.tool,
            "risk": decision.risk,
        })
        return decision

    def _deny_reason(
        self,
        principal: Principal,
        agent_id: str,
        tool: str,
        risk: str,
        approval: ApprovalEvidence | None,
    ) -> str:
        if not isinstance(principal, Principal):
            return "INVALID_PRINCIPAL"
        if not isinstance(principal.subject_id, str) or not principal.subject_id.strip():
            return "INVALID_PRINCIPAL"
        if not isinstance(principal.authenticated, bool) or not principal.authenticated:
            return "AUTHENTICATION_REQUIRED"
        if not isinstance(principal.roles, tuple) or not principal.roles or any(
            not isinstance(role, str) or not role.strip() for role in principal.roles
        ):
            return "INVALID_PRINCIPAL_ROLES"
        if not isinstance(agent_id, str) or not isinstance(tool, str):
            return "INVALID_REQUEST"
        if risk not in VALID_RISKS:
            return "INVALID_RISK"
        agent = self.policy["agents"].get(agent_id)
        if agent is None:
            return "AGENT_NOT_IN_POLICY"
        if not set(principal.roles).intersection(agent["roles"]):
            return "ROLE_NOT_AUTHORIZED"
        grant = agent["tools"].get(tool)
        if grant is None:
            return "TOOL_NOT_AUTHORIZED"
        if risk not in grant["risks"]:
            return "RISK_NOT_AUTHORIZED"
        if grant["approval_required"]:
            if approval is None:
                return "HUMAN_APPROVAL_REQUIRED"
            if not isinstance(approval, ApprovalEvidence):
                return "INVALID_APPROVAL_EVIDENCE"
            if (
                approval.agent_id != agent_id
                or approval.tool != tool
                or approval.risk != risk
                or approval.subject_id != principal.subject_id
                or not approval.approval_id.strip()
                or not approval.approver_id.strip()
            ):
                return "APPROVAL_SCOPE_MISMATCH"
            if self.approval_verifier is None:
                return "APPROVAL_VERIFIER_UNAVAILABLE"
            try:
                verified = self.approval_verifier(approval)
            except Exception:
                return "APPROVAL_VERIFICATION_FAILED"
            if verified is not True:
                return "APPROVAL_NOT_VERIFIED"
        return "AUTHORIZED"
