import json
import tempfile
import unittest
from pathlib import Path

from crm_router import load_rules, route_records


RULES = {
    "qualification_threshold": 60,
    "weights": {"company_provided": 20, "business_email": 15, "need_provided": 25,
                "budget_confirmed": 20, "decision_role_confirmed": 20},
    "territory_teams": {"south": "sales_south"},
    "follow_up_sla_calendar_days": 2,
    "free_email_domains": ["gmail.com"]
}


class CrmRouterTests(unittest.TestCase):
    def setUp(self):
        self.qualified = {
            "lead_id": "L1", "name": "Test Lead", "email": "person@company.example",
            "company": "Company", "need": "Automation", "budget_confirmed": "true",
            "decision_role_confirmed": "false", "territory": "south",
            "created_date": "2026-11-17"
        }

    def test_qualified_lead_routes_to_territory_team(self):
        routed, review = route_records([self.qualified], RULES)
        self.assertEqual(review, [])
        self.assertEqual(routed[0]["route"], "sales_queue")
        self.assertEqual(routed[0]["assigned_team"], "sales_south")
        self.assertEqual(routed[0]["follow_up_due_date"], "2026-11-19")

    def test_free_email_reduces_score_and_nurtures(self):
        row = {**self.qualified, "email": "person@gmail.com", "budget_confirmed": "false"}
        routed, review = route_records([row], RULES)
        self.assertEqual(review, [])
        self.assertEqual(routed[0]["route"], "nurture_queue")

    def test_missing_required_field_goes_to_review(self):
        row = {**self.qualified, "name": ""}
        routed, review = route_records([row], RULES)
        self.assertEqual(routed, [])
        self.assertIn("missing_name", review[0]["review_reasons"])

    def test_duplicate_email_goes_to_review(self):
        second = {**self.qualified, "lead_id": "L2"}
        routed, review = route_records([self.qualified, second], RULES)
        self.assertEqual(len(routed), 1)
        self.assertIn("duplicate_email", review[0]["review_reasons"])

    def test_qualified_unmapped_territory_goes_to_review(self):
        row = {**self.qualified, "territory": "central"}
        routed, review = route_records([row], RULES)
        self.assertEqual(routed, [])
        self.assertEqual(review[0]["review_reasons"], "unmapped_territory")

    def test_invalid_rule_weights_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rules.json"
            path.write_text(json.dumps({**RULES, "weights": {"company_provided": -1}}))
            with self.assertRaises(ValueError):
                load_rules(path)

    def test_invalid_email_goes_to_review(self):
        row = {**self.qualified, "email": "not-an-email"}
        routed, review = route_records([row], RULES)
        self.assertEqual(routed, [])
        self.assertIn("invalid_email_format", review[0]["review_reasons"])


if __name__ == "__main__":
    unittest.main()
