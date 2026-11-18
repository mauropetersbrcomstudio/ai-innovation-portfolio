# Portfolio Delivery Roadmap — Essential Backlog

**Objective:** make the existing GitHub portfolio coherent, reliable, easy to demonstrate, and ready to receive substantiated client cases.

**Only deliverable:** the central GitHub repository and its eight agreed folders. No separate website, domain, hosting, or deployment.

**Execution rule:** stabilize and present what already exists before creating anything new. Do not add projects merely to increase the project count.

## Repository structure

The agreed structure has two top-level areas:

- `Client Demos/` — independent area reserved for substantiated, authorized client cases.
- `Demo Templates/` — the single reusable demonstration library, organized into six technology categories:
  1. AI Agents & Agentic Systems
  2. AI Automation & Workflows
  3. AI Skills & Tooling
  4. AI Product Development
  5. Web Applications & SaaS
  6. Marketing Intelligence & Business Automation

## Current portfolio inventory

The repository already contains working demonstrations across the eight areas, including:

- Agent and workflow demonstrations, including bounded execution, orchestration, coordination, governance, state, observability, and recovery.
- Lead and invoice intake pipelines, the Resumable Intake Operations Hub, and the Operations Review Workspace.
- Reusable demo templates for operations intake, CRM lead qualification, customer support, and internal knowledge assistance.
- Reusable skills and tools for brief-to-task conversion, CSV quality and normalization, document extraction, JSON validation, knowledge retrieval, and agent tooling.
- SME Workflow Opportunity Mapper and SME KPI Workspace.
- Campaign Performance Analyzer, Marketing Analytics Pipeline, and Campaign Launch QA & UTM Builder.

The root README and individual project READMEs are the authoritative project catalogue and implementation instructions. The [Selected Demo Guide](./DEMO-GUIDE.md) provides a consolidated presentation path for the initial three demos. The [cross-project test guide](./tests/README.md) explains the browser and CI test coverage. Sample records are synthetic unless explicitly identified otherwise. Existing demonstrations must not be described as client engagements or production systems without evidence.

## Essential backlog

### P0 — Portfolio integrity and navigation

- [x] Reconcile the root README, category indexes, and this roadmap against the actual repository tree.
- [x] Re-verify all relative links in the root README against the current repository tree: 50 local links resolve, with zero broken targets.
- [x] Reconcile project documentation coverage against the current tree: 37 project directories have project READMEs, and the two top-level areas and six category indexes have category indexes.
- [x] Retain the original audit and correction record, including the review of status labels, run instructions, dependencies, tests, limitations, and essential documentation.
- [x] Confirm Portfolio Quality Gate succeeded for the backlog simplification commit `5a7359d10b247096ba00ce90123e646fde01c152` (run [44228054863](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44228054863)).
- [x] Confirm the quality gate for subsequent documentation corrections passed (run [44229011568](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44229011568), commit `6164850df8283f49a56ee89116c9cfa536a1b899`).

**Exit criteria:** the repository catalogue matches the files that exist; documented commands and links are usable; applicable CI checks pass.

**Initial audit snapshot (2026-11-18):** 201 tracked files and 45 README files were recorded: 36 project READMEs, six category indexes, and the root README. At that point, the root index and category indexes covered the 36 project directories, with no broken local links. The initial pass corrected two non-standard status labels, repaired one malformed root-index row, and documented component test commands for the operations-intake template.

**Current reconciliation (2026-11-18):** the recursive Git tree contains 215 tracked files and 47 README files: 37 project READMEs, nine category/test indexes, and the root README. All eight agreed portfolio folders have their category README; the additional `tests/README.md` is a cross-project test index. The root README contains 50 relative links; all 50 resolve to tracked files or repository directories. The historical 201/45/36/48 figures are retained above only as the initial audit snapshot and are not presented as current counts.

### P1 — Demonstration readiness of existing projects

- [x] Select three existing demos for first presentation: **Operations Review Workspace**, **Campaign Performance Analyzer**, and **Campaign Launch QA & UTM Builder**. These cover an interactive workflow and two complementary marketing use cases without new implementation.
- [x] Reassess the selection after reproducibility checks; no blocker justified changing the three-demo shortlist.
- [x] Verify automated test coverage and documented sample commands for each selected demo through GitHub Actions.
- [x] Add a headless Chromium workflow for the Operations Review Workspace and Campaign Performance Analyzer, using synthetic data and loopback-only services.
- [x] Verify that the Operations Review Workspace browser test checks decision persistence after a full page reload.
- [x] Confirm the cross-project browser workflow passed and record [run 44235238035](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44235238035).
- [x] Add 375-pixel responsive smoke checks for both interactive demos, including layout structure and page-level horizontal overflow.
- [x] Verify Campaign Performance Analyzer print-media behavior: executive report visible, dashboard masthead and print control hidden.
- [x] Resolve the mobile report-table overflow found by the new browser check and confirm the final browser workflow passed (run `44242143780`).
- [ ] Execute each demo interactively on a local machine and verify the complete visual/user flow; CI checks do not establish this.
- [x] Ensure synthetic sample data, expected outputs, limitations, and a short demonstration path are clear.
- [x] Resolve the test-hygiene warning found during the automated test run; no test blocker remained.
- [x] Publish the [Selected Demo Guide](./DEMO-GUIDE.md) with reproducible commands, presentation sequence, automated checks, and explicit limitations.
- [x] Add a cross-project test index in [tests/README.md](./tests/README.md).

