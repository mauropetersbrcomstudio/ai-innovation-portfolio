import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Marketing Intelligence & Business Automation" / "marketing-analytics-pipeline"))
from pipeline import PreflightBlocked, run_pipeline


class MarketingPipelineTests(unittest.TestCase):
    def write_csv(self, path: Path, rows: list[list[str]]) -> None:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["campaign", "channel", "spend", "impressions", "clicks", "conversions", "revenue"])
            writer.writerows(rows)

    def test_clean_csv_runs_preflight_and_analysis(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, output = root / "campaigns.csv", root / "out"
            self.write_csv(source, [["A", "Search", "100", "1000", "100", "10", "400"]])
            result = run_pipeline(source, output)
            self.assertEqual(result["preflight_status"], "ok")
            self.assertEqual(result["summary"]["campaign_count"], 1)
            self.assertTrue((output / "quality_report.json").exists())
            self.assertTrue((output / "campaign_metrics.csv").exists())

    def test_review_status_blocks_by_default_and_can_be_explicitly_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, output = root / "campaigns.csv", root / "out"
            self.write_csv(source, [
                ["A", "Search", "100", "1000", "100", "10", "400"],
                ["B", "", "50", "500", "20", "2", "100"],
            ])
            with self.assertRaises(PreflightBlocked):
                run_pipeline(source, output)
            result = run_pipeline(source, output, allow_review=True)
            self.assertEqual(result["preflight_status"], "review")
            self.assertEqual(result["summary"]["campaign_count"], 1)
            self.assertEqual(result["exception_count"], 1)

    def test_invalid_structure_blocks_analysis(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, output = root / "bad.csv", root / "out"
            source.write_text("campaign,channel\nA,Search,extra\n", encoding="utf-8")
            with self.assertRaises(PreflightBlocked):
                run_pipeline(source, output)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
