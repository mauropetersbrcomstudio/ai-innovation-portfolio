# Portfolio Delivery Roadmap & Status

**Objective:** build a credible, navigable AI Innovation Portfolio in the central GitHub repository. The repository and its agreed folders are the only deliverable. No separate website, homepage, domain, hosting setup, or web deployment is in scope.

## Repository structure

The repository contains the eight agreed areas:

1. Client Demos
2. Demo Templates
3. AI Agents & Agentic Systems
4. AI Automation & Workflows
5. AI Skills & Tooling
6. AI Product Development
7. Web Applications & SaaS
8. Marketing Intelligence & Business Automation

Each category has a README describing its purpose and linking to its current contents. The root README is the repository-level index for working demonstrations and category navigation.

## Current working demonstrations

| Category | Project | Status |
|---|---|---|
| AI Agents & Agentic Systems | SME Operations Assistant | DEMO |
| AI Agents & Agentic Systems | SME Procurement Request Triage Agent | DEMO |
| AI Automation & Workflows | Lead Intake Pipeline | DEMO |
| Demo Templates | SME Customer Support Automation | DEMO |
| AI Skills & Tooling | Brief-to-Task Skill | DEMO |
| AI Product Development | SME Workflow Opportunity Mapper | DEMO |
| Web Applications & SaaS | SME KPI Workspace | DEMO |
| Marketing Intelligence & Business Automation | Campaign Performance Analyzer | DEMO |

These are independently developed demonstrations. Their sample records are synthetic; none is presented as a completed client engagement or a production deployment.

## Completed foundation

- [x] One central public GitHub repository.
- [x] Eight agreed portfolio categories.
- [x] Root README with category navigation and a working-demo index.
- [x] Category READMEs with scope and project links.
- [x] Project READMEs documenting status, setup, use, and limitations.
- [x] Executable demonstrations across the non-client categories.
- [x] Python unit tests for command-line demonstrations.
- [x] Automated portfolio quality workflow for Python test discovery.
- [x] Dedicated Node.js test workflow for the SME KPI Workspace.
- [x] Synthetic sample data and explicit boundaries for demonstrations.
- [x] No separate portfolio website or deployment in the current scope.

## Quality gates

- The Portfolio Quality Gate discovers and runs Python test suites in project folders.
- The SME KPI Workspace has a separate Node.js 20 test workflow.
- Project-specific workflows also run tests and, where configured, execute sample demonstrations.
- A project is labelled **DEMO** only when a limited working implementation and documented scope are present.
- A passing automated test suite is evidence for the tested behavior only; it does not establish production readiness.

## Remaining priorities

1. **Expand Demo Templates.** Add a second reusable template, with the Internal Knowledge Assistant as the next candidate. Keep the first version focused on approved-source retrieval, access boundaries, citations, and human escalation.
2. **Deepen selected demonstrations.** Add edge-case coverage, clearer sample outputs, and cross-project consistency where this improves the usefulness of the portfolio.
3. **Populate Client Demos when source material is supplied.** Add only real engagements with publication authorization. Do not invent client identities, project details, outcomes, metrics, or testimonials.
4. **Review the portfolio periodically.** Check links, commands, status labels, test workflows, and disclosure language after substantive changes.

## Project status definitions

- **CONCEPT** — an idea and proposed approach; no working implementation.
- **DEMO** — a limited working example of a specific capability.
- **PROTOTYPE** — an implemented proof of concept that is not production-ready.
- **IMPLEMENTED** — running in a defined environment, with scope and evidence documented.

## Non-negotiable boundaries

- Preserve existing repository work; do not overwrite unrelated projects.
- Use synthetic data or data explicitly authorized for publication and testing.
- Do not publish secrets, credentials, private customer records, or confidential client material.
- Do not represent independent work as client work.
- Do not claim results, integrations, tests, or production readiness without evidence.
- Keep the deliverable GitHub-only: no separate website, domain, hosting setup, or web deployment.
