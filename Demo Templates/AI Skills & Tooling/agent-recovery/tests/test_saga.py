import unittest

from saga import SagaStep, run_saga


class SagaRecoveryTests(unittest.TestCase):
    def test_success_completes_without_compensation(self):
        result = run_saga([SagaStep("one", lambda _: 1), SagaStep("two", lambda _: 2)])
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["outputs"], {"one": 1, "two": 2})

    def test_failure_compensates_in_reverse_order(self):
        calls = []
        steps = [
            SagaStep("one", lambda _: "one", lambda _ctx, result: calls.append(result)),
            SagaStep("two", lambda _: "two", lambda _ctx, result: calls.append(result)),
            SagaStep("three", lambda _: 1 / 0),
        ]
        result = run_saga(steps)
        self.assertEqual(result["status"], "ROLLED_BACK")
        self.assertEqual(calls, ["two", "one"])

    def test_compensation_failure_is_reported(self):
        steps = [
            SagaStep("one", lambda _: "ok", lambda _ctx, _result: 1 / 0),
            SagaStep("two", lambda _: 1 / 0),
        ]
        result = run_saga(steps)
        self.assertEqual(result["status"], "PARTIAL_ROLLBACK")
        self.assertEqual(result["compensation_errors"], ["one"])

    def test_retry_is_bounded(self):
        attempts = {"count": 0}
        def flaky(_):
            attempts["count"] += 1
            if attempts["count"] < 2:
                raise RuntimeError()
            return "ok"
        result = run_saga([SagaStep("retry", flaky, max_attempts=2)])
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(attempts["count"], 2)

    def test_duplicate_step_ids_rejected(self):
        result = run_saga([SagaStep("same", lambda _: 1), SagaStep("same", lambda _: 2)])
        self.assertEqual(result["reason"], "INVALID_STEP_IDS")

    def test_step_limit_rejected(self):
        result = run_saga([SagaStep("one", lambda _: 1), SagaStep("two", lambda _: 2)], max_steps=1)
        self.assertEqual(result["reason"], "INVALID_STEP_COUNT")

    def test_compensation_skipped_when_not_defined(self):
        result = run_saga([SagaStep("one", lambda _: "ok"), SagaStep("two", lambda _: 1 / 0)])
        self.assertEqual(result["status"], "ROLLED_BACK")
        self.assertTrue(any(item["event"] == "COMPENSATION_SKIPPED" for item in result["events"]))


if __name__ == "__main__":
    unittest.main()
