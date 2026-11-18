# Operations Review Workspace

**Status: DEMO**

A small local web application connected to the existing Resumable Intake Operations Hub. It loads a synthetic intake workflow from SQLite, displays its review queue, records decisions through the existing `ReviewDecisionStore`, and shows persisted decision and event history.

## Run locally

Requires Python 3.10+; standard library only.

From this directory:

```bash
python server.py
```

Open the address printed by the server (default `http://127.0.0.1:8765`). Stop the server with Ctrl+C. The first run creates a synthetic workflow and SQLite database under `output/`. The sample workflow is seeded only when it does not already exist.

To use another local port:

```bash
python server.py --port 8766
```

The server refuses non-loopback binding. No external packages, cloud hosting, or paid services are required.

## Demonstration path

1. Start the server and open the printed loopback address.
2. Review the queue totals and filter between lead, invoice, pending, and decided items.
3. Select a pending item and inspect its source reference and routing reason.
4. Enter a clearly synthetic reviewer identifier, choose an outcome, provide a reason, and record the decision.
5. Refresh the workspace and confirm the item is marked decided and appears in the decision history.

A review decision is a local record only. It does not send a message, update a CRM, approve an invoice for payment, or trigger another external action.

## What works

- Reads the persisted workflow and prepared human-review queue.
- Filters queue items by source and decision status.
- Displays source reference, routing reason, and item details.
- Records one of three supported outcomes through the existing decision store.
- Refreshes the queue from SQLite after a successful write.
- Displays persisted decisions and workflow event history.
- Rejects duplicate decisions, unknown items, and unsupported outcomes.

## Product design artifacts

- [Product brief](./PRODUCT-BRIEF.md)
- [User journeys](./USER-JOURNEYS.md)
- [Data model and interface contract](./DATA-MODEL-AND-INTERFACE-CONTRACT.md)

## Trust and security boundaries

- **Local demo only:** the HTTP server binds to loopback and is not designed for LAN or internet exposure.
- **Synthetic data:** the bundled sample records are fictional. Do not place real customer or invoice data in this demo.
- **No authentication:** the reviewer identifier is typed into the form and is an unverified assertion, not an authenticated identity. Do not use this to make real operational decisions.
- **No external side effects:** no CRM, email, accounting, payment, or bank transfer action is performed.
- **Audit limitations:** decision records are persisted with a matching workflow event in one SQLite transaction, but direct database modification is possible; storage is not tamper-proof.
- **No production controls:** no identity provider, server-side reviewer roles, CSRF token, TLS, deployment hardening, backups, or operational monitoring.

## Tests

From this directory:

```bash
python -m unittest discover -s tests -v
```

The integration tests exercise the HTTP adapter, real SQLite state, decision persistence, duplicate rejection, invalid input, and loopback binding.
