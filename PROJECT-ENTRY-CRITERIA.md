# Project Entry Criteria

This document defines the minimum publication standard for projects added to this portfolio.

## 1. Classify the project honestly

Every project must use one status:

- **CONCEPT** — problem and proposed approach are documented; no working implementation is available.
- **DEMO** — a limited, runnable or explorable example demonstrates a specific capability. Its boundaries are explicit.
- **PROTOTYPE** — an integrated early version demonstrates a broader workflow, but still requires meaningful development or validation.
- **IMPLEMENTED** — deployed or operating in a defined environment, with scope and evidence documented. This label alone does not mean production-ready, secure, compliant, or commercially ready.

Do not assign a more advanced status based on ambition or appearance. Reassess status when implementation changes.

## 2. Minimum documentation

Each project must have a README based on `PROJECT-README-TEMPLATE.md`. At minimum, explain:

- What the project is and which problem it addresses.
- Whether it is independent work, a reusable template, a fictional scenario, or an authorized client engagement.
- What is included and excluded.
- Technologies and exact requirements.
- How to run or explore it, or why it cannot yet be run.
- Tests and available evidence.
- Data provenance, privacy considerations, safety boundaries, and limitations.
- Next steps.

## 3. Minimum implementation evidence

For a runnable DEMO or PROTOTYPE:

- Source files must be present and linked from the README.
- A new visitor must have a reproducible run or exploration path.
- Sample data must be synthetic, public, or explicitly authorized.
- Automated tests should cover core behavior where practical; otherwise document the manual verification method and its limits.
- Do not claim tests pass unless the relevant test command or CI run was actually executed and succeeded.
- Do not include secrets, credentials, private customer records, or unauthorized third-party materials.

For CONCEPT entries, clearly label the entry as non-executable and do not imply that source code or a working product exists.

## 4. Client work and case studies

- Publish client identity, logo, materials, metrics, testimonials, and outcomes only with appropriate authorization.
- If confidentiality applies, anonymize only to the level the client permits.
- Never convert an independent demo or fictional scenario into a claimed client delivery.
- Keep independently developed examples in the relevant portfolio category, not in Client Demos.

## 5. Quality gate before publication

Before merging or publishing a project, check:

1. README follows the template and all placeholders are removed.
2. Status matches the actual implementation.
3. Setup and run commands match the repository files.
4. Tests and outputs are reproducible.
5. Links and paths resolve.
6. Sample data and claims have a clear provenance.
7. Limitations and exclusions are visible.
8. No secrets, credentials, private customer records, or unauthorized third-party materials are present.
9. Run `python scripts/check_public_content.py` and treat any finding as a publication blocker. The check reports paths and rule IDs only; it never prints matched values.

The public-content check is heuristic. It scans tracked UTF-8 files in the current checkout, not Git history, binary files, every possible credential format, or all forms of confidential information. It does not replace human review or credential rotation.

## 6. Maintenance

When a project changes, update its README, tests, status, and category index in the same change where practical. Remove stale instructions and links. Keep evidence current; historical CI success is not proof that a later revision still passes.
