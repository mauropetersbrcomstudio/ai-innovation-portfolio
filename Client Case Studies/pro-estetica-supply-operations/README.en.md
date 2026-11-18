# Operations Assistant — Supply Replenishment

A real client case developed for Pró Estética Clinic. This functional prototype was prepared for approval before integration with the final platforms and go-live. It demonstrates a copilot that receives internal requests, consults a fictional inventory and policy database, proposes transfers or purchases, and records human decisions.

## Run locally

With Python 3 installed, open a terminal in this folder and run:

```bash
python server.py
```

Then open `http://127.0.0.1:8765`. The server accepts connections only from this computer. No packages, account, API key, or external connection are required. You can also open `index.html` directly, but the local server provides more predictable browser storage.

## Demonstration flow

1. Type a request or choose an example on the home screen.
2. The assistant interprets the text locally and identifies the unit, supply item, quantity, and urgency.
3. Review or correct the extracted fields.
4. The prototype checks the fictional inventory balances and `DEMO-EST-01` policy, then suggests a transfer from central inventory, a simulated purchase, or both steps.
5. The team reviews the request in the queue. Exceptions require a justification.
6. Approvals, receipts, and stock movements update data stored only in this browser's `localStorage`.

Requests that exceed central inventory proceed to a separate purchase approval step. Receipt can then be simulated to complete the request. Rejections are also recorded in the local queue.

## Limitations

- There is no integration with WhatsApp, ERP, inventory, finance, suppliers, scheduling, or electronic health records.
- Message interpretation uses local rules and keywords; no AI model is connected.
- Inventory, catalog, 17 units, initial requests, and limits are synthetic data. Pró Estética has not approved these rules.
- Approving or receiving updates only the local demo state. No purchase, physical transfer, message, or external system update occurs.
- The prototype does not authenticate users. A local record does not verify who clicked.
- Do not enter real patient, employee, or operational data.

Use **Reiniciar demonstração** (Reset demo) to restore the synthetic examples. The header button exports a JSON copy of the current demo data.