**Exit criteria:** each selected demo can be explained and reproduced from its README, with test evidence and limitations visible. Desktop, 375-pixel responsive, and print-media smoke checks are passing; human-led local presentation review remains pending.

**Verification evidence (2026-11-18):**
- [Portfolio Quality Gate](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44242143819): passed; catalogue validator covered 36 project READMEs, eight category indexes, root index coverage, local links, status labels, and documentation requirements; 224 Python tests passed across 35 suites.
- [Portfolio Demo Browser Tests](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44242143780): passed; Operations Review Workspace recorded a synthetic decision that persisted after reload and passed a 375-pixel single-column layout check. Campaign Performance Analyzer imported the sample CSV, filtered Search, rendered the executive report, passed a 375-pixel layout check, and passed print-media assertions.
- [Campaign Performance Analyzer Tests](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44242143783): passed; Python and browser-logic tests plus sample CLI output checks.
- [Marketing Analytics Pipeline Tests](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44242144371): passed.
- [Operations Review Workspace Tests](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44241490459): passed; six integration tests.
- [Campaign Performance Analyzer Tests](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44235237936): passed; six Python tests and the sample CLI output checks passed.
- [Portfolio Quality Gate](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44229011568): catalogue validator passed; 34 Python test suites and 224 tests passed.
- [Operations Review Workspace Tests](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44228923871): six integration tests passed, covering the local HTTP adapter, workflow state, and review-decision flow.
- [Campaign Performance Analyzer Tests](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44228923767): six Python tests and 15 browser-logic tests passed; the sample CLI run generated all three expected non-empty reports.
- [Campaign Launch QA Tests](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44229011729): nine Python tests passed; the sample CLI run generated the approved, exception, and summary files.

The first browser runs exposed two real issues: the test expected two Search campaigns although the synthetic fixture contains one, and the dashboard's JavaScript referenced an executive-report section that was absent from the HTML. The expected count was corrected, the missing report section and Print / Save as PDF control were restored, and the final browser run above passed. The earlier failed runs remain visible in GitHub Actions and are not counted as successful evidence.

The cross-project Chromium workflow now checks persisted review state, 375-pixel mobile layout behavior, and the Campaign Performance Analyzer's print-media rules. The responsive run exposed a five-pixel page-level overflow caused by the daily-evolution table in the generated report; the table is now contained in a horizontally scrollable region. The final browser run above passed. The dashboard and workspace still require human-led local presentation review. Automated browser checks do not establish complete visual quality on every device or browser.

### P1 — Reusable foundation hardening: Agent Observability

- [x] Review the structured JSONL logger's sensitive-key matching rather than treating its original substring checks as comprehensive.
- [x] Normalize common key styles, including camelCase, spaces, dots, hyphens, and case differences, before matching recognized credential/session markers.
- [x] Avoid broad substring matches that would redact unrelated names such as `tokenizer` and `secretary`.
- [x] Reject non-string severity values with a clear validation error.
- [x] Add regression coverage for sensitive key variants, safe-name controls, and invalid severity types.
- [x] Clarify in the project and category READMEs that redaction is key-name based and does not inspect arbitrary free-text values.
- [x] Confirm [Agent Observability Tests — run 44247820974](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44247820974): 9 tests passed.
- [x] Confirm [Portfolio Quality Gate — run 44247821005](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44247821005): catalogue validation passed and 226 Python tests passed across 35 suites.

**Boundary:** this remains a limited DEMO safeguard. It is not a data-loss-prevention system, cannot detect secrets embedded in free text or unrecognized fields, and does not provide encrypted or tamper-proof audit storage.

### P1 — Agent Tool Gateway and Security & Governance consistency

