import unittest

from evaluate import evaluate


class AgentEvaluationTests(unittest.TestCase):
    def test_matching_expectations_pass(self):
        actual = {
            "status": "COMPLETED",
            "output": {"queue": "support"},
            "trace": [{"agent": "intake"}, {"agent": "review"}],
            "events": [{"event": "AGENT_HANDOFF"}],
        }
        expected = {
            "status": "COMPLETED",
            "output_equals": {"queue": "support"},
            "required_agents": ["intake", "review"],
            "forbidden_agents": ["publisher"],
            "required_events": ["AGENT_HANDOFF"],
        }
        result = evaluate(actual, expected)
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(result["checks_failed"], 0)

    def test_mismatch_fails(self):
        actual = {"status": "ESCALATE", "trace": [], "events": []}
        result = evaluate(actual, {"status": "COMPLETED", "required_agents": ["review"]})
        self.assertEqual(result["result"], "FAIL")
        self.assertEqual(result["checks_failed"], 2)

    def test_forbidden_event_fails(self):
        actual = {"status": "COMPLETED", "trace": [], "events": [{"event": "EXTERNAL_ACTION"}]}
        result = evaluate(actual, {"forbidden_events": ["EXTERNAL_ACTION"]})
        self.assertEqual(result["result"], "FAIL")

    def test_empty_expectations_pass(self):
        self.assertEqual(evaluate({}, {})["result"], "PASS")

    def test_missing_output_object_fails_field_assertion(self):
        result = evaluate({"status": "COMPLETED"}, {"output_equals": {"queue": "support"}})
        self.assertEqual(result["result"], "FAIL")


if __name__ == "__main__":
    unittest.main()
