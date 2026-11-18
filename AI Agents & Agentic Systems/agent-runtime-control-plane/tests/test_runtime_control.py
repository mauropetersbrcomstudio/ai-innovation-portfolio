import sys
import tempfile
import unittest
from pathlib import Path

from runtime_control import AgentSpec, RuntimeControlPlane

security_path = Path(__file__).resolve().parents[2] / "AI Skills & Tooling" / "agent-security-governance"
sys.path.insert(0, str(security_path))
from security_governance import ApprovalEvidence, Principal, SecurityPolicyEngine


class RuntimeControlPlaneTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.effects = []
        self.runtime = RuntimeControlPlane(
            Path(self.tmp.name) / "runtime.db",
            {"create_task": lambda args: self.effects.append(args) or {"created": True}},
        )
        self.runtime.register(AgentSpec(
            "support-agent", "operator", ("create_task",), ("create_task",), max_invocations=1
        ))

    def activate(self):
        self.runtime.transition("support-agent", "ACTIVE")

    def test_lifecycle_and_execution_require_activation_and_approval(self):
        denied = self.runtime.invoke("support-agent", "create_task", {"id": "A"})
        self.assertEqual(denied["reason"], "AGENT_NOT_ACTIVE")
        self.activate()
        denied = self.runtime.invoke("support-agent", "create_task", {"id": "A"})
        self.assertEqual(denied["reason"], "HUMAN_APPROVAL_REQUIRED")
        self.assertEqual(self.effects, [])
        allowed = self.runtime.invoke("support-agent", "create_task", {"id": "A"},
                                       approved_tools=("create_task",))
        self.assertEqual(allowed["status"], "EXECUTED")
        self.assertEqual(len(self.effects), 1)


    def test_security_policy_is_enforced_before_handler_execution(self):
        policy = {"agents": {"support-agent": {
            "roles": ["support_operator"],
            "tools": {"create_task": {"risks": ["LOW"], "approval_required": False}}
        }}}
        security = SecurityPolicyEngine(policy)
        runtime = RuntimeControlPlane(
            Path(self.tmp.name) / "secure-runtime.db",
            {"create_task": lambda args: self.effects.append(args) or {"created": True}},
            authorization_check=security.authorize,
        )
        runtime.register(AgentSpec("support-agent", "operator", ("create_task",)))
        runtime.transition("support-agent", "ACTIVE")
        denied = runtime.invoke(
            "support-agent", "create_task", {"id": "DENIED"},
            principal=Principal("user-1", ("viewer",), True), risk="LOW"
        )
        self.assertEqual(denied["status"], "DENIED")
        self.assertEqual(denied["reason"], "ROLE_NOT_AUTHORIZED")
        self.assertEqual(self.effects, [])
        allowed = runtime.invoke(
            "support-agent", "create_task", {"id": "ALLOWED"},
            principal=Principal("user-1", ("support_operator",), True), risk="LOW"
        )
        self.assertEqual(allowed["status"], "EXECUTED")
        self.assertEqual(len(self.effects), 1)

    def test_secure_runtime_fails_closed_without_principal(self):
        security = SecurityPolicyEngine({"agents": {"support-agent": {
            "roles": ["support_operator"],
            "tools": {"create_task": {"risks": ["LOW"], "approval_required": False}}
        }}})
        runtime = RuntimeControlPlane(
            Path(self.tmp.name) / "secure-runtime-no-principal.db",
            {"create_task": lambda args: self.effects.append(args) or {"created": True}},
            authorization_check=security.authorize,
        )
        runtime.register(AgentSpec("support-agent", "operator", ("create_task",)))
        runtime.transition("support-agent", "ACTIVE")
        result = runtime.invoke("support-agent", "create_task", {"id": "A"}, risk="LOW")
        self.assertEqual(result["status"], "DENIED")
        self.assertEqual(result["reason"], "INVALID_PRINCIPAL")
        self.assertEqual(self.effects, [])

    def test_secure_runtime_requires_verified_approval_for_high_risk(self):
        policy = {"agents": {"support-agent": {
            "roles": ["support_operator"],
            "tools": {"create_task": {"risks": ["HIGH"], "approval_required": True}}
        }}}
        security = SecurityPolicyEngine(policy, lambda evidence: evidence.approval_id == "valid")
        runtime = RuntimeControlPlane(
            Path(self.tmp.name) / "secure-runtime-approval.db",
            {"create_task": lambda args: self.effects.append(args) or {"created": True}},
            authorization_check=security.authorize,
        )
        runtime.register(AgentSpec("support-agent", "operator", ("create_task",)))
        runtime.transition("support-agent", "ACTIVE")
        principal = Principal("user-1", ("support_operator",), True)
        missing = runtime.invoke(
            "support-agent", "create_task", {"id": "A"},
            principal=principal, risk="HIGH"
        )
        self.assertEqual(missing["reason"], "HUMAN_APPROVAL_REQUIRED")
        self.assertEqual(self.effects, [])
        evidence = ApprovalEvidence("valid", "supervisor-1", "support-agent",
                                    "create_task", "HIGH", "user-1")
        accepted = runtime.invoke(
            "support-agent", "create_task", {"id": "B"},
            principal=principal, risk="HIGH", approval=evidence
        )
        self.assertEqual(accepted["status"], "EXECUTED")
        self.assertEqual(len(self.effects), 1)

    def test_invocation_limit_blocks_second_call(self):
        self.activate()
        self.runtime.invoke("support-agent", "create_task", {"id": "A"},
                             approved_tools=("create_task",))
        result = self.runtime.invoke("support-agent", "create_task", {"id": "B"},
                                     approved_tools=("create_task",))
        self.assertEqual(result["reason"], "INVOCATION_LIMIT_REACHED")
        self.assertEqual(len(self.effects), 1)

    def test_health_block_and_automatic_escalation(self):
        self.activate()
        agent = self.runtime.heartbeat("support-agent", "UNHEALTHY")
        self.assertEqual(agent["health"], "UNHEALTHY")
        denied = self.runtime.invoke("support-agent", "create_task", {"id": "A"},
                                     approved_tools=("create_task",))
        self.assertEqual(denied["reason"], "AGENT_HEALTH_BLOCKED")
        report = self.runtime.audit_report("support-agent")
        self.assertEqual(report["open_escalations"], 1)

    def test_human_escalation_can_be_resolved_once(self):
        escalation = self.runtime.escalate("support-agent", "AMBIGUOUS_REQUEST", {"ticket": "T-1"})
        resolved = self.runtime.resolve_escalation(escalation["escalation_id"], "Manual review completed")
        self.assertEqual(resolved["status"], "RESOLVED")
        with self.assertRaises(ValueError):
            self.runtime.resolve_escalation(escalation["escalation_id"], "Second resolution")

    def test_retired_agent_cannot_be_reactivated(self):
        self.runtime.transition("support-agent", "RETIRED")
        with self.assertRaises(ValueError):
            self.runtime.transition("support-agent", "ACTIVE")

    def test_unknown_tool_and_wildcard_registration_are_rejected(self):
        with self.assertRaises(ValueError):
            self.runtime.register(AgentSpec("bad-agent", "operator", ("*",)))
        self.activate()
        result = self.runtime.invoke("support-agent", "delete_all", {})
        self.assertEqual(result["reason"], "TOOL_NOT_ALLOWLISTED")


if __name__ == "__main__":
    unittest.main()
