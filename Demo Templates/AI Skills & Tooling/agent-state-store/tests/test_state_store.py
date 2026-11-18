import tempfile
import unittest
from pathlib import Path

from state_store import StateConflictError, StateStore


class StateStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = StateStore(Path(self.temp.name) / "state.db")

    def tearDown(self):
        self.temp.cleanup()

    def test_create_and_read_state(self):
        created = self.store.create("wf-1", {"status": "RUNNING", "step": "intake"})
        self.assertEqual(created["version"], 1)
        loaded = self.store.get("wf-1")
        self.assertEqual(loaded["state"]["step"], "intake")

    def test_duplicate_workflow_rejected(self):
        self.store.create("wf-1", {"status": "PENDING"})
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.store.create("wf-1", {"status": "PENDING"})

    def test_optimistic_version_update(self):
        self.store.create("wf-1", {"status": "RUNNING"})
        saved = self.store.save("wf-1", {"status": "COMPLETED"}, expected_version=1)
        self.assertEqual(saved["version"], 2)
        self.assertEqual(self.store.get("wf-1")["status"], "COMPLETED")

    def test_stale_version_rejected(self):
        self.store.create("wf-1", {"status": "RUNNING"})
        self.store.save("wf-1", {"status": "PAUSED"}, expected_version=1)
        with self.assertRaises(StateConflictError):
            self.store.save("wf-1", {"status": "COMPLETED"}, expected_version=1)

    def test_missing_workflow_update_rejected(self):
        with self.assertRaises(KeyError):
            self.store.save("missing", {"status": "FAILED"}, expected_version=1)

    def test_events_are_append_only_and_ordered(self):
        self.store.create("wf-1", {"status": "RUNNING"})
        first = self.store.append_event("wf-1", "STEP_STARTED", {"step": "one"})
        second = self.store.append_event("wf-1", "STEP_COMPLETED", {"step": "one"})
        events = self.store.events("wf-1")
        self.assertEqual([item["event_id"] for item in events], [first, second])
        self.assertEqual([item["event_type"] for item in events], ["STEP_STARTED", "STEP_COMPLETED"])

    def test_invalid_non_json_value_rejected(self):
        with self.assertRaises(ValueError):
            self.store.create("wf-1", {"status": "RUNNING", "bad": object()})

    def test_invalid_state_shape_rejected(self):
        with self.assertRaises(ValueError):
            self.store.create("wf-1", ["not", "an", "object"])


if __name__ == "__main__":
    unittest.main()
