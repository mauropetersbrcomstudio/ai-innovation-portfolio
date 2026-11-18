# AI Innovation Portfolio

**Mauro Peters | AI Strategy, Product Development & Business Automation**

A portfolio of selected client work alongside independently developed AI demonstrations, reusable templates, tools, and product prototypes.

The repository brings together two kinds of work: projects carried out for real clients, presented in the Client Demos section, and solutions or building blocks developed independently to explore, demonstrate, or support the use of AI in business.

## Explore working demos

The projects below are executable demonstrations. Each project README contains its own setup instructions, scope, and limitations.

| Demo | What it demonstrates | Status |
|---|---|---|
| [SME Operations Assistant](./AI%20Agents%20%26%20Agentic%20Systems/sme-operations-assistant/) | Request classification, action allowlisting, escalation, and decision traces | DEMO |
| [SME Procurement Request Triage Agent](./AI%20Agents%20%26%20Agentic%20Systems/sme-procurement-request-triage/) | Purchase-request validation, policy-based review routing, duplicate detection, and supplier checks | DEMO |
| [Lead Intake Pipeline](./AI%20Automation%20%26%20Workflows/lead-intake-pipeline/) | CSV validation, normalization, duplicate detection, lead scoring, and routing | DEMO |
| [SME Customer Support Automation](./demo-templates/sme-customer-support-automation/) | Support request classification, knowledge-based draft responses, and human escalation | DEMO |
| [Brief-to-Task Skill](./AI%20Skills%20%26%20Tooling/brief-to-task/) | Structured business brief converted into a task plan with open questions | DEMO |
| [SME Workflow Opportunity Mapper](./AI%20Product%20Development/sme-workflow-opportunity-mapper/) | Transparent rubric to prioritize workflows for further discovery | DEMO |
| [SME KPI Workspace](./Web%20Applications%20%26%20SaaS/sme-kpi-workspace/) | Responsive browser dashboard with KPI calculations and period filtering | DEMO |
| [Campaign Performance Analyzer](./Marketing%20Intelligence%20%26%20Business%20Automation/campaign-performance-analyzer/) | CSV validation and calculation of CTR, conversion rate, CPC, CPA, and ROAS | DEMO |

The included sample records are synthetic. These demonstrations do not imply client engagements or production deployments.

## Portfolio

| Area | Projects |
|---|---|
| [Client Demos](./client-demos/) | Reserved for substantiated, authorized case studies from real client engagements |
| [Demo Templates](./demo-templates/) | Reusable templates for presenting and adapting AI solutions to business needs |
| [AI Agents & Agentic Systems](./AI%20Agents%20%26%20Agentic%20Systems/) | Agent demonstrations, orchestration patterns, and bounded agentic workflows |
| [AI Automation & Workflows](./AI%20Automation%20%26%20Workflows/) | Automation examples and workflow tools for business processes |
| [AI Skills & Tooling](./AI%20Skills%20%26%20Tooling/) | Reusable AI skills, utilities, and tools |
| [AI Product Development](./AI%20Product%20Development/) | AI product concepts and functional prototypes |
| [Web Applications & SaaS](./Web%20Applications%20%26%20SaaS/) | Application demonstrations and SaaS prototypes |
| [Marketing Intelligence & Business Automation](./Marketing%20Intelligence%20%26%20Business%20Automation/) | Tools for marketing intelligence and business automation |

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
- A demo is not a production-ready service unless that status is explicitly supported by its implementation and evidence.
