import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skill import build_plan, normalize_brief, render_markdown, run


class BriefToTaskTests(unittest.TestCase):
    def test_missing_fields_become_questions_not_inventions(self):
        plan = build_plan({"title": "Small brief", "deliverables": ["Create a report"]})
        self.assertEqual(plan["status"], "NEEDS_CLARIFICATION")
        self.assertEqual(len(plan["task_breakdown"]), 1)
        self.assertIsNone(plan["task_breakdown"][0]["owner"])
        self.assertTrue(plan["open_questions"])
        self.assertEqual(plan["source_brief"]["deadline"], "")

    def test_supplied_values_are_preserved_and_assumptions_separated(self):
        plan = build_plan({
            "title": "  Project A  ", "objective": " Keep wording ",
            "deliverables": ["One output"], "assumptions": ["User supplied assumption"],
        })
        self.assertEqual(plan["title"], "Project A")
        self.assertEqual(plan["source_brief"]["objective"], "Keep wording")
        self.assertEqual(plan["assumptions"], ["User supplied assumption"])
        self.assertNotIn("User supplied assumption", plan["confirmed_requirements"]["constraints"])

    def test_acceptance_criteria_are_not_fabricated(self):
        plan = build_plan({"title": "A", "deliverables": ["B"]})
        task = plan["task_breakdown"][0]
        self.assertEqual(task["acceptance_criteria"], [])
        self.assertEqual(task["acceptance_status"], "unresolved")

    def test_invalid_types_are_rejected(self):
        with self.assertRaises(ValueError):
            normalize_brief({"title": "A", "deliverables": [42]})
        with self.assertRaises(ValueError):
            normalize_brief({"title": 12})

    def test_markdown_and_json_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "brief.json"
            source.write_text(json.dumps({
                "title": "Output test", "deliverables": ["Build demo"],
            }), encoding="utf-8")
            plan = run(source, root / "out")
            saved = json.loads((root / "out" / "task_plan.json").read_text(encoding="utf-8"))
            markdown = (root / "out" / "task_plan.md").read_text(encoding="utf-8")
            self.assertEqual(saved["title"], "Output test")
            self.assertIn("Build demo", markdown)
            self.assertEqual(len(plan["task_breakdown"]), 1)


if __name__ == "__main__":
    unittest.main()
