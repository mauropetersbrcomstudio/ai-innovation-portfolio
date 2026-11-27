# Healthcare Reception Assistant

**Status: DEMO**

A local, browser-based product prototype for a healthcare reception workflow. It demonstrates administrative-message routing, synthetic appointment-preference intake, a browser-local review queue, and human escalation for clinical, urgent, ambiguous, or unsupported requests.

It is an independently developed demo template. It does not represent a client deployment or use client data.

## Run locally

No packages or API keys are needed. From this directory, start a local static server with Python 3:

```bash
python -m http.server 8000
```

Open [http://localhost:8000](http://localhost:8000). You can also open `index.html` directly in a browser; the local server is recommended for consistent browser storage.

## What to try

- Ask to book an assessment and submit a synthetic region and preferred time period. The request appears in the local reception queue as pending.
- Ask about hours, addresses, prices, or services. Since no real approved content is provided, the demo routes the question for human review.
- Use the clinical and urgent sample prompts. The demo does not generate clinical advice and creates only a generic escalation record.
- Mark an item as reviewed to demonstrate the human workflow. This does not confirm an appointment or trigger any external action.

## Boundaries

- Use synthetic information only. Do not enter real names, contact details, health information, or appointment data.
- No WhatsApp, Instagram, phone, website, calendar, CRM, or patient-record connection is included.
- No messages are sent and no appointments are confirmed.
- The queue is stored only in the current browser's local storage. It has no login, access controls, cross-device synchronization, or notifications.
- Classification is deterministic keyword logic. The demo includes no organization-specific operational content.
- A real implementation requires approved content, authentication, access controls, privacy review, monitored escalation procedures, and validated integrations.

This is a functional prototype for walkthroughs and product discovery, not a production system.
