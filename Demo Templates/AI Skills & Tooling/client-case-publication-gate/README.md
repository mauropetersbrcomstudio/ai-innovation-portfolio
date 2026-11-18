# Client Case Publication Gate

**Status: DEMO**

## Overview

A deterministic, standard-library Python preflight that checks whether a client-case publication manifest contains the required authorization declarations, claim-level evidence references, attribution permissions, and data-review declarations. It returns only a status and finding codes. It never authorizes publication.

This is an independently developed reusable template. It is not a client case, does not describe a client engagement, and contains no client identity or outcome.

## Problem and context

A case study should not enter the public portfolio until the proposed claims, evidence, attribution, source data, and disclosure permissions have been reviewed. This utility makes missing declarations visible before a human reviewer inspects the underlying records.

## Scope

### Included

- Strict versioned JSON manifest validation.
- Opaque case, authorization, and evidence references.
- Claim-level evidence verification and publication-authorization declarations.
- Named versus anonymized attribution checks.
- Separate client-name and logo permission checks.
- Required source-data, personal-data, confidentiality, and third-party-asset review declarations.
- Fail-closed finding codes without echoing manifest values.
- Optional `--require-ready` exit behavior for a release preflight.

### Not included

- Authentication of clients, reviewers, or approvers.
- Inspection or verification of underlying evidence documents.
- Legal advice or determination of publication rights.
- Storage of client names, claim text, confidential documents, or personal data.
- Publishing, deployment, or modification of the `client-demos/` category.

## How it works

1. Load a JSON manifest using schema version 1.
2. Validate the engagement type and opaque references.
3. Check attribution, client-name, and logo permissions independently.
4. Check each claim for a unique identifier, evidence reference, verification declaration, and publication authorization declaration.
5. Check the four required data-review declarations.
6. Return `BLOCKED` when any declaration is missing, malformed, duplicated, or false. Otherwise return `READY_FOR_HUMAN_REVIEW`.

Both outcomes include `publish_authorized: false` and `human_review_required: true`. The tool trusts declarations supplied in the manifest; it does not prove that the referenced evidence or authorization exists.

## Technologies and requirements

- Python 3.10+
- Python standard library only
- No network access, external service, account, or third-party package required

## Run locally

From this project directory:

```bash
python publication_gate.py sample_manifest.json
```

The included sample is intentionally incomplete and should report `BLOCKED`. It is a synthetic intake checklist, not a fictional client story or evidence of an engagement.

For a manifest that must be complete enough to enter human review:

```bash
python publication_gate.py path/to/authorized-manifest.json --require-ready
```

The command exits with code 2 when the manifest is blocked. A zero exit code means only that the declarations passed this preflight; it is not publication approval.

## Manifest contract

See [sample_manifest.json](./sample_manifest.json) for the exact schema shape. Use opaque, non-sensitive references rather than names, statements, document contents, or client-specific paths. Each claim must carry its own evidence reference, verification declaration, and publication-authorization declaration.

The manifest must not contain client names, logos, claim text, personal records, confidential information, credentials, or copies of evidence. Keep source evidence in its authorized system of record and have a responsible human inspect it separately.

## Tests and quality checks

Run:

```bash
python -m unittest discover -s tests -v
```

The tests cover complete and incomplete declarations, named/anonymized attribution, logo permissions, missing and duplicate evidence declarations, data-review gates, unsupported engagement types, unknown fields, duplicate JSON keys, output redaction, and CLI exit behavior.

The private internal validation materials run the unit tests and the intentionally blocked sample command. Portfolio-wide validation also discovers this test suite and checks the project README and category indexes.

## Data, privacy, and safety

The sample manifest contains synthetic placeholders only. The tool does not read evidence references, access client systems, transmit data, or write a publication artifact. Its output omits case references, authorization references, evidence references, and any unrecognized values.

A `READY_FOR_HUMAN_REVIEW` result is not proof of consent, legal authorization, factual accuracy, confidentiality clearance, or client approval. A responsible human must verify the original records and the exact permitted disclosure before any case is added to the public repository.

## Limitations

- This is a deterministic checklist validator, not an authorization or legal-compliance engine.
- Boolean declarations and opaque references are trusted inputs and can be false.
- Evidence references are not dereferenced or cryptographically verified.
- No identity, approval signature, timestamp authority, or audit trail is provided.
- The utility does not scan the evidence store for secrets or personal data.
- It does not publish or modify files under `client-demos/`.

## Next steps

- Define a controlled evidence register outside the public repository.
- Have the responsible client contact confirm permitted attribution and claim scope.
- Add a human review record in the authorized system of record before preparing a public case.

## Evidence and provenance

- **Project type:** Independent reusable demonstration.
- **Data:** Synthetic, intentionally incomplete sample manifest.
- **Client disclosure:** No client engagement or case is represented.
- **Status:** DEMO; local deterministic preflight only.