- [x] Compare the gateway's caller-supplied role/approval checks with the separate deny-by-default policy engine; document that the gateway markers are not trusted identity or approval evidence.
- [x] Ensure the gateway audit trail records invocation outcomes without copying potentially sensitive handler output.
- [x] Count a handler invocation attempt before entering application code, so a handler that partially acts and then raises cannot be retried repeatedly in the same session beyond its configured limit.
- [x] Reject non-string and otherwise malformed risk values in both policy manifests and authorization requests without leaking a Python type error.
- [x] Add regression tests for output-free audit records, failed-handler attempt limits, and malformed risk values.
- [x] Clarify the host integration sequence in both project READMEs and the category index: authenticate and authorize first, then dispatch only when the policy decision is allowed.
- [x] Confirm a concrete integration gap: the existing Governed Agent Execution demo did not call the separate deny-by-default Agent Security & Governance engine before gateway dispatch.
- [x] Add a read-only gateway tool-spec lookup so the host can check dispatch-contract alignment without accessing gateway internals.
- [x] Add `host_adapter.py` to the Governed Agent Execution demo. It accepts a host-authenticated `Principal`, calls the policy engine first, delegates approval verification to an injected verifier, and dispatches only after an allowed decision.
- [x] Derive the gateway role and approval marker from the allowed policy decision rather than accepting gateway approval markers directly from the request.
- [x] Reject policy/gateway approval mismatches, incompatible role allowlists, invalid session IDs, and attempts to reuse a session across subjects or roles.
- [x] Preserve per-session invocation counts across calls made through the same host adapter and block reuse of consumed approval IDs within that host instance.
- [x] Add regression tests for missing/unverified approval, unauthenticated principals, role and approval configuration mismatches, session binding, quota persistence, approval replay, invalid arguments, and audit-output exclusion.
- [x] Extend the dedicated Governed Agent Execution workflow to run when Agent Security & Governance changes.

**Boundary:** the adapter does not authenticate users or approvers; the host must supply a trusted principal and an authoritative approval verifier. Session bindings, invocation counts, consumed approval IDs, and audit events are in memory, reset on process restart, and are not concurrency-safe or shared across processes. Handler effects are not transactional, and audit records are not durable or tamper-evident. The gateway, policy engine, and host adapter remain DEMOs.

**Verification evidence (2026-11-18):**
- [Governed Agent Execution Tests — run 44264628146](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44264628146): 18 tests passed, including 14 new host-adapter regression tests.
- [Portfolio Quality Gate — run 44264628058](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44264628058): portfolio validation passed for 36 project READMEs, eight category indexes, and root index coverage; 244 Python tests passed across 35 suites.

The initial CI attempt caught a missing `ToolSpec` import in the demo runner. It was corrected in commit [c376b19](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/commit/c376b19c16224f35a8abd0fdb0eb66657ecf8fb5), and the final dedicated and portfolio-wide runs above passed. The initial failed runs remain visible in Actions history.

**Verification evidence (2026-11-18):**
- [Agent Tool Gateway Tests — run 44255991317](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44255991317): 10 tests passed, including output-free audit records and failed-handler attempt limits.
- [Agent Security Governance Tests — run 44255991438](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44255991438): 11 tests passed, including malformed risk values in requests and policy manifests.
- [Portfolio Quality Gate — run 44255991376](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44255991376): portfolio validator passed for 36 project READMEs and eight category indexes; 230 Python tests passed across 35 suites.

### P1 — Defensive policy and dispatch contract snapshots

- [x] Copy registered tool input schemas so caller-owned dictionaries cannot change gateway validation after registration.
- [x] Return defensive copies from the gateway's host-facing tool-spec lookup.
- [x] Retain the validated security policy as an internal normalized snapshot and expose only defensive copies.
- [x] Reject malformed gateway registration contracts, including invalid schema containers and boolean/non-positive invocation limits.
- [x] Add regression tests for source-schema mutation, inspected-spec mutation, source-policy mutation, and policy-snapshot mutation.
- [x] Update the Agent Tool Gateway, Agent Security & Governance, and Governed Agent Execution documentation plus both relevant category indexes.
- [x] Confirm [Agent Tool Gateway Tests — run 44272797015](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44272797015): 13 tests passed.
- [x] Confirm [Agent Security Governance Tests — run 44272797055](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44272797055): 13 tests passed.
- [x] Confirm [Governed Agent Execution Tests — run 44272829622](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44272829622): 18 tests passed.
- [x] Confirm [Portfolio Quality Gate — run 44272829717](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44272829717): catalogue validation passed and 249 Python tests passed across 35 suites.

**Boundary:** defensive copies protect against accidental mutation through ordinary public references; they are not a sandbox against malicious code running inside the same Python process or code using introspection. Policy and gateway state remain in memory, the gateway supports only a small schema subset, and neither component provides production identity, approval, concurrency, or durable audit controls. Both remain DEMOs.

### P1 — Public repository content hygiene

- [x] Add a standard-library scanner for Git-tracked UTF-8 files that flags selected high-confidence credential formats and non-example environment-file names.
- [x] Ensure findings report only repository paths and rule identifiers; matched values are never printed.
- [x] Add regression tests for provider-token formats, private-key markers, credential-bearing URLs, environment-file names, safe placeholders, binary/oversized-file handling, and diagnostic redaction.
- [x] Run the scanner before catalogue validation and Python tests in the Portfolio Quality Gate.
- [x] Document coverage and limitations in the root README, Project Entry Criteria, cross-project test guide, and AI Skills & Tooling integration notes.

