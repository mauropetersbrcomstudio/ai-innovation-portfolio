import csv
import tempfile
import unittest
from pathlib import Path

from launch_qa import run, validate_row


BASE = {
    "campaign_id": "CMP-001",
    "campaign_name": "Spring",
    "destination_url": "https://example.com/path?ref=home",
    "utm_source": "linkedin",
    "utm_medium": "social",
    "utm_campaign": "spring",
    "start_date": "2026-12-01",
    "end_date": "2026-12-14",
    "budget": "2500.00",
    "utm_content": "carousel",
}


class LaunchQaTests(unittest.TestCase):
    def test_builds_tracking_url_and_preserves_existing_query(self):
        result, errors = validate_row(BASE, set())
        self.assertEqual(errors, [])
        self.assertIn("ref=home", result["tracking_url"])
        self.assertIn("utm_source=linkedin", result["tracking_url"])
        self.assertIn("utm_content=carousel", result["tracking_url"])

    def test_rejects_non_http_url_and_embedded_credentials(self):
        for url in ("javascript:alert(1)", "https://user:pass@example.com"):
            row = {**BASE, "destination_url": url}
            _, errors = validate_row(row, set())
            self.assertTrue(any("destination_url" in error for error in errors))

    def test_rejects_existing_utm_parameters(self):
        row = {**BASE, "destination_url": "https://example.com/?utm_source=old"}
        _, errors = validate_row(row, set())
        self.assertIn("destination_url already contains UTM parameters", errors)

    def test_rejects_invalid_dates_and_reversed_range(self):
        for start, end in (("2026-02-30", "2026-03-01"), ("2026-12-20", "2026-12-01")):
            _, errors = validate_row({**BASE, "start_date": start, "end_date": end}, set())
            self.assertTrue(any("date" in error for error in errors))

    def test_rejects_negative_nonfinite_or_invalid_budget(self):
        for budget in ("-1", "NaN", "Infinity", "abc"):
            _, errors = validate_row({**BASE, "budget": budget}, set())
            self.assertIn("budget must be a finite non-negative decimal number", errors)

    def test_missing_fields_are_reported(self):
        row = {**BASE, "utm_source": "", "campaign_name": ""}
        _, errors = validate_row(row, set())
        self.assertIn("utm_source is required", errors)
        self.assertIn("campaign_name is required", errors)

    def test_duplicate_campaign_ids_flag_every_occurrence_and_source_is_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input.csv"
            output = root / "out"
            rows = [BASE, {**BASE, "campaign_name": "Duplicate"}]
            with source.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(BASE))
                writer.writeheader()
                writer.writerows(rows)
            before = source.read_bytes()
            summary = run(source, output)
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(summary["approved_rows"], 0)
            self.assertEqual(summary["exception_rows"], 2)
            with (output / "exceptions.csv").open(encoding="utf-8", newline="") as handle:
                exceptions = list(csv.DictReader(handle))
            self.assertTrue(all("campaign_id is duplicated" in item["reasons"] for item in exceptions))

    def test_outputs_are_created_and_status_reflects_review(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input.csv"
            with source.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(BASE))
                writer.writeheader()
                writer.writerow(BASE)
                writer.writerow({**BASE, "campaign_id": "CMP-002", "budget": "-3"})
            summary = run(source, root / "out")
            self.assertEqual(summary["status"], "review")
            self.assertEqual(summary["approved_rows"], 1)
            self.assertTrue((root / "out" / "approved_campaigns.csv").exists())
            self.assertTrue((root / "out" / "exceptions.csv").exists())
            self.assertTrue((root / "out" / "summary.json").exists())

    def test_missing_required_headers_fail_before_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input.csv"
            source.write_text("campaign_id,campaign_name\n1,Only partial\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Missing required CSV columns"):
                run(source, root / "out")
            self.assertFalse((root / "out").exists())


if __name__ == "__main__":
    unittest.main()
