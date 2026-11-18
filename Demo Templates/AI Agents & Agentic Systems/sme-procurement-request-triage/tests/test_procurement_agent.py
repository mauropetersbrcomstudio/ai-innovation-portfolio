import unittest

from procurement_agent import assess_request, build_report, validate_policy

POLICY = {
    "currency": "BRL",
    "manager_review_limit": 1500,
    "finance_review_limit": 5000,
    "allowed_categories": ["office_supplies", "software", "equipment", "services"],
}


def request(**changes):
    item = {
        "request_id": "PR-001",
        "requester": "Sample requester",
        "item": "Office chairs",
        "category": "equipment",
        "amount": 1200,
        "currency": "BRL",
        "supplier": "Example Supplier",
        "supplier_status": "approved",
        "urgency": "standard",
    }
    item.update(changes)
    return item


class ProcurementAgentTests(unittest.TestCase):
    def test_manager_band(self):
        result = assess_request(request(amount=1200), POLICY)
        self.assertEqual(result["review_route"], "manager_review")
        self.assertEqual(result["status"], "review_required")

    def test_finance_band(self):
        result = assess_request(request(amount=2500), POLICY)
        self.assertEqual(result["review_route"], "finance_review")

    def test_executive_band(self):
        result = assess_request(request(amount=7000), POLICY)
        self.assertEqual(result["review_route"], "executive_review")

    def test_urgent_request_gets_priority_review(self):
        result = assess_request(request(urgency="urgent"), POLICY)
        self.assertEqual(result["review_route"], "priority_review")

    def test_unverified_supplier_requires_due_diligence(self):
        result = assess_request(request(supplier_status="unverified"), POLICY)
        self.assertEqual(result["review_route"], "supplier_due_diligence")

    def test_missing_fields_are_reported(self):
        item = request()
        del item["item"]
        result = assess_request(item, POLICY)
        self.assertEqual(result["status"], "needs_information")
        self.assertIn("item", result["missing_fields"])

    def test_invalid_amount_is_rejected(self):
        for amount in (-1, 0, True, "100", float("inf"), float("nan")):
            with self.subTest(amount=amount):
                result = assess_request(request(amount=amount), POLICY)
                self.assertEqual(result["status"], "rejected_input")

    def test_non_string_required_field_is_rejected(self):
        result = assess_request(request(supplier=42), POLICY)
        self.assertEqual(result["status"], "rejected_input")
        self.assertIn("supplier", result["invalid_fields"])

    def test_currency_mismatch_is_rejected(self):
        result = assess_request(request(currency="USD"), POLICY)
        self.assertEqual(result["status"], "rejected_input")

    def test_unknown_category_is_rejected(self):
        result = assess_request(request(category="marketing"), POLICY)
        self.assertEqual(result["status"], "rejected_input")

    def test_duplicate_ids_are_flagged(self):
        report = build_report([request(), request(item="Second item")], POLICY)
        self.assertEqual([d["status"] for d in report["decisions"]],
                         ["duplicate_review", "duplicate_review"])

    def test_policy_threshold_order_is_checked(self):
        with self.assertRaises(ValueError):
            validate_policy({**POLICY, "manager_review_limit": 6000})

    def test_no_purchase_order_is_created(self):
        result = assess_request(request(), POLICY)
        self.assertFalse(result["purchase_order_created"])
        self.assertIn("no_purchase_order_created", result["trace"])

    def test_non_object_request_is_rejected(self):
        result = assess_request("not an object", POLICY)
        self.assertEqual(result["status"], "rejected_input")


if __name__ == "__main__":
    unittest.main()
