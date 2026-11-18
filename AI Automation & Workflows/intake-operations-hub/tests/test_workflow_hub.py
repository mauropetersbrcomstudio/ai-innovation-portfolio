import tempfile
import unittest
from pathlib import Path
from workflow_hub import run_intake_workflow

class IntakeOperationsHubTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.database, self.events = root / "workflows.sqlite", root / "events.jsonl"

    def tearDown(self):
        self.temp.cleanup()

    def run_case(self, workflow_id, leads, invoices, threshold="5000.00"):
        return run_intake_workflow(workflow_id, leads, invoices, self.database,
                                   self.events, threshold)

    def test_normal_records_complete_without_review_queue(self):
        result = self.run_case("normal",
            [{"name":"Ada","email":"ada@acme.example","company":"Acme","service":"Analytics","source":"Referral"}],
            [{"invoice_id":"INV-1","supplier_id":"SUP-1","invoice_date":"2026-01-01",
              "due_date":"2026-02-01","amount":"120.00","currency":"BRL","purchase_order":"PO-1"}])
        state = result["workflow"]["state"]
        self.assertEqual(state["status"], "COMPLETED")
        self.assertEqual(state["outputs"]["prepare_human_review"]["status"], "NO_REVIEW_REQUIRED")

    def test_incomplete_and_duplicate_records_enter_review_queue(self):
        result = self.run_case("exceptions",
            [{"name":"Ada","email":"ada@acme.example"},
             {"name":"Ada Duplicate","email":"ada@acme.example"}],
            [{"invoice_id":"INV-2","supplier_id":"SUP-2","invoice_date":"2026-01-01",
              "due_date":"2026-02-01","amount":"6000.00","currency":"BRL","purchase_order":""},
             {"invoice_id":"INV-2","supplier_id":"SUP-2","invoice_date":"2026-01-01",
              "due_date":"2026-02-01","amount":"6000.00","currency":"BRL","purchase_order":"PO-2"}])
        review = result["workflow"]["state"]["outputs"]["prepare_human_review"]
        self.assertEqual(review["status"], "PENDING_HUMAN_REVIEW")
        self.assertGreaterEqual(review["lead_exception_count"], 1)
        self.assertGreaterEqual(review["invoice_review_count"], 1)

    def test_completed_workflow_is_not_repeated(self):
        args = ("repeat", [], [], "5000.00")
        first, second = self.run_case(*args), self.run_case(*args)
        self.assertEqual(first["workflow"]["state"]["completed_steps"],
                         second["workflow"]["state"]["completed_steps"])
        self.assertTrue(second["resumed"])
        self.assertEqual(second["workflow"]["status"], "COMPLETED")

    def test_changed_input_conflicts_with_persisted_workflow(self):
        self.run_case("conflict", [], [], "5000.00")
        with self.assertRaises(ValueError):
            self.run_case("conflict", [{"name":"Grace","email":"grace@example.org"}], [], "5000.00")

    def test_invalid_threshold_is_recorded_as_failed_workflow(self):
        result = self.run_case("failure", [], [], "0")
        self.assertEqual(result["workflow"]["status"], "FAILED")
        self.assertIn("STEP_FAILED", [event["event_type"] for event in result["events"]])

if __name__ == "__main__":
    unittest.main()
