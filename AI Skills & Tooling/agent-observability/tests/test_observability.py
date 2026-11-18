import json
import tempfile
import unittest
from pathlib import Path

from observability import JsonlEventLogger, redact


class ObservabilityTests(unittest.TestCase):
    def test_recursive_redaction(self):
        value = {
            "user": "Ana",
            "api_key": "do-not-log",
            "nested": {"Authorization": "Bearer secret", "safe": 3},
            "items": [{"refresh-token": "hidden"}],
        }
        cleaned = redact(value)
        self.assertEqual(cleaned["api_key"], "[REDACTED]")
        self.assertEqual(cleaned["nested"]["Authorization"], "[REDACTED]")
        self.assertEqual(cleaned["items"][0]["refresh-token"], "[REDACTED]")
        self.assertEqual(cleaned["nested"]["safe"], 3)

    def test_redaction_normalizes_common_sensitive_key_variants(self):
        sensitive = {
            "apiKey": "one",
            "API Key": "two",
            "X-API-Key": "three",
            "clientSecret": "four",
            "private.key": "five",
            "sessionToken": "six",
            "Set-Cookie": "seven",
            "JWT": "eight",
            "auth": "nine",
        }
        safe = {"tokenizer": "keep", "secretary": "keep", "monkey": "keep"}

        cleaned = redact({**sensitive, **safe})

        for key in sensitive:
            with self.subTest(key=key):
                self.assertEqual(cleaned[key], "[REDACTED]")
        for key, value in safe.items():
            with self.subTest(key=key):
                self.assertEqual(cleaned[key], value)

    def test_emit_persists_structured_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = JsonlEventLogger(Path(tmp) / "logs" / "events.jsonl")
            event = logger.emit("STEP_COMPLETED", workflow_id="wf-1", agent="review",
                                details={"result": "ok", "password": "secret"})
            loaded = logger.read_events()
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["event_type"], "STEP_COMPLETED")
            self.assertEqual(loaded[0]["details"]["password"], "[REDACTED]")
            self.assertEqual(event["level"], "INFO")

    def test_append_preserves_event_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = JsonlEventLogger(Path(tmp) / "events.jsonl")
            logger.emit("START")
            logger.emit("END", level="warning")
            self.assertEqual([x["event_type"] for x in logger.read_events()], ["START", "END"])

    def test_invalid_level_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = JsonlEventLogger(Path(tmp) / "events.jsonl")
            with self.assertRaises(ValueError):
                logger.emit("EVENT", level="TRACE")

    def test_non_string_level_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = JsonlEventLogger(Path(tmp) / "events.jsonl")
            with self.assertRaisesRegex(ValueError, "level must be a string"):
                logger.emit("EVENT", level=None)

    def test_invalid_event_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            logger = JsonlEventLogger(Path(tmp) / "events.jsonl")
            with self.assertRaises(ValueError):
                logger.emit(" ")

    def test_unsupported_log_value_rejected(self):
        with self.assertRaises(ValueError):
            redact({"not_serializable": object()})

    def test_corrupt_jsonl_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            path.write_text("{broken}\\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line 1"):
                JsonlEventLogger(path).read_events()


if __name__ == "__main__":
    unittest.main()
