# Four Industry Workflow Prototypes

**Status: PROTOTYPE** — independent local demonstrations awaiting client-specific briefs, attribution, and validation.

Four functional, browser-based workflows assembled from patterns already present in the portfolio: lead intake and CRM routing, invoice exception routing, operations review, and governed human decisions. They use explicit deterministic rules, synthetic inputs, a browser-local queue, decision notes, event history, JSON export, and sector reset.

| Sector | Workflow | Demonstrated decision |
|---|---|---|
| Professional education | Adult course enrollment intake | Documentation, schedule, and available-seat review |
| Retail | Return exceptions | Illustrative deadline, receipt, condition, and value review |
| Hospitality | Room maintenance | Occupancy and safety escalation |
| Manufacturing | Quality deviations | Severity, evidence, and release-status escalation |

These are four proposed client-specific starting points, **not four completed client engagements**. No client name, logo, workflow requirement, policy, outcome, or authorization record is present in this version. Rules and thresholds are illustrative and must be validated with each client before being presented as their actual process. The interface does not claim live AI model inference.

## Run

Requires Python 3.10+ and a modern browser. No packages, account, key, or network connection are needed.

```bash
python server.py
```

Open `http://127.0.0.1:8768/`. Select one of the four sectors in the sidebar. Use **Fluxo padrão** or **Exceção** to fill synthetic inputs, submit a request, inspect the suggested queue and reasons, then record a human decision with a note. Reload to confirm local persistence. Export JSON or reset the current sector as needed.

Run deterministic rule tests with Node.js 20+:

```bash
node --test tests/engine.test.cjs
```

The portfolio browser workflow also exercises all four exception paths, decision persistence after reload, and a 375-pixel mobile viewport with Playwright/Chromium. It runs on pull requests that change this project; it requires the browser dependency installed by CI.

## Scope and data

- State lives only in the current browser's `localStorage`. Each sector has an independent key.
- All sample references, room codes, lots, values, thresholds, and policy logic are synthetic.
- The browser does not send data to a server. The Python server only serves static files on loopback.
- No authentication, shared database, real inventory, order, reservation, enrollment, quality-system, messaging, or payment integration exists.
- Approve, request adjustment, and reject are local simulated decisions. Event history is editable browser data, not a reliable audit trail.
- Do not enter personal, confidential, client, guest, student, or production data.

## Before client-case publication

For each of the four clients, obtain the exact name/logo supplied by the user, confirm the intended workflow and approved public wording, validate sample rules against the actual brief, and review each statement under the portfolio's Client Case Publication Gate. A functional prototype can be described as a client project only after its client relationship and public disclosure scope are substantiated. Do not infer implementation, deployment, savings, or client outcomes from this demonstration.
