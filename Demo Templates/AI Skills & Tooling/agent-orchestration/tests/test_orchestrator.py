import unittest

from orchestrator import Orchestrator, Step


class OrchestratorTests(unittest.TestCase):
    def test_runs_steps_in_order_and_captures_outputs(self):
        calls = []
        engine = Orchestrator({
            "one": lambda payload: calls.append("one") or {"value": 1},
            "two": lambda payload: calls.append("two") or {"value": payload["previous_outputs"]["first"]["value"] + 1},
        })
        state = engine.start("wf-1", [Step("first", "one"), Step("second", "two")])
        self.assertEqual(state.status, "COMPLETED")
        self.assertEqual(calls, ["one", "two"])
        self.assertEqual(state.outputs["second"]["value"], 2)

    def test_approval_gate_pauses_and_resumes(self):
        calls = []
        engine = Orchestrator({"run": lambda payload: calls.append(payload["step_id"]) or "ok"})
        steps = [Step("prepare", "run"), Step("publish", "run", requires_approval=True), Step("finish", "run")]
        state = engine.start("wf-2", steps)
        self.assertEqual(state.status, "WAITING_FOR_APPROVAL")
        self.assertEqual(calls, ["prepare"])
        engine.approve_and_resume(state, steps, "publish")
        self.assertEqual(state.status, "COMPLETED")
        self.assertEqual(calls, ["prepare", "publish", "finish"])

    def test_retry_is_bounded(self):
        count = {"n": 0}
        def flaky(_):
            count["n"] += 1
            if count["n"] < 3:
                raise RuntimeError("temporary")
            return "done"
        engine = Orchestrator({"flaky": flaky})
        state = engine.start("wf-3", [Step("retry", "flaky", max_attempts=3)])
        self.assertEqual(state.status, "COMPLETED")
        self.assertEqual(state.attempts["retry"], 3)

    def test_exhausted_retries_fail_closed(self):
        engine = Orchestrator({"bad": lambda _: 1 / 0})
        state = engine.start("wf-4", [Step("bad-step", "bad", max_attempts=2)])
        self.assertEqual(state.status, "FAILED")
        self.assertNotIn("bad-step", state.outputs)

    def test_unknown_handler_rejects_workflow(self):
        engine = Orchestrator({})
        state = engine.start("wf-5", [Step("step", "missing")])
        self.assertEqual(state.status, "FAILED")
        self.assertEqual(state.events[-1]["reason"], "INVALID_STEP_CONFIGURATION")

    def test_duplicate_step_ids_rejected(self):
        engine = Orchestrator({"run": lambda _: None})
        state = engine.start("wf-6", [Step("same", "run"), Step("same", "run")])
        self.assertEqual(state.events[-1]["reason"], "INVALID_OR_DUPLICATE_STEP_ID")

    def test_cancel_prevents_further_execution(self):
        calls = []
        engine = Orchestrator({"run": lambda _: calls.append(1)})
        state = engine.start("wf-7", [Step("approval", "run", requires_approval=True)])
        engine.cancel(state)
        self.assertEqual(state.status, "CANCELLED")
        engine.approve_and_resume(state, [Step("approval", "run", requires_approval=True)], "approval")
        self.assertEqual(calls, [])

    def test_workflow_step_limit(self):
        engine = Orchestrator({"run": lambda _: None}, max_workflow_steps=1)
        state = engine.start("wf-8", [Step("a", "run"), Step("b", "run")])
        self.assertEqual(state.events[-1]["reason"], "STEP_LIMIT_EXCEEDED")


if __name__ == "__main__":
    unittest.main()
