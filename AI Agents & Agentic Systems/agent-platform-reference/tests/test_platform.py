import tempfile
import unittest
from pathlib import Path

from platform import execute_reference_workflow


class AgentPlatformReferenceTests(unittest.TestCase):
    def test_workflow_state_and_events_are_persisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = execute_reference_workflow(
                "wf-test", "Review this support request", root / "state.db", root / "events.jsonl"
            )
            self.assertEqual(result["workflow"]["status"], "COMPLETED")
            self.assertEqual(result["workflow"]["state"]["completed_steps"], ["validation", "preparation"])
            self.assertTrue(result["events"])
            self.assertEqual(result["log_events"][0]["event_type"], "WORKFLOW_CREATED")

    def test_empty_request_fails_closed_and_state_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = execute_reference_workflow("wf-empty", " ", root / "state.db", root / "events.jsonl")
            self.assertEqual(result["workflow"]["status"], "FAILED")
            self.assertEqual(result["workflow"]["state"]["completed_steps"], [])
            self.assertTrue(any(x["event_type"] == "WORKFLOW_FAILED" for x in result["events"]))


if __name__ == "__main__":
    unittest.main()