**Boundary:** this is a heuristic guard, not a comprehensive secret scanner or confidentiality review. It scans the current Git-tracked checkout; it does not inspect Git history, binary/oversized/non-UTF-8 files, symlinks, every credential format, or all forms of confidential/client information. A clean result does not replace human review, access controls, or credential rotation.

**Verification evidence (2026-11-18):**
- [Portfolio Quality Gate — run 44281968643](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44281968643): passed; heuristic scan checked 210 tracked UTF-8 text files with zero skipped files and no reported findings; catalogue validation passed for 36 project READMEs and eight category indexes; 257 Python tests passed across 35 suites.
- [Campaign Launch QA Tests — run 44281968628](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44281968628): passed; nine unit tests and sample-output checks passed.
- The first scan run flagged a credential-shaped URL used as a negative test fixture, not a real credential. The fixture was rewritten to assemble the URL from separate strings; the final repository scan and workflow then passed.

### P2 preparation — Client Case Publication Gate (template only)

- [x] Add a reusable, standard-library preflight under the six technology categories without creating or implying a client case.
- [x] Require an opaque case reference, publication authorization reference, explicit attribution permissions, claim-level evidence declarations, and data-review declarations.
- [x] Fail closed on missing, malformed, duplicated, unverified, or unauthorized manifest declarations.
- [x] Keep the output limited to status and finding codes; never echo client names, claim text, evidence references, or matched values.
- [x] Confirm the dedicated unit-test and sample-manifest workflow — [run 44298660386](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44298660386).
- [x] Confirm the portfolio-wide quality gate — [run 44298765167](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44298765167).

**Verification evidence (2026-11-18):**
- [Client Case Publication Gate Tests](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44298660386): passed; 18 unit tests and the intentionally blocked synthetic sample command completed successfully.
- [Portfolio Quality Gate](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44298765167): passed; the heuristic scanner checked 215 tracked UTF-8 text files with zero skips and no reported findings; catalogue validation covered 37 project READMEs and eight category indexes; 275 Python tests passed across 36 suites.

The first quality-gate attempt on the implementation commit failed because a direct project-directory link in the Client Demos category index was interpreted by the catalogue validator as a Client Demos project. The cross-reference was changed to the Demo Templates category index, preserving category separation; the final quality gate above passed.

**Boundary:** the sample is a synthetic, intentionally blocked intake manifest. The tool does not inspect evidence, authenticate a client or approver, verify legal permissions, or authorize publication. A successful preflight means only that the manifest declarations are complete enough for human review. `client-demos/` remains reserved for real, substantiated, authorized cases.

### P2 — Client Demos, only when source material is supplied

- [ ] Convert user-provided case briefs into client-specific demonstrations only after the facts, assets, and publication authorization are supplied.
- [ ] Separate verified historical work from newly created illustrative demos.
- [ ] Do not invent client identities, engagements, outcomes, metrics, testimonials, logos, or prior deliveries.

**Exit criteria:** every published client claim is supported by supplied evidence and authorized for publication.

## Explicitly deferred — not part of the essential backlog

- New agents, skills, workflow examples, or standalone utilities that duplicate existing capabilities.
- A new Marketing Operations Workspace or another dashboard that merely combines existing marketing demos.
- Generalizing the Operations Review Workspace, adding more sample scenarios, or building a broader product platform.
- Real identity-provider integration, multi-user authentication, role enforcement, external actions, or production hardening.
- SaaS conversion, cloud hosting, public deployment, a separate website, domain, or paid services.
- Additional integrations with CRM, advertising, analytics, accounting, email, or payment platforms.

These items may be reconsidered only when a concrete client requirement or demonstrated gap justifies the cost and scope.

## Quality and integrity gates

- Status labels must match observable evidence: CONCEPT, DEMO, PROTOTYPE, or IMPLEMENTED.
- A passing test suite does not establish production readiness.
- Document security and operational limitations; do not imply authenticated identity, tamper-proof audit, exactly-once external effects, or autonomous LLM behavior where these are not implemented.
- Preserve existing repository work and unrelated projects.
- Use synthetic data unless the user explicitly authorizes other data for the intended use.
- Keep the implementation reproducible and avoid unnecessary dependencies.

## Working rule

**P0 is complete. P1 automated verification, browser end-to-end checks, and the public-content heuristic gate are passing; the trusted-host adapter demonstrates the authorization-to-dispatch boundary. Human-led local presentation review remains outstanding.** Do not create a client case until a source brief, supporting evidence, and publication authorization are supplied. Defer additional independent projects unless a concrete gap justifies them.
