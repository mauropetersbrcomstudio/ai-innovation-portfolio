# AI Innovation Portfolio

**Mauro Peters | AI Strategy, Product Development & Business Automation**

A portfolio of selected client work alongside independently developed AI demonstrations, reusable templates, tools, and product prototypes.

The repository brings together two kinds of work: projects carried out for real clients, presented in the Client Demos section, and solutions or building blocks developed independently to explore, demonstrate, or support the use of AI in business.

## Development strategy

The portfolio follows **Foundation First → Client Demos**. We will build reusable skills and tools first, then specialized agents, orchestrated workflows, and product components. Client-specific demonstrations will then assemble and configure these foundations against verified business requirements.

Read the [Portfolio Development Strategy v2.0](./PORTFOLIO-DEVELOPMENT-STRATEGY-v2.md) and the [Portfolio Delivery Roadmap](./ROADMAP-48H.md) for the execution sequence.

## Explore working demos

The six technology categories contain 37 independently developed demonstrations and reusable templates. Each project README records its status, setup instructions, dependencies, test commands, scope, and limitations. Every project is listed under exactly one category below.

| Demo | What it demonstrates | Status |
|---|---|---|
| [SME Operations Assistant](./Demo%20Templates/AI%20Agents%20%26%20Agentic%20Systems/sme-operations-assistant/) | Request classification, action allowlisting, escalation, and decision traces | DEMO |
| [SME Procurement Request Triage Agent](./Demo%20Templates/AI%20Agents%20%26%20Agentic%20Systems/sme-procurement-request-triage/) | Purchase-request validation, policy-based review routing, duplicate detection, and supplier checks | DEMO |
| [Bounded Support Workflow Agent](./Demo%20Templates/AI%20Agents%20%26%20Agentic%20Systems/bounded-support-workflow-agent/) | Composes workflow orchestration and allowlisted tools with approval pauses and bounded execution | DEMO |
| [Multi-Agent Request Review](./Demo%20Templates/AI%20Agents%20%26%20Agentic%20Systems/multi-agent-request-review/) | Bounded intake-to-review handoff with explicit routing and human escalation | DEMO |
| [Agent Platform Reference](./Demo%20Templates/AI%20Agents%20%26%20Agentic%20Systems/agent-platform-reference/) | Integrates orchestration, SQLite workflow state, and structured event logs | DEMO |
| [Governed Agent Execution](./Demo%20Templates/AI%20Agents%20%26%20Agentic%20Systems/governed-agent-execution/) | Integrates policy validation, role and approval gates, allowlisted tools, and bounded orchestration | DEMO |
| [Durable Workflow Runner](./Demo%20Templates/AI%20Agents%20%26%20Agentic%20Systems/durable-workflow-runner/) | Checkpoints sequential workflows in SQLite and resumes incomplete steps with idempotency keys | DEMO |
| [Agent Runtime Control Plane](./Demo%20Templates/AI%20Agents%20%26%20Agentic%20Systems/agent-runtime-control-plane/) | Centralizes agent lifecycle, tool permissions, invocation caps, health reports, human escalation, and audit events | DEMO |
| [Lead Intake Pipeline](./Demo%20Templates/AI%20Automation%20%26%20Workflows/lead-intake-pipeline/) | CSV validation, normalization, duplicate detection, lead scoring, and routing | DEMO |
| [Invoice Intake & Exception Routing](./Demo%20Templates/AI%20Automation%20%26%20Workflows/invoice-intake-exception-routing/) | Validates synthetic invoices, detects duplicates, and routes missing information, policy exceptions, and approval thresholds | DEMO |
| [Resumable Intake Operations Hub](./Demo%20Templates/AI%20Automation%20%26%20Workflows/intake-operations-hub/) | Composes lead and invoice intake with SQLite checkpoints, structured events, and durable human-review decisions | DEMO |
| [Operations Review Workspace](./Demo%20Templates/AI%20Product%20Development/operations-review-workspace/) | Local web workspace connected to SQLite intake state and durable human-review decisions | DEMO |
| [Operations Intake & Human Review Template](./Demo%20Templates/AI%20Product%20Development/operations-intake-review/) | Reusable assembly of intake pipelines, durable workflow state, review decisions, and local workspace | DEMO |
| [Marketing Analytics Pipeline](./Demo%20Templates/Marketing%20Intelligence%20%26%20Business%20Automation/marketing-analytics-pipeline/) | Composes CSV quality preflight with campaign metrics; blocks review findings by default | DEMO |
| [CRM Lead Qualification & Routing](./Demo%20Templates/AI%20Automation%20%26%20Workflows/crm-lead-qualification-routing/) | Configurable qualification rules, territory queues, follow-up dates, and human-review routing | DEMO |
| [Client Case Publication Gate](./Demo%20Templates/AI%20Skills%20%26%20Tooling/client-case-publication-gate/) | Pre-publication checks for evidence references, attribution permissions, data review, and claim authorization declarations; never authorizes publication | DEMO |
| [SME Customer Support Automation](./Demo%20Templates/AI%20Automation%20%26%20Workflows/sme-customer-support-automation/) | Support request classification, knowledge-based draft responses, and human escalation | DEMO |
| [SME Internal Knowledge Assistant](./Demo%20Templates/AI%20Agents%20%26%20Agentic%20Systems/sme-internal-knowledge-assistant/) | Role-filtered retrieval from approved sample sources, citations, and human escalation | DEMO |
| [Brief-to-Task Skill](./Demo%20Templates/AI%20Skills%20%26%20Tooling/brief-to-task/) | Structured business brief converted into a task plan with open questions | DEMO |
| [CSV Data Quality Profiler](./Demo%20Templates/AI%20Skills%20%26%20Tooling/csv-data-quality/) | CSV structure profiling, duplicate detection, and data-quality reporting | DEMO |
| [Document Intelligence — Plain-Text Extraction](./Demo%20Templates/AI%20Skills%20%26%20Tooling/document-intelligence/) | Traceable extraction of headings, key/value pairs, dates, contact details, and currency mentions | DEMO |
| [JSON Contract Validator](./Demo%20Templates/AI%20Skills%20%26%20Tooling/json-contract-validator/) | Validate JSON structures against a documented schema subset | DEMO |
| [CSV Data Normalization](./Demo%20Templates/AI%20Skills%20%26%20Tooling/data-normalization/) | Apply explicit, configurable CSV field transformations and report changed cells | DEMO |
| [Knowledge Retrieval](./Demo%20Templates/AI%20Skills%20%26%20Tooling/knowledge-retrieval/) | Role-filtered lexical retrieval with source excerpts, traceability, and no-match escalation | DEMO |
| [Agent Tool Gateway](./Demo%20Templates/AI%20Skills%20%26%20Tooling/agent-tool-gateway/) | Allowlisted tool dispatch with role checks, input contracts, approval gates, and audit events | DEMO |
| [Agent Execution & Orchestration](./Demo%20Templates/AI%20Skills%20%26%20Tooling/agent-orchestration/) | Sequential workflow execution with bounded retries, approval pauses, cancellation, and event traces | DEMO |
| [Multi-Agent Coordination](./Demo%20Templates/AI%20Skills%20%26%20Tooling/agent-coordination/) | Explicit agent registry, bounded handoffs, invocation limits, and escalation | DEMO |
| [Agent Evaluation](./Demo%20Templates/AI%20Skills%20%26%20Tooling/agent-evaluation/) | Scenario-based assertions for agent outputs, execution traces, and safety events | DEMO |
| [Agent State Store](./Demo%20Templates/AI%20Skills%20%26%20Tooling/agent-state-store/) | SQLite workflow-state persistence, optimistic versioning, and ordered event records | DEMO |
| [Agent Observability](./Demo%20Templates/AI%20Skills%20%26%20Tooling/agent-observability/) | Structured JSONL events with recursive redaction of common credential fields | DEMO |
| [Agent Recovery](./Demo%20Templates/AI%20Skills%20%26%20Tooling/agent-recovery/) | Bounded retries and reverse-order compensating actions with partial-rollback reporting | DEMO |
| [Agent Policy Validator](./Demo%20Templates/AI%20Skills%20%26%20Tooling/agent-policy-validator/) | Validate agent risk levels, explicit tool allowlists, approval gates, and execution bounds | DEMO |
| [Agent Security & Governance](./Demo%20Templates/AI%20Skills%20%26%20Tooling/agent-security-governance/) | Deny-by-default agent/tool authorization with scoped approval verification and audit decisions | DEMO |
| [SME Workflow Opportunity Mapper](./Demo%20Templates/AI%20Product%20Development/sme-workflow-opportunity-mapper/) | Transparent rubric to prioritize workflows for further discovery | DEMO |
| [SME KPI Workspace](./Demo%20Templates/Web%20Applications%20%26%20SaaS/sme-kpi-workspace/) | Responsive browser dashboard with KPI calculations and period filtering | DEMO |
| [Campaign Performance Analyzer](./Demo%20Templates/Marketing%20Intelligence%20%26%20Business%20Automation/campaign-performance-analyzer/) | CSV validation, campaign KPIs, temporal evolution, period comparison, filtered JSON export, and printable executive report | DEMO |
| [Campaign Launch QA & UTM Builder](./Demo%20Templates/Marketing%20Intelligence%20%26%20Business%20Automation/campaign-launch-qa/) | Pre-launch metadata validation, UTM URL generation, duplicate detection, and exception reporting | DEMO |

