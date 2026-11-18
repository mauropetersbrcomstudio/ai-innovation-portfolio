import tempfile
import unittest
from pathlib import Path

from runtime_control import AgentSpec, RuntimeControlPlane


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
