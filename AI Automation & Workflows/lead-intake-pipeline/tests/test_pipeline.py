import csv
import json
import tempfile
import unittest
from pathlib import Path

from pipeline import normalize, process_rows, route_lead, run, score_lead


class PipelineTests(unittest.TestCase):
    def test_normalize_collapses_whitespace(self):
        self.assertEqual(normalize("  Ada   Lovelace  "), "Ada Lovelace")

    def test_score_and_routes(self):
        lead = {
            "name": "Ada", "email": "ada@company.example",
            "company": "Company", "service": "AI", "source": "Website",
        }
        self.assertEqual(score_lead(lead), 100)
        self.assertEqual(route_lead(100), "priority")
        self.assertEqual(route_lead(40), "standard")
        self.assertEqual(route_lead(39), "review")

    def test_invalid_and_duplicate_rows_are_exceptions(self):
        rows = [
            {"name": "Ada", "email": "ada@company.example", "company": "", "service": "", "source": ""},
            {"name": "Bad", "email": "not-an-email", "company": "", "service": "", "source": ""},
            {"name": "Ada Again", "email": "ada@company.example", "company": "", "service": "", "source": ""},
            {"name": "", "email": "missing@example.com", "company": "", "service": "", "source": ""},
        ]
        processed, exceptions = process_rows(rows)
        self.assertEqual(len(processed), 1)
        self.assertEqual([item["reason"] for item in exceptions],
                         ["invalid_email", "duplicate_email", "missing_name"])

    def test_run_writes_expected_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "leads.csv"
            with source.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["name", "email", "company", "service", "source"])
                writer.writeheader()
                writer.writerow({"name": "Ada", "email": "ada@company.example",
                                 "company": "Company", "service": "AI", "source": "Website"})
            output = root / "out"
            summary = run(source, output)
            self.assertEqual(summary["processed_rows"], 1)
            self.assertTrue((output / "processed_leads.csv").exists())
            self.assertTrue((output / "exceptions.csv").exists())
            self.assertEqual(json.loads((output / "summary.json").read_text())["routes"]["priority"], 1)

    def test_missing_required_columns_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "bad.csv"
            source.write_text("name,company\nAda,Example\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                run(source, Path(temp) / "out")


if __name__ == "__main__":
    unittest.main()
