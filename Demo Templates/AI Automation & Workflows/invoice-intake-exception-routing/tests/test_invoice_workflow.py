import json
import tempfile
import unittest
from pathlib import Path

from invoice_workflow import process_invoices, run


SAMPLE = Path(__file__).resolve().parents[1] / "sample_invoices.json"


def invoice(**overrides):
    record = {
        "invoice_id": "INV-2001",
        "supplier_id": "SUP-020",
        "invoice_date": "2026-11-01",
        "due_date": "2026-11-30",
        "amount": "1000.00",
        "currency": "BRL",
        "purchase_order": "PO-2001",
    }
    record.update(overrides)
    return record


class InvoiceWorkflowTests(unittest.TestCase):
    def test_sample_records_cover_expected_routes(self):
        records = json.loads(SAMPLE.read_text(encoding="utf-8"))
        result = process_invoices(records)
        self.assertEqual(result["processed_count"], 6)
        self.assertEqual(result["status_counts"], {
            "AP_REVIEW": 1,
            "MANAGER_APPROVAL": 1,
            "NEEDS_INFORMATION": 1,
            "DUPLICATE_REVIEW": 2,
            "POLICY_HOLD": 1,
        })

    def test_duplicate_pair_is_flagged_on_both_rows_case_insensitively(self):
        records = [
            invoice(invoice_id="INV-X", supplier_id="SUP-X"),
            invoice(invoice_id="inv-x", supplier_id="sup-x"),
        ]
        result = process_invoices(records)
        self.assertEqual(
            [item["status"] for item in result["results"]],
            ["DUPLICATE_REVIEW", "DUPLICATE_REVIEW"],
        )

    def test_missing_purchase_order_is_routed_for_information(self):
        result = process_invoices([invoice(purchase_order="")])
        self.assertEqual(result["results"][0]["status"], "NEEDS_INFORMATION")
        self.assertIn("purchase_order", result["results"][0]["missing_fields"])

    def test_amount_above_threshold_requires_manager_review(self):
        result = process_invoices([invoice(amount="5000.01")])
        self.assertEqual(result["results"][0]["status"], "MANAGER_APPROVAL")

    def test_amount_equal_to_threshold_stays_in_accounts_payable_review(self):
        result = process_invoices([invoice(amount="5000.00")])
        self.assertEqual(result["results"][0]["status"], "AP_REVIEW")

    def test_invalid_date_amount_and_currency_are_policy_holds(self):
        records = [
            invoice(invoice_date="not-a-date"),
            invoice(invoice_id="INV-2002", amount="-10.00"),
            invoice(invoice_id="INV-2003", currency="XYZ"),
        ]
        result = process_invoices(records)
        self.assertEqual(
            [item["status"] for item in result["results"]],
            ["POLICY_HOLD", "POLICY_HOLD", "POLICY_HOLD"],
        )

    def test_missing_amount_and_invalid_amount_take_different_routes(self):
        records = [
            invoice(amount=""),
            invoice(invoice_id="INV-2004", amount="-10.00"),
        ]
        result = process_invoices(records)
        self.assertEqual(
            [item["status"] for item in result["results"]],
            ["NEEDS_INFORMATION", "POLICY_HOLD"],
        )

    def test_due_date_before_invoice_date_is_policy_hold(self):
        result = process_invoices([invoice(due_date="2026-10-31")])
        self.assertEqual(result["results"][0]["reasons"], ["DUE_DATE_BEFORE_INVOICE_DATE"])

    def test_non_object_record_is_held_without_crashing_batch(self):
        result = process_invoices([invoice(), "not-an-object", invoice(invoice_id="INV-2002")])
        self.assertEqual(result["processed_count"], 3)
        self.assertEqual(result["results"][1]["status"], "POLICY_HOLD")
        self.assertEqual(result["status_counts"]["AP_REVIEW"], 2)

    def test_invalid_input_and_threshold_are_rejected(self):
        with self.assertRaises(ValueError):
            process_invoices({"invoice_id": "INV-1"})
        with self.assertRaises(ValueError):
            process_invoices([invoice()], approval_threshold="0")

    def test_run_writes_a_reproducible_json_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "nested" / "review.json"
            result = run(SAMPLE, output)
            saved = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(saved, result)
            self.assertEqual(saved["processed_count"], 6)


if __name__ == "__main__":
    unittest.main()
