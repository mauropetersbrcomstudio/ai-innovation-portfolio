import unittest

from agent import handle_request


class OperationsAssistantTests(unittest.TestCase):
    def test_classifies_billing_request(self):
        result = handle_request("Please check my invoice payment")
        self.assertEqual(result.status, "proposal_only")
        self.assertEqual(result.proposed_action, "billing_status")

    def test_classifies_order_request(self):
        result = handle_request("Where is my order delivery?")
        self.assertEqual(result.proposed_action, "order_status")

    def test_ambiguous_request_escalates(self):
        result = handle_request("I need help with my invoice")
        self.assertEqual(result.status, "escalated")
        self.assertIsNone(result.proposed_action)

    def test_unknown_action_is_rejected(self):
        result = handle_request("Check my invoice", "delete_customer")
        self.assertEqual(result.status, "rejected")
        self.assertIn("rejected_unknown_action", result.trace)

    def test_empty_request_escalates(self):
        result = handle_request("   ")
        self.assertEqual(result.status, "escalated")

    def test_no_external_side_effects(self):
        result = handle_request("Check my invoice")
        self.assertIn("simulated_no_side_effects", result.trace)
        self.assertEqual(result.status, "proposal_only")


if __name__ == "__main__":
    unittest.main()
