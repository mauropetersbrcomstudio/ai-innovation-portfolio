# SME Customer Support Automation

A practical starting point for mapping and demonstrating a support workflow for a small or medium-sized business. The template helps a team classify incoming requests, prepare consistent responses, and route cases that need a person.

**Type:** Reusable demo template  
**Readiness:** Ready to adapt; not a deployed support system  
**Data:** Use synthetic examples or data explicitly authorized for the demonstration

## 1. The business problem

SME support requests often arrive through several channels and are handled manually. Common consequences include slow triage, inconsistent answers, missed follow-ups, and staff spending time on repetitive questions.

This template defines a bounded workflow for organizing incoming requests. It does not assume that every request should be automated.

## 2. Intended workflow

1. **Receive** — capture the message and its source, timestamp, and available customer reference.
2. **Normalize** — standardize the request text and identify missing required information.
3. **Classify** — assign one primary category:
   - Order or delivery status
   - Billing or payment
   - Product or service information
   - Technical support
   - Returns or complaints
   - Other / unclear
4. **Retrieve approved information** — use only the business's approved FAQs, policies, product information, and operating procedures.
5. **Prepare a response** — draft a concise answer grounded in the approved information.
6. **Route** — send uncertain, sensitive, exceptional, or policy-dependent cases to a human.
7. **Record the outcome** — retain the category, routing decision, response status, and human resolution where permitted.

## 3. Automation boundaries

**May be automated in a controlled demonstration**
- Request normalization and categorization
- Detection of missing information
- Drafting responses from an approved knowledge base
- Routing recommendations and internal summaries
- Logging of workflow decisions

**Must remain under human control unless separately authorized and tested**
- Refunds, credits, cancellations, or order changes
- Changes to customer accounts or personal information
- Commitments about delivery dates, prices, warranties, or compensation
- Complaints involving legal, safety, privacy, or reputational risk
- Sending messages to customers or taking actions in live business systems

When confidence is low, information is missing, or sources conflict, the workflow should abstain and escalate rather than guess.

## 4. Required business inputs

Before adapting the template, collect and approve:

- Support channels and operating hours
- Request categories and priority definitions
- Current FAQs and policy documents
- Order, billing, returns, and escalation procedures
- Tone of voice and approved response examples
- Human owners and escalation destinations
- Data retention, access, and privacy requirements
- Systems involved and the permissions available to an automation

Do not connect customer systems or use real customer data until the business has approved the scope, access, and safeguards.

## 5. Suggested output for each request

| Field | Description |
|---|---|
| Request ID | Business-approved reference; avoid unnecessary personal data |
| Category | Primary request category |
| Summary | Short description of the customer's need |
| Information gaps | Details required before a reliable answer is possible |
| Suggested response | Draft based on approved sources |
| Source references | FAQ or policy sections used |
| Route | Automated draft, human review, or specialist escalation |
| Reason | Why the route was selected |
| Status | New, awaiting information, in review, resolved |

## 6. Exception and escalation rules

Escalate when:
- The request cannot be classified reliably.
- Approved information does not answer the question.
- Two approved sources disagree.
- The customer disputes a previous answer or requests an exception.
- The request involves money, account access, personal data, safety, legal matters, or a formal complaint.
- The workflow would need to perform an action outside its approved permissions.

The system should preserve the original request and explain why it escalated. It should not silently discard or rewrite the customer's message.

## 7. Demonstration scenario

Use a small set of synthetic requests covering:
- A straightforward delivery-status question
- A billing question with a documented answer
- A request missing an order reference
- A complaint requiring human attention
- A question not covered by the knowledge base

For each example, show the category, source used, draft or information gap, routing decision, and reason. Label all sample data clearly as synthetic.

## 8. Acceptance checks

A demonstration is ready for review when it can show that:

- Each test request receives a traceable category or an explicit uncertainty result.
- Draft answers refer only to approved source material.
- Missing information is identified rather than invented.
- Sensitive and out-of-scope requests are routed to a person.
- No live customer message or business-system action occurs without explicit authorization.
- The workflow records enough information to review why it made each routing decision.

## 9. Adaptation checklist

- [ ] Confirm the business problem and measurable objective.
- [ ] Map current support channels and handoffs.
- [ ] Approve categories, priorities, and escalation owners.
- [ ] Collect and review the knowledge sources.
- [ ] Define permitted data and system access.
- [ ] Prepare synthetic test cases.
- [ ] Test normal, ambiguous, conflicting, and sensitive requests.
- [ ] Review outputs with the support team.
- [ ] Document limitations and obtain approval before any live pilot.

## 10. Possible next implementation

This template can be turned into a small working demonstration with a CSV or form-based intake, rule-based categorization, retrieval from a curated FAQ file, response drafts, and an exception report. A live chatbot, CRM connection, or automatic customer messaging is a separate scope and should not be implied by this template.

---

**Portfolio note:** This is an independently developed reusable template. It is not presented as a completed client engagement or as a deployed production system.
