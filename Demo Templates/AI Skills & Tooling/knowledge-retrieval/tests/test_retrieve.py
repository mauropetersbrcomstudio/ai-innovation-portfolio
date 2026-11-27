import unittest

from retrieve import retrieve, load_sources
from pathlib import Path


SOURCES = [
    {"id": "A", "title": "Leave policy", "text": "Submit leave requests to your manager.", "tags": ["vacation"], "allowed_roles": ["employee", "manager"]},
    {"id": "B", "title": "Finance reimbursement", "text": "Submit receipts for reimbursement.", "tags": ["expenses"], "allowed_roles": ["finance"]},
    {"id": "C", "title": "Public handbook", "text": "The office opens at nine.", "tags": []},
]


class RetrievalTests(unittest.TestCase):
    def test_relevant_source_retrieved(self):
        result = retrieve("leave request", "employee", SOURCES)
        self.assertEqual(result["status"], "MATCHES_FOUND")
        self.assertEqual(result["results"][0]["source_id"], "A")

    def test_restricted_source_is_not_returned(self):
        result = retrieve("reimbursement receipts", "employee", SOURCES)
        self.assertNotIn("B", [item["source_id"] for item in result["results"]])

    def test_no_match_escalates(self):
        result = retrieve("international relocation", "employee", SOURCES)
        self.assertEqual(result["status"], "ESCALATE_NO_QUALIFYING_SOURCE")
        self.assertEqual(result["results"], [])

    def test_threshold_can_remove_weak_match(self):
        result = retrieve("leave", "employee", SOURCES, min_score=99)
        self.assertEqual(result["returned_count"], 0)

    def test_limit_is_applied(self):
        result = retrieve("office leave", "employee", SOURCES, limit=1)
        self.assertLessEqual(result["returned_count"], 1)

    def test_invalid_query_rejected(self):
        with self.assertRaises(ValueError):
            retrieve("   ", "employee", SOURCES)

    def test_duplicate_source_ids_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate source id"):
            load_sources(Path(__file__).parents[1] / "examples" / "invalid-duplicates.json")


if __name__ == "__main__":
    unittest.main()
