import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from publication_gate import DEFAULT_MANIFEST, evaluate_manifest, load_manifest, main

def ready_manifest():
    return {
        "schema_version": 1, "case_reference": "opaque-case-ref-001",
        "engagement_type": "client_engagement",
        "attribution": {"mode": "anonymized", "case_publication_authorized": True, "client_name_included": False, "client_name_authorized": False, "logo_included": False, "logo_authorized": False},
        "authorization_reference": "opaque-authorization-ref-001",
        "claims": [{"id": "scope-001", "kind": "scope", "evidence_ref": "opaque-evidence-ref-001", "evidence_verified": True, "publication_authorized": True}],
        "data_review": {"source_data_authorized": True, "personal_data_review_complete": True, "confidentiality_review_complete": True, "third_party_assets_review_complete": True},
    }

class PublicationGateTests(unittest.TestCase):
    def test_complete_declarations_are_ready_only_for_human_review(self):
        result = evaluate_manifest(ready_manifest())
        self.assertEqual(result.status, "READY_FOR_HUMAN_REVIEW")
        self.assertEqual(result.finding_codes, ())
        self.assertFalse(result.to_dict()["publish_authorized"])
        self.assertTrue(result.to_dict()["human_review_required"])

    def test_repository_sample_is_intentionally_blocked(self):
        result = evaluate_manifest(load_manifest(DEFAULT_MANIFEST))
        self.assertEqual(result.status, "BLOCKED")
        self.assertIn("no-claims-declared", result.finding_codes)
        self.assertIn("case-publication-not-authorized", result.finding_codes)

    def test_non_object_manifest_fails_closed(self):
        result = evaluate_manifest(["not", "an", "object"])
        self.assertEqual(result.finding_codes, ("invalid-manifest",))

    def test_named_attribution_requires_name_permission(self):
        manifest = ready_manifest()
        manifest["attribution"].update({"mode": "named", "client_name_included": True, "client_name_authorized": False})
        self.assertIn("client-name-not-authorized", evaluate_manifest(manifest).finding_codes)

    def test_anonymized_attribution_rejects_included_name(self):
        manifest = ready_manifest()
        manifest["attribution"].update({"client_name_included": True, "client_name_authorized": True})
        self.assertIn("anonymized-case-includes-client-name", evaluate_manifest(manifest).finding_codes)

    def test_logo_requires_explicit_permission(self):
        manifest = ready_manifest()
        manifest["attribution"].update({"logo_included": True, "logo_authorized": False})
        self.assertIn("logo-not-authorized", evaluate_manifest(manifest).finding_codes)

    def test_missing_claim_evidence_blocks(self):
        manifest = ready_manifest()
        manifest["claims"][0].update({"evidence_ref": "", "evidence_verified": False})
        codes = evaluate_manifest(manifest).finding_codes
        self.assertIn("claim-evidence-reference-missing", codes)
        self.assertIn("claim-evidence-unverified", codes)

    def test_claim_requires_publication_permission(self):
        manifest = ready_manifest()
        manifest["claims"][0]["publication_authorized"] = False
        self.assertIn("claim-not-authorized-for-publication", evaluate_manifest(manifest).finding_codes)

    def test_duplicate_claim_ids_block(self):
        manifest = ready_manifest()
        manifest["claims"].append(dict(manifest["claims"][0]))
        self.assertIn("duplicate-claim-id", evaluate_manifest(manifest).finding_codes)

    def test_incomplete_data_review_blocks(self):
        manifest = ready_manifest()
        manifest["data_review"]["confidentiality_review_complete"] = False
        self.assertIn("data-review-incomplete-confidentiality_review_complete", evaluate_manifest(manifest).finding_codes)

    def test_non_client_material_is_rejected(self):
        manifest = ready_manifest()
        manifest["engagement_type"] = "independent_demo"
        self.assertIn("unsupported-engagement-type", evaluate_manifest(manifest).finding_codes)

    def test_unknown_fields_are_rejected_without_echoing_values(self):
        manifest = ready_manifest()
        manifest["client_name"] = "synthetic-private-value"
        result = evaluate_manifest(manifest)
        self.assertIn("unknown-field", result.finding_codes)
        self.assertNotIn("synthetic-private-value", json.dumps(result.to_dict()))

    def test_unhashable_mode_and_claim_kind_fail_closed(self):
        manifest = ready_manifest()
        manifest["attribution"]["mode"] = []
        manifest["claims"][0]["kind"] = []
        codes = evaluate_manifest(manifest).finding_codes
        self.assertIn("invalid-attribution-mode", codes)
        self.assertIn("invalid-claim-kind", codes)

    def test_boolean_is_not_schema_version(self):
        manifest = ready_manifest()
        manifest["schema_version"] = True
        self.assertIn("unsupported-schema-version", evaluate_manifest(manifest).finding_codes)

    def test_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text('{"schema_version": 1, "schema_version": 1}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_manifest(path)

    def test_cli_sample_reports_blocked(self):
        output = StringIO()
        with redirect_stdout(output):
            code = main([str(DEFAULT_MANIFEST)])
        self.assertEqual(code, 0)
        self.assertIn('"status": "BLOCKED"', output.getvalue())
        self.assertIn('"publish_authorized": false', output.getvalue())

    def test_cli_require_ready_fails_for_blocked_sample(self):
        with redirect_stdout(StringIO()):
            self.assertEqual(main([str(DEFAULT_MANIFEST), "--require-ready"]), 2)

    def test_cli_require_ready_accepts_complete_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ready.json"
            path.write_text(json.dumps(ready_manifest()), encoding="utf-8")
            with redirect_stdout(StringIO()):
                self.assertEqual(main([str(path), "--require-ready"]), 0)

if __name__ == "__main__":
    unittest.main()
