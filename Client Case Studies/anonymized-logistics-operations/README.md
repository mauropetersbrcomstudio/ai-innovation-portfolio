# Logistics Operations Workspace (Anonymized)

**Status: DEMO**

A local-only demonstration for manually recording and reviewing logistics operations. This public version is anonymized: client identity and the client-confirmed operational baseline are withheld pending explicit public-disclosure authorization.

Only generic interface behavior and manually entered demonstration records are included. Do not add client names, logos, source process documents, actual shipment records, personal data, commercial data, metrics, or outcomes without documented authorization.

## Demonstrated capabilities

- Manually register shipment references and operational metadata.
- Record a technology inventory for discovery discussions.
- Record operational occurrences and follow-up notes.
- Track document metadata and status without uploading source documents or performing fiscal validation.
- Record manual movement, collection, terminal, and proof-of-delivery events.
- Review a local event history and export the browser's demonstration state as JSON.
- Display deterministic alerts derived from manually entered records for human review.

These are local records and rule-based summaries. They do not confirm physical movement, delivery, contractual SLA, or actual business performance.

## Run locally

Requires Python 3 and no additional packages.

```bash
python server.py
```

Open `http://127.0.0.1:8766` on the same computer. Stop the server with Ctrl+C.

## Data and privacy

Records remain in this browser's `localStorage`; they are not synchronized. Use synthetic data only. Do not enter client records, personal data, transport documents, credentials, or confidential commercial information.

## Limitations

- No ERP, TMS, WMS, carrier, tracking, messaging, BI, or external service integration.
- No authentication, multi-user database, central backup, or tamper-evident audit.
- No fiscal-document validation, dispatch, payment, inventory movement, or physical delivery confirmation.
- No connected AI model; classifications and alerts are deterministic.
- This is a DEMO, not a production logistics system or a statement of a client's approved operating procedure.

See [PUBLIC-SCOPE.md](./docs/PUBLIC-SCOPE.md) for the publication boundary.
