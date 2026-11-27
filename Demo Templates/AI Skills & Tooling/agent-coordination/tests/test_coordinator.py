import unittest

from coordinator import AgentCoordinator, AgentSpec


class AgentCoordinatorTests(unittest.TestCase):
    def test_registered_handoff_completes(self):
        agents = {
            "intake": (AgentSpec("intake", ("review",)), lambda p: {"status": "HANDOFF", "next_agent": "review", "payload": p}),
            "review": (AgentSpec("review", ()), lambda p: {"status": "COMPLETED", "answer": "reviewed"}),
        }
        result = AgentCoordinator(agents).run("intake", {"request": "sample"})
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual([x["agent"] for x in result["trace"]], ["intake", "review"])

    def test_unapproved_handoff_blocked(self):
        agents = {
            "intake": (AgentSpec("intake", ()), lambda p: {"status": "HANDOFF", "next_agent": "review", "payload": {}}),
            "review": (AgentSpec("review", ()), lambda p: {"status": "COMPLETED"}),
        }
        result = AgentCoordinator(agents).run("intake", {})
        self.assertEqual(result["reason"], "HANDOFF_NOT_ALLOWED")

    def test_handoff_budget_enforced(self):
        agents = {
            "a": (AgentSpec("a", ("b",)), lambda p: {"status": "HANDOFF", "next_agent": "b", "payload": {}}),
            "b": (AgentSpec("b", ("a",)), lambda p: {"status": "HANDOFF", "next_agent": "a", "payload": {}}),
        }
        result = AgentCoordinator(agents, max_handoffs=1).run("a", {})
        self.assertEqual(result["reason"], "HANDOFF_LIMIT_REACHED")

    def test_agent_invocation_limit_enforced(self):
        agents = {
            "a": (AgentSpec("a", ("a",), max_invocations=1), lambda p: {"status": "HANDOFF", "next_agent": "a", "payload": {}}),
        }
        result = AgentCoordinator(agents, max_handoffs=3).run("a", {})
        self.assertEqual(result["reason"], "AGENT_INVOCATION_LIMIT")

    def test_unknown_agent_blocked(self):
        result = AgentCoordinator({}).run("missing", {})
        self.assertEqual(result["reason"], "AGENT_NOT_REGISTERED")

    def test_agent_can_escalate(self):
        agents = {"triage": (AgentSpec("triage", ()), lambda p: {"status": "ESCALATE", "reason": "NEEDS_HUMAN"})}
        result = AgentCoordinator(agents).run("triage", {})
        self.assertEqual(result["status"], "ESCALATE")

    def test_handler_error_fails_closed(self):
        agents = {"broken": (AgentSpec("broken", ()), lambda p: 1 / 0)}
        result = AgentCoordinator(agents).run("broken", {})
        self.assertEqual(result["reason"], "AGENT_HANDLER_ERROR")


if __name__ == "__main__":
    unittest.main()
