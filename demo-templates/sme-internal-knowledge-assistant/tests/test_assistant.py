import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from assistant import load_sources, retrieve, run


class KnowledgeAssistantTests(unittest.TestCase):
    def setUp(self):
        self.sources = [
            {"id": "HR-001", "title": "Vacation Procedure", "content": "Submit vacation requests to your manager 15 days ahead.", "allowed_roles": ["employee", "manager"]},
            {"id": "FIN-001", "title": "Expense Policy", "content": "Submit receipts to finance within 30 days.", "allowed_roles": ["finance"]},
        ]

    def test_retrieves_relevant_approved_source_with_citation(self):
        result = retrieve("How do I request vacation?", "employee", self.sources)
        self.assertEqual(result["status"], "RETRIEVED")
        self.assertEqual(result["results"][0]["source_id"], "HR-001")
        self.assertIn("[HR-001]", result["results"][0]["citation"])

    def test_role_filter_prevents_restricted_source_retrieval(self):
        result = retrieve("How do I submit expense receipts?", "employee", self.sources)
        self.assertEqual(result["status"], "ESCALATE")
        self.assertEqual(result["results"], [])
        self.assertEqual(result["reason"], "no_approved_source_match")

    def test_no_match_escalates(self):
        result = retrieve("How do I book international travel?", "employee", self.sources)
        self.assertEqual(result["status"], "ESCALATE")

    def test_missing_role_escalates(self):
        result = retrieve("vacation policy", "", self.sources)
        self.assertEqual(result["reason"], "missing_user_role")

    def test_duplicate_source_ids_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sources.json"
            path.write_text(json.dumps({"sources": [self.sources[0], self.sources[0]]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate source id"):
                load_sources(path)

    def test_run_writes_a_result_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_path = root / "sources.json"
            request_path = root / "request.json"
            output_path = root / "out" / "result.json"
            source_path.write_text(json.dumps({"sources": self.sources}), encoding="utf-8")
            request_path.write_text(json.dumps({"request_id": "R1", "user_role": "employee", "question": "vacation request"}), encoding="utf-8")
            result = run(source_path, request_path, output_path)
            saved = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(result["request_id"], "R1")
            self.assertEqual(saved["status"], "RETRIEVED")


if __name__ == "__main__":
    unittest.main()
