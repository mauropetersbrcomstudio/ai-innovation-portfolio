import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mapper import assess, build_report, classify, run, validate_opportunity


def opportunity(**overrides):
    item = {
        "name": "Invoice entry", "problem": "Manual invoice entry.",
        "frequency": 5, "time_burden": 4, "standardization": 5,
        "data_readiness": 4, "user_impact": 4, "risk": 2,
    }
    item.update(overrides)
    return item


class OpportunityMapperTests(unittest.TestCase):
    def test_score_applies_inverse_risk(self):
        result = assess(opportunity())
        self.assertEqual(result["risk_adjusted_score"], 4)
        self.assertEqual(result["rubric_score"], 4.33)
        self.assertEqual(result["recommendation"], "PRIORITIZE_FOR_DISCOVERY")

    def test_risk_reduces_score(self):
        low_risk = assess(opportunity(risk=1))
        high_risk = assess(opportunity(risk=5))
        self.assertGreater(low_risk["rubric_score"], high_risk["rubric_score"])

    def test_classification_thresholds(self):
        self.assertEqual(classify(4.0), "PRIORITIZE_FOR_DISCOVERY")
        self.assertEqual(classify(3.0), "INVESTIGATE")
        self.assertEqual(classify(2.99), "DEFER_OR_REDESIGN")

    def test_invalid_scores_are_rejected(self):
        with self.assertRaises(ValueError):
            validate_opportunity(opportunity(frequency=6), 1)
        with self.assertRaises(ValueError):
            validate_opportunity(opportunity(risk=True), 1)

    def test_report_sorts_and_preserves_user_problem(self):
        report = build_report({"opportunities": [
            opportunity(name="Zeta"),
            opportunity(name="Alpha", frequency=1, time_burden=1, standardization=1,
                        data_readiness=1, user_impact=1, risk=5),
        ]})
        self.assertEqual(report["assessments"][0]["name"], "Zeta")
        self.assertEqual(report["assessments"][0]["problem"], "Manual invoice entry.")

    def test_cli_writes_json_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "input.json"
            source.write_text(json.dumps({"opportunities": [opportunity()]}), encoding="utf-8")
            output = root / "out" / "report.json"
            result = run(source, output)
            saved = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(len(result["assessments"]), 1)
            self.assertEqual(saved["status"], "RUBRIC_ASSESSMENT")


if __name__ == "__main__":
    unittest.main()
