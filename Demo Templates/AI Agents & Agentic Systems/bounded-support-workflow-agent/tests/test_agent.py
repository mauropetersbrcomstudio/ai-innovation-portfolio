import unittest

from agent import run_demo


class BoundedSupportWorkflowAgentTests(unittest.TestCase):
    def test_pauses_for_approval_without_creating_ticket(self):
        result = run_demo(subject="Cannot access account")
        self.assertEqual(result["workflow"]["status"], "WAITING_FOR_APPROVAL")
        self.assertEqual(result["workflow"]["completed_steps"], ["assessment"])
        self.assertEqual(result["tool_audit"], [])

    def test_approved_request_completes(self):
        result = run_demo(subject="Cannot access account", priority="urgent", approval_granted=True)
        self.assertEqual(result["workflow"]["status"], "COMPLETED")
        self.assertEqual(result["workflow"]["outputs"]["ticket_creation"]["ticket_id"], "DEMO-001")
        self.assertEqual(result["tool_audit"][0]["status"], "EXECUTED")

    def test_unauthorized_role_fails_closed(self):
        result = run_demo(subject="Cannot access account", role="sales", approval_granted=True)
        self.assertEqual(result["workflow"]["status"], "FAILED")
        self.assertEqual(result["tool_audit"][0]["reason"], "ROLE_NOT_ALLOWED")

    def test_invalid_request_fails_before_approval(self):
        result = run_demo(subject=" ")
        self.assertEqual(result["workflow"]["status"], "FAILED")
        self.assertEqual(result["workflow"]["completed_steps"], [])
        self.assertEqual(result["tool_audit"], [])


if __name__ == "__main__":
    unittest.main()
