import unittest

from governed_execution import run_governed_execution


class GovernedExecutionTests(unittest.TestCase):
    def test_invalid_policy_is_rejected_before_workflow_or_tool_execution(self):
        result = run_governed_execution(
            "Review this request",
            approved=True,
            policy={"agents": [{"name": "unsafe", "risk": "HIGH", "allowed_tools": ["*"],
                                "approval_required_for": [], "max_steps": 2}]},
        )
        self.assertEqual(result["status"], "REJECTED")
        self.assertEqual(result["reason"], "INVALID_POLICY")
        self.assertEqual(result["tool_audit"], [])
        self.assertEqual(result["side_effects"], [])

    def test_missing_approval_fails_closed_without_side_effect(self):
        result = run_governed_execution("Review this request")
        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(result["tool_audit"][0]["reason"], "HUMAN_APPROVAL_REQUIRED")
        self.assertEqual(result["side_effects"], [])

    def test_disallowed_role_fails_closed_without_side_effect(self):
        result = run_governed_execution("Review this request", role="viewer", approved=True)
        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(result["tool_audit"][0]["reason"], "ROLE_NOT_ALLOWED")
        self.assertEqual(result["side_effects"], [])

    def test_approved_authorized_operator_executes_only_simulated_action(self):
        result = run_governed_execution("Review this request", approved=True)
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["tool_audit"][0]["status"], "EXECUTED")
        self.assertEqual(len(result["side_effects"]), 1)
        self.assertFalse(result["side_effects"][0].get("external_action", False))


if __name__ == "__main__":
    unittest.main()
