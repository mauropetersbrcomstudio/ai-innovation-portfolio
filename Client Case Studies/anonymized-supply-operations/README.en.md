# Supply Replenishment Assistant (Anonymized)

**Status: PROTOTYPE**

A local prototype derived from a client-context project. The client identity and brand assets are withheld because specific public-disclosure authorization is not recorded. This public version does not claim that its demonstration rules were approved by the client.

## Run locally

Requires Python 3. From this directory, run:

```bash
python server.py
```

Open `http://127.0.0.1:8765`. The server accepts connections only from this computer. No packages, account, API key, or external connection are required.

## Demonstration flow

1. Enter a synthetic request or choose an example.
2. The prototype interprets the text locally and identifies the unit, supply item, quantity, and urgency using deterministic rules and keywords.
3. Review or correct the extracted fields.
4. Inspect fictional inventory balances and the demonstration policy `DEMO-SUP-01`.
5. Review the simulated transfer or purchase proposal in the queue.
6. Record a simulated human decision; data remains in this browser's `localStorage`.

## Data and limitations

- Inventory, catalog, units, initial requests, limits, and policy values are synthetic.
- There is no ERP, inventory, finance, supplier, scheduling, patient-record, messaging, or other external-system integration.
- No AI model is connected; message interpretation uses local rules.
- Approving, rejecting, or receiving changes only local demo state. No purchase, physical transfer, or message occurs.
- The prototype does not authenticate users or verify who recorded a decision.
- Do not enter real patient, employee, supplier, or operational data.

This is a local PROTOTYPE for controlled demonstration, not a production system or evidence of operational outcomes.
