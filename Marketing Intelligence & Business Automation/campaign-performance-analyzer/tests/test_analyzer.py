import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyzer import calculate_metrics, load_campaigns, run, safe_divide, summarize


class CampaignAnalyzerTests(unittest.TestCase):
    def test_metric_calculations(self):
        result = calculate_metrics({
            "campaign": "Test", "channel": "Search", "spend": 100,
            "impressions": 1000, "clicks": 100, "conversions": 10, "revenue": 400,
        })
        self.assertAlmostEqual(result["ctr"], 0.1)
        self.assertAlmostEqual(result["conversion_rate"], 0.1)
        self.assertEqual(result["cpc"], 1)
        self.assertEqual(result["cpa"], 10)
        self.assertEqual(result["roas"], 4)

    def test_zero_denominators_are_null(self):
        self.assertIsNone(safe_divide(12, 0))
        result = calculate_metrics({
            "campaign": "Zero", "channel": "Other", "spend": 0,
            "impressions": 0, "clicks": 0, "conversions": 0, "revenue": 0,
        })
        for key in ("ctr", "conversion_rate", "cpc", "cpa", "roas"):
            self.assertIsNone(result[key])

    def test_aggregate_metrics_use_totals_not_average_of_rates(self):
        summary = summarize([
            {"spend": 100, "impressions": 1000, "clicks": 100, "conversions": 10, "revenue": 200},
            {"spend": 100, "impressions": 9000, "clicks": 90, "conversions": 9, "revenue": 300},
        ])
        self.assertEqual(summary["campaign_count"], 2)
        self.assertAlmostEqual(summary["ctr"], 190 / 10000)
        self.assertAlmostEqual(summary["roas"], 2.5)

    def test_invalid_rows_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "input.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=[
                    "campaign", "channel", "spend", "impressions", "clicks", "conversions", "revenue"
                ])
                writer.writeheader()
                writer.writerow({"campaign":"Good","channel":"Search","spend":"10","impressions":"100","clicks":"10","conversions":"2","revenue":"20"})
                writer.writerow({"campaign":"Bad","channel":"Search","spend":"-1","impressions":"100","clicks":"10","conversions":"2","revenue":"20"})
                writer.writerow({"campaign":"Impossible","channel":"Social","spend":"1","impressions":"10","clicks":"11","conversions":"1","revenue":"2"})
            valid, errors = load_campaigns(path)
            self.assertEqual(len(valid), 1)
            self.assertEqual(len(errors), 2)

    def test_run_writes_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "input.csv"
            source.write_text(
                "campaign,channel,spend,impressions,clicks,conversions,revenue\n"
                "A,Search,100,1000,100,10,400\n", encoding="utf-8"
            )
            result = run(source, root / "out")
            self.assertEqual(result["summary"]["campaign_count"], 1)
            self.assertTrue((root / "out" / "campaign_metrics.csv").exists())
            saved = json.loads((root / "out" / "summary.json").read_text())
            self.assertEqual(saved["summary"]["roas"], 4)


if __name__ == "__main__":
    unittest.main()
