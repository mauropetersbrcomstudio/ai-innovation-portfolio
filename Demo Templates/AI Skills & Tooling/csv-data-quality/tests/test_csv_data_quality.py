import tempfile
import unittest
from pathlib import Path

from csv_data_quality import analyze_csv


class CsvDataQualityTests(unittest.TestCase):
    def analyze(self, content: str, keys=None):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "sample.csv"
            source.write_text(content, encoding="utf-8")
            return analyze_csv(source, keys)

    def test_clean_file(self):
        report = self.analyze("id,name\n1,Ana\n2,Bruno\n")
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["row_count"], 2)

    def test_detects_duplicate_rows_and_keys(self):
        report = self.analyze("id,name\n1,Ana\n1,Ana\n1,Bia\n", ["id"])
        self.assertEqual(report["duplicate_rows"], [3])
        self.assertEqual(len(report["duplicate_keys"]), 2)
        self.assertEqual(report["status"], "review")

    def test_detects_malformed_row(self):
        report = self.analyze("id,name\n1,Ana\n2\n")
        self.assertEqual(report["malformed_rows"], [3])
        self.assertEqual(report["status"], "invalid")

    def test_counts_blank_rows_and_empty_cells(self):
        report = self.analyze("id,name\n1,\n  ,  \n2,Bia\n")
        self.assertEqual(report["blank_rows"], 1)
        self.assertEqual(report["empty_cells_by_column"]["name"], 1)
        self.assertEqual(report["status"], "review")

    def test_duplicate_headers_are_invalid(self):
        report = self.analyze("id,id\n1,2\n")
        self.assertIn("duplicate_headers", report["issues"])
        self.assertEqual(report["status"], "invalid")

    def test_missing_key_column_is_reported(self):
        report = self.analyze("id,name\n1,Ana\n", ["email"])
        self.assertEqual(report["missing_key_columns"], ["email"])
        self.assertEqual(report["status"], "invalid")

    def test_empty_file(self):
        report = self.analyze("")
        self.assertEqual(report["status"], "invalid")
        self.assertIn("empty_file", report["issues"])


if __name__ == "__main__":
    unittest.main()
