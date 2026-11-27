import unittest

from agent import run_review


class MultiAgentRequestReviewTests(unittest.TestCase):
    def test_supported_category_is_routed(self):
        result = run_review({"request": "Need access to the reporting workspace", "category": "access"})
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["output"]["queue"], "access")
        self.assertEqual([event["agent"] for event in result["trace"]], ["intake", "policy_review"])

    def test_unsupported_category_escalates(self):
        result = run_review({"request": "Need a legal interpretation", "category": "legal"})
        self.assertEqual(result["status"], "ESCALATE")
        self.assertEqual(result["reason"], "CATEGORY_REQUIRES_HUMAN_REVIEW")

    def test_empty_request_escalates(self):
        result = run_review({"request": "  ", "category": "support"})
        self.assertEqual(result["status"], "ESCALATE")
        self.assertEqual(result["reason"], "MISSING_REQUEST_TEXT")


if __name__ == "__main__":
    unittest.main()
