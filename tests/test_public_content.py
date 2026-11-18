import tempfile
import unittest
from pathlib import Path

from scripts.check_public_content import (
    Finding,
    format_findings,
    scan_repository,
    scan_text,
)


class PublicContentScanTests(unittest.TestCase):
    def test_detects_private_key_marker_without_printing_key_material(self):
        marker = "-" * 5 + "BEGIN " + "PRIVATE KEY" + "-" * 5
        findings = scan_text("keys.txt", marker)
        self.assertIn(Finding("keys.txt", "private-key-block"), findings)

    def test_detects_common_provider_token_formats(self):
        examples = (
            ("github-token", "ghp_" + "A" * 36),
            ("github-token", "github_pat_" + "A" * 45),
            ("gitlab-token", "glpat-" + "A" * 30),
            ("aws-access-key-id", "AKIA" + "A" * 16),
            ("stripe-live-secret", "sk_live_" + "a" * 24),
            ("openai-project-key", "sk-proj-" + "A" * 30),
            ("anthropic-api-key", "sk-ant-api03-" + "A" * 30),
            ("slack-token", "xoxb-" + "1" * 12),
            ("google-api-key", "AIza" + "A" * 35),
            ("sendgrid-api-key", "SG." + "A" * 22 + "." + "B" * 22),
            ("huggingface-token", "hf_" + "A" * 32),
            ("jwt-like-token", "eyJ" + "A" * 12 + "." + "B" * 12 + "." + "C" * 12),
        )
        for expected_rule, value in examples:
            with self.subTest(rule=expected_rule, prefix=value[:8]):
                findings = scan_text("fixture.txt", value)
                self.assertIn(Finding("fixture.txt", expected_rule), findings)

    def test_detects_credential_bearing_url(self):
        value = "https://" + "demo-user" + ":" + "not-a-real-secret" + "@example.test/path"
        findings = scan_text("config.txt", value)
        self.assertIn(Finding("config.txt", "credential-url"), findings)

    def test_flags_environment_files_but_allows_named_examples(self):
        self.assertIn(
            Finding(".env.production", "environment-file"),
            scan_text(".env.production", "SETTING=placeholder"),
        )
        self.assertNotIn(
            Finding(".env.example", "environment-file"),
            scan_text(".env.example", "API_KEY=YOUR_API_KEY"),
        )
        self.assertNotIn(
            Finding(".env.sample", "environment-file"),
            scan_text(".env.sample", "API_KEY=replace-me"),
        )

    def test_ordinary_words_and_short_placeholders_do_not_trigger(self):
        content = (
            'password = "demo"; token = "YOUR_TOKEN"; '
            "tokenizer = True; secretary = False; api_key = 'replace-me'"
        )
        self.assertEqual(scan_text("example.py", content), [])

    def test_diagnostics_never_include_the_matched_value(self):
        value = "ghp_" + "Z" * 36
        findings = scan_text("settings.txt", "credential=" + value)
        rendered = format_findings(findings)
        self.assertIn("settings.txt", rendered)
        self.assertIn("github-token", rendered)
        self.assertNotIn(value, rendered)

    def test_repository_scan_skips_binary_and_oversized_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "binary.dat").write_bytes(b"\x00" + b"ghp_" + b"A" * 36)
            (root / "large.txt").write_text("x" * 100, encoding="utf-8")
            result = scan_repository(
                root,
                relative_paths=["binary.dat", "large.txt"],
                max_file_bytes=20,
            )
            self.assertEqual(result.scanned_files, 0)
            self.assertEqual(result.skipped_files, 2)
            self.assertEqual(result.findings, ())

    def test_repository_scan_reports_path_and_rule_not_secret_value(self):
        value = "ghp_" + "Q" * 36
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "settings.txt").write_text("token=" + value, encoding="utf-8")
            result = scan_repository(root, relative_paths=["settings.txt"])
            rendered = format_findings(result.findings)
            self.assertEqual(result.scanned_files, 1)
            self.assertIn("settings.txt: github-token", rendered)
            self.assertNotIn(value, rendered)


if __name__ == "__main__":
    unittest.main()
