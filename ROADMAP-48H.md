# Portfolio Delivery Roadmap — Essential Backlog

**Objective:** make the existing GitHub portfolio coherent, reliable, easy to demonstrate, and ready to receive substantiated client cases.

**Only deliverable:** the central GitHub repository and its eight agreed folders. No separate website, domain, hosting, or deployment.

**Execution rule:** stabilize and present what already exists before creating anything new. Do not add projects merely to increase the project count.

## Repository structure

The eight agreed areas remain unchanged:

1. Client Demos
2. Demo Templates
3. AI Agents & Agentic Systems
4. AI Automation & Workflows
5. AI Skills & Tooling
6. AI Product Development
7. Web Applications & SaaS
8. Marketing Intelligence & Business Automation

## Current portfolio inventory

The repository already contains working demonstrations across the eight areas, including:

- Agent and workflow demonstrations, including bounded execution, orchestration, coordination, governance, state, observability, and recovery.
- Lead and invoice intake pipelines, the Resumable Intake Operations Hub, and the Operations Review Workspace.
- Reusable demo templates for operations intake, CRM lead qualification, customer support, and internal knowledge assistance.
- Reusable skills and tools for brief-to-task conversion, CSV quality and normalization, document extraction, JSON validation, knowledge retrieval, and agent tooling.
- SME Workflow Opportunity Mapper and SME KPI Workspace.
- Campaign Performance Analyzer, Marketing Analytics Pipeline, and Campaign Launch QA & UTM Builder.

The root README and individual project READMEs are the authoritative project catalogue and implementation instructions. Sample records are synthetic unless explicitly identified otherwise. Existing demonstrations must not be described as client engagements or production systems without evidence.

## Essential backlog

### P0 — Portfolio integrity and navigation

- [x] Reconcile the root README, category indexes, and this roadmap against the actual repository tree.
- [x] Verify that all 48 relative links in the root README resolve to existing repository paths (repository-tree audit, 2026-11-18).
- [x] Audit all 36 project READMEs for status, run instructions, dependencies, tests, and limitations.
- [x] Correct factual inconsistencies and missing essential documentation found in the audit.
- [x] Confirm Portfolio Quality Gate succeeded for the backlog simplification commit `5a7359d10b247096ba00ce90123e646fde01c152` (run `44228054863`).
- [x] Confirm the quality gate for subsequent documentation corrections passed (run [44229011568](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44229011568), commit `6164850df8283f49a56ee89116c9cfa536a1b899`).

**Exit criteria:** the repository catalogue matches the files that exist; documented commands and links are usable; applicable CI checks pass.

**Audit snapshot (2026-11-18):** 201 tracked files and 45 README files were found: 36 project READMEs, eight category indexes, and the root README. The root index and category indexes cover all 36 project directories; no broken local links were found. This pass corrects two non-standard status labels, repairs one malformed root-index row, and documents the component test commands for the operations-intake template.

### P1 — Demonstration readiness of existing projects

- [x] Select three existing demos for first presentation: **Operations Review Workspace**, **Campaign Performance Analyzer**, and **Campaign Launch QA & UTM Builder**. These cover an interactive workflow and two complementary marketing use cases without new implementation.
- [x] Reassess the selection after reproducibility checks; no blocker justified changing the three-demo shortlist.
- [x] Verify each selected demo from its documented setup through its primary user flow using its existing tests and available execution environment.
- [x] Ensure synthetic sample data, expected outputs, limitations, and a short demonstration path are clear.
- [x] Resolve the test-hygiene warning found during the run; no functional blocker remained in the selected demo paths.

**Exit criteria:** each selected demo can be explained and reproduced from its README, with test evidence and limitations visible.

**Verification evidence (2026-11-18):**
- [Portfolio Quality Gate](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44229011568): catalogue validator passed; 34 Python test suites and 224 tests passed.
- [Operations Review Workspace Tests](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44228923871): six integration tests passed, covering the local HTTP adapter, workflow state, and review-decision flow.
- [Campaign Performance Analyzer Tests](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44228923767): six Python tests and 15 browser-logic tests passed; the sample CLI run generated all three expected non-empty reports.
- [Campaign Launch QA Tests](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44229011729): nine Python tests passed; the sample CLI run generated the approved, exception, and summary files.

The dashboard and workspace were not subjected to full browser-driven end-to-end automation. Their documented browser paths remain subject to manual presentation review; the automated evidence covers the underlying logic, HTTP integration, and sample CLI outputs.

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

**P0 and P1 are complete.** Do not create a client case until a source brief, supporting evidence, and publication authorization are supplied. Defer additional independent projects unless a concrete gap justifies them.
