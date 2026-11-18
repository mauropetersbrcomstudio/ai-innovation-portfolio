import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from server import DEMO_WORKFLOW_ID, create_server, seed_demo


class WorkspaceServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.database, self.events = root / "workflow.sqlite", root / "events.jsonl"
        seed_demo(self.database, self.events)
        self.server = create_server(self.database, port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp.cleanup()

    def call(self, path, payload=None):
        data = None if payload is None else json.dumps(payload).encode()
        request = Request(self.base + path, data=data,
                          headers={"Content-Type": "application/json"} if data else {})
        try:
            with urlopen(request, timeout=3) as response:
                return response.status, json.loads(response.read())
        except HTTPError as exc:
            return exc.code, json.loads(exc.read())

    def test_health_and_demo_workflow(self):
        self.assertEqual(self.call("/api/health")[1]["status"], "ok")
        status, data = self.call(f"/api/workflows/{DEMO_WORKFLOW_ID}")
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "COMPLETED")
        self.assertGreater(len(data["items"]), 0)

    def test_records_decision_and_returns_it_in_queue(self):
        _, data = self.call(f"/api/workflows/{DEMO_WORKFLOW_ID}")
        item = next(row for row in data["items"] if row["decision"] is None)
        status, result = self.call("/api/decisions", {
            "workflow_id": DEMO_WORKFLOW_ID, "item_id": item["item_id"],
            "reviewer_id": "demo-reviewer", "outcome": "REQUESTED_INFORMATION",
            "reason": "Confirm source details"
        })
        self.assertEqual(status, 201)
        self.assertEqual(result["decision"]["item_id"], item["item_id"])
        _, refreshed = self.call(f"/api/workflows/{DEMO_WORKFLOW_ID}")
        stored = next(row for row in refreshed["items"] if row["item_id"] == item["item_id"])
        self.assertEqual(stored["decision"]["outcome"], "REQUESTED_INFORMATION")
        self.assertTrue(any(event["event_type"] == "HUMAN_REVIEW_DECISION_RECORDED"
                            for event in refreshed["events"]))

    def test_duplicate_decision_is_conflict(self):
        _, data = self.call(f"/api/workflows/{DEMO_WORKFLOW_ID}")
        item = next(row for row in data["items"] if row["decision"] is None)
        payload = {"workflow_id": DEMO_WORKFLOW_ID, "item_id": item["item_id"],
                   "reviewer_id": "demo-reviewer", "outcome": "REJECTED", "reason": "Out of scope"}
        self.assertEqual(self.call("/api/decisions", payload)[0], 201)
        self.assertEqual(self.call("/api/decisions", payload)[0], 409)

    def test_invalid_outcome_and_unknown_item_are_rejected(self):
        base = {"workflow_id": DEMO_WORKFLOW_ID, "reviewer_id": "demo-reviewer", "reason": "Test"}
        self.assertEqual(self.call("/api/decisions", {**base, "item_id": "lead_intake:999", "outcome": "REJECTED"})[0], 404)
        _, data = self.call(f"/api/workflows/{DEMO_WORKFLOW_ID}")
        item = next(row for row in data["items"] if row["decision"] is None)
        self.assertEqual(self.call("/api/decisions", {**base, "item_id": item["item_id"], "outcome": "PAID"})[0], 400)

    def test_server_refuses_non_loopback_binding(self):
        with self.assertRaises(ValueError):
            create_server(self.database, host="0.0.0.0", port=0)


if __name__ == "__main__":
    unittest.main()
