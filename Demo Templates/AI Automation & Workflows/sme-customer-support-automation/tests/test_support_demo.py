import unittest
from support_demo import handle_request, classify

KB = {"order_status": {"draft_response": "Ask for order reference.", "source": "test FAQ"}}

class SupportDemoTests(unittest.TestCase):
    def test_single_category_gets_draft(self):
        result = handle_request({"request_id": "1", "message": "Where is my order?"}, KB)
        self.assertEqual(result["route"], "agent_draft_for_review")
        self.assertEqual(result["status"], "draft_ready")
        self.assertFalse(result["message_sent"])

    def test_sensitive_request_escalates(self):
        result = handle_request({"request_id": "2", "message": "I want a refund"}, KB)
        self.assertEqual(result["route"], "human_review")

    def test_unknown_request_escalates(self):
        result = handle_request({"request_id": "3", "message": "What are your opening hours?"}, KB)
        self.assertEqual(result["route"], "human_review")

    def test_missing_message_needs_information(self):
        result = handle_request({"request_id": "4", "message": "  "}, KB)
        self.assertEqual(result["status"], "needs_information")

    def test_multiple_categories_escalate(self):
        category, _ = classify("My order invoice has a problem")
        self.assertEqual(category, "human_review")

    def test_missing_knowledge_entry_escalates(self):
        result = handle_request({"request_id": "5", "message": "I cannot access my account"}, KB)
        self.assertEqual(result["route"], "human_review")

if __name__ == "__main__":
    unittest.main()