The included sample records are synthetic. These demonstrations do not imply client engagements or production deployments.

## Portfolio

| Area | Projects |
|---|---|
| [Client Demos](./Client%20Demos/) | Reserved for substantiated, authorized case studies from real client engagements |
| [Demo Templates](./Demo%20Templates/) | Library of reusable demonstrations organized into six technology categories |
| [AI Agents & Agentic Systems](./Demo%20Templates/AI%20Agents%20%26%20Agentic%20Systems/) | Agent demonstrations, orchestration patterns, and bounded agentic workflows |
| [AI Automation & Workflows](./Demo%20Templates/AI%20Automation%20%26%20Workflows/) | Automation examples and workflow tools for business processes |
| [AI Skills & Tooling](./Demo%20Templates/AI%20Skills%20%26%20Tooling/) | Reusable AI skills, utilities, and tools |
| [AI Product Development](./Demo%20Templates/AI%20Product%20Development/) | AI product concepts and functional prototypes |
| [Web Applications & SaaS](./Demo%20Templates/Web%20Applications%20%26%20SaaS/) | Application demonstrations and SaaS prototypes |
| [Marketing Intelligence & Business Automation](./Demo%20Templates/Marketing%20Intelligence%20%26%20Business%20Automation/) | Tools for marketing intelligence and business automation |

