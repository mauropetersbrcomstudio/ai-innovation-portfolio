import tempfile
import unittest
from pathlib import Path

from durable_runner import PlanConflictError, run_durable_workflow


class DurableRunnerTests(unittest.TestCase):
    def test_persists_each_step_and_resumes_without_repeating_completed_steps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            calls = {"first": 0, "second": 0}

            def first(payload):
                calls["first"] += 1
                return {"value": "one"}

            def second(payload):
                calls["second"] += 1
                return {"value": payload["previous_outputs"]["first"]["value"] + "-two"}

            handlers = {"first": first, "second": second}
            result = run_durable_workflow("wf-1", ["first", "second"], handlers, {"input": "x"},
                                          root / "state.db", root / "events.jsonl")
            self.assertEqual(result["workflow"]["status"], "COMPLETED")
            again = run_durable_workflow("wf-1", ["first", "second"], handlers, {"input": "x"},
                                         root / "state.db", root / "events.jsonl")
            self.assertTrue(again["resumed"])
            self.assertEqual(calls, {"first": 1, "second": 1})

    def test_failed_step_can_resume_with_same_idempotency_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seen_keys = []
            attempts = {"count": 0}

            def flaky(payload):
                seen_keys.append(payload["idempotency_key"])
                attempts["count"] += 1
                if attempts["count"] == 1:
                    raise RuntimeError("simulated interruption")
                return {"accepted": True}

            first = run_durable_workflow("wf-2", ["flaky"], {"flaky": flaky}, {},
                                         root / "state.db", root / "events.jsonl")
            self.assertEqual(first["workflow"]["status"], "FAILED")
            second = run_durable_workflow("wf-2", ["flaky"], {"flaky": flaky}, {},
                                          root / "state.db", root / "events.jsonl")
            self.assertEqual(second["workflow"]["status"], "COMPLETED")
            self.assertEqual(seen_keys[0], seen_keys[1])

    def test_rejects_changed_plan_or_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handlers = {"step": lambda payload: {"ok": True}}
            run_durable_workflow("wf-3", ["step"], handlers, {"version": 1},
                                 root / "state.db", root / "events.jsonl")
            with self.assertRaises(PlanConflictError):
                run_durable_workflow("wf-3", ["step"], handlers, {"version": 2},
                                     root / "state.db", root / "events.jsonl")

    def test_rejects_missing_handler_before_creating_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(ValueError):
                run_durable_workflow("wf-4", ["missing"], {}, {}, root / "state.db", root / "events.jsonl")
            self.assertFalse((root / "state.db").exists())


if __name__ == "__main__":
    unittest.main()
