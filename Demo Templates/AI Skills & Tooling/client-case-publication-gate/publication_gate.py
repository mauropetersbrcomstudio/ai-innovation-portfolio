#!/usr/bin/env python3
"""Preflight client-case publication metadata without approving publication."""
from __future__ import annotations
import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_MANIFEST = ROOT / "sample_manifest.json"
ROOT_KEYS = {"schema_version", "case_reference", "engagement_type", "attribution", "authorization_reference", "claims", "data_review"}
ATTRIBUTION_KEYS = {"mode", "case_publication_authorized", "client_name_included", "client_name_authorized", "logo_included", "logo_authorized"}
CLAIM_KEYS = {"id", "kind", "evidence_ref", "evidence_verified", "publication_authorized"}
DATA_REVIEW_KEYS = {"source_data_authorized", "personal_data_review_complete", "confidentiality_review_complete", "third_party_assets_review_complete"}
CLAIM_KINDS = {"context", "scope", "role", "deliverable", "technology", "outcome", "metric", "testimonial"}

@dataclass(frozen=True)
class GateResult:
    status: str
    finding_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "decision_scope": "preflight_only", "publish_authorized": False, "human_review_required": True, "finding_codes": list(self.finding_codes)}

def _is_opaque_reference(value: Any, max_length: int = 120) -> bool:
    return isinstance(value, str) and bool(value.strip()) and len(value) <= max_length and all(ch.isprintable() for ch in value)

def _unknown_fields(value: dict[str, Any], allowed: set[str], findings: set[str]) -> None:
    if any(key not in allowed for key in value):
        findings.add("unknown-field")

def _require_true(value: dict[str, Any], key: str, code: str, findings: set[str]) -> None:
    item = value.get(key)
    if item is not True:
        findings.add(code if isinstance(item, bool) else f"{code}-invalid")

def evaluate_manifest(manifest: Any) -> GateResult:
    """Return a fail-closed result containing codes only, never source values."""
    findings: set[str] = set()
    if not isinstance(manifest, dict):
        return GateResult("BLOCKED", ("invalid-manifest",))
    _unknown_fields(manifest, ROOT_KEYS, findings)
    version = manifest.get("schema_version")
    if type(version) is not int or version != 1:
        findings.add("unsupported-schema-version")
    if not _is_opaque_reference(manifest.get("case_reference")):
        findings.add("missing-or-invalid-case-reference")
    if manifest.get("engagement_type") != "client_engagement":
        findings.add("unsupported-engagement-type")
    if not _is_opaque_reference(manifest.get("authorization_reference")):
        findings.add("missing-authorization-reference")

    attribution = manifest.get("attribution")
    if not isinstance(attribution, dict):
        findings.add("invalid-attribution")
    else:
        _unknown_fields(attribution, ATTRIBUTION_KEYS, findings)
        mode = attribution.get("mode")
        mode_valid = isinstance(mode, str) and mode in {"named", "anonymized"}
        if not mode_valid:
            findings.add("invalid-attribution-mode")
        _require_true(attribution, "case_publication_authorized", "case-publication-not-authorized", findings)
        name_included, name_authorized = attribution.get("client_name_included"), attribution.get("client_name_authorized")
        if type(name_included) is not bool or type(name_authorized) is not bool:
            findings.add("invalid-client-name-permission")
        elif name_included and not name_authorized:
            findings.add("client-name-not-authorized")
        elif mode_valid and mode == "anonymized" and name_included:
            findings.add("anonymized-case-includes-client-name")
        elif mode_valid and mode == "named" and not name_included:
            findings.add("named-case-missing-client-name")
        logo_included, logo_authorized = attribution.get("logo_included"), attribution.get("logo_authorized")
        if type(logo_included) is not bool or type(logo_authorized) is not bool:
            findings.add("invalid-logo-permission")
        elif logo_included and not logo_authorized:
            findings.add("logo-not-authorized")

    claims = manifest.get("claims")
    if not isinstance(claims, list):
        findings.add("invalid-claims")
    elif not claims:
        findings.add("no-claims-declared")
    else:
        seen_ids: set[str] = set()
        if len(claims) > 100:
            findings.add("too-many-claims")
        for claim in claims:
            if not isinstance(claim, dict):
                findings.add("invalid-claim")
                continue
            _unknown_fields(claim, CLAIM_KEYS, findings)
            claim_id = claim.get("id")
            if not _is_opaque_reference(claim_id, max_length=80):
                findings.add("invalid-claim-id")
            elif claim_id in seen_ids:
                findings.add("duplicate-claim-id")
            else:
                seen_ids.add(claim_id)
            kind = claim.get("kind")
            if not isinstance(kind, str) or kind not in CLAIM_KINDS:
                findings.add("invalid-claim-kind")
            if not _is_opaque_reference(claim.get("evidence_ref")):
                findings.add("claim-evidence-reference-missing")
            _require_true(claim, "evidence_verified", "claim-evidence-unverified", findings)
            _require_true(claim, "publication_authorized", "claim-not-authorized-for-publication", findings)

    data_review = manifest.get("data_review")
    if not isinstance(data_review, dict):
        findings.add("invalid-data-review")
    else:
        _unknown_fields(data_review, DATA_REVIEW_KEYS, findings)
        for key in sorted(DATA_REVIEW_KEYS):
            _require_true(data_review, key, f"data-review-incomplete-{key}", findings)
    ordered = tuple(sorted(findings))
    return GateResult("READY_FOR_HUMAN_REVIEW" if not ordered else "BLOCKED", ordered)

def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result

def load_manifest(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle, object_pairs_hook=_reject_duplicate_keys)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check client-case manifest completeness; this does not approve publication.")
    parser.add_argument("manifest", nargs="?", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--require-ready", action="store_true", help="return exit code 2 unless ready for human review")
    args = parser.parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        print("Manifest could not be read or parsed; source content is omitted.", file=sys.stderr)
        return 1
    result = evaluate_manifest(manifest)
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    if args.require_ready and result.status != "READY_FOR_HUMAN_REVIEW":
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