## Project standards

Use the [Project README Template](./PROJECT-README-TEMPLATE.md) when adding a project and follow the [Project Entry Criteria](./PROJECT-ENTRY-CRITERIA.md) before publishing. These standards keep project descriptions, status labels, execution instructions, evidence, and limitations consistent.

## First demonstrations

Use the [Selected Demo Guide](./DEMO-GUIDE.md) for reproducible setup and presentation steps for the three initial demonstrations.

## Getting started

1. Open a demo's README from the links above.
2. Check its requirements and documented limitations.
3. Use its included synthetic sample data, or provide appropriately authorized test data.
4. Run the documented command from that demo's directory.

Most command-line examples use Python 3.10+ and the standard library. The SME KPI Workspace uses a modern browser and Node.js 20+ for its automated tests. Individual project READMEs are authoritative for exact requirements and commands.

## Project status

The status shown in each project describes what is available to explore:

- **CONCEPT** — an idea and proposed approach; no working implementation.
- **DEMO** — a limited working example of a specific capability.
- **PROTOTYPE** — an implemented proof of concept that is not production-ready.
- **IMPLEMENTED** — running in a defined environment, with its scope and evidence documented.

Client projects are identified as such. Independently developed demos, templates, tools, and prototypes are presented in their own categories and are not represented as client engagements. The Client Demos section will be populated from case briefs and supporting information supplied for publication; no client identities, outcomes, metrics, or testimonials are fabricated.

## Quality and integrity

- Each project should document its purpose, run instructions, technologies, tests, status, and limitations.
- Automated tests are used where appropriate; workflow results are available in the repository's GitHub Actions.
- Synthetic data is used for examples unless a different source is explicitly authorized.
- No credentials, secrets, or confidential client materials belong in this public repository.
- The quality workflow runs a heuristic scan of tracked UTF-8 files for selected high-confidence credential formats and non-example `.env` files. It does not scan Git history or detect every secret or confidential-data type.
- A demo is not a production-ready service unless that status is explicitly supported by its implementation and evidence.
