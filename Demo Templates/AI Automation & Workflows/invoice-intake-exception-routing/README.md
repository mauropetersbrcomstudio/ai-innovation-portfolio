# Invoice Intake & Exception Routing

**Status: DEMO**

A local Python workflow that checks synthetic invoice records and routes each item to an appropriate review queue. It demonstrates a narrow accounts-payable intake process: required-field checks, date and amount validation, duplicate detection, purchase-order presence, and an approval-threshold rule.

This is an independently developed demonstration, not a client engagement or a deployed finance system.

## What it does

1. Reads a JSON array of invoice records.
2. Normalizes supplier and invoice identifiers for duplicate comparison.
3. Validates required fields, ISO dates, positive decimal amounts, supported currencies, and due-date order.
4. Flags every occurrence of a duplicate supplier/invoice pair.
5. Routes valid records to accounts-payable review or manager approval according to the configured amount threshold.
6. Writes a JSON report with one result per input row, reason codes, missing fields, and route counts.

## Routes

| Route | Meaning |
|---|---|
| `AP_REVIEW` | Complete record below or equal to the approval threshold; ready for human accounts-payable review |
| `MANAGER_APPROVAL` | Amount exceeds the configured threshold; manager review is recommended |
| `NEEDS_INFORMATION` | One or more required fields, including the purchase-order reference, are missing |
| `DUPLICATE_REVIEW` | More than one row has the same supplier and invoice identifier, ignoring letter case |
| `POLICY_HOLD` | Invalid record shape, date, amount, currency, or date sequence |

The default manager-review threshold is 5,000.00 in the invoice's stated currency. The demonstration does not perform foreign-exchange conversion or compare amounts across currencies.

## Requirements

- Python 3.10+
- Python standard library only
- No API keys, external accounts, database, or third-party packages

## Run

From this directory:

```bash
python invoice_workflow.py --input sample_invoices.json --output output/invoice-review.json
```

Set a different threshold with `--approval-threshold`:

```bash
python invoice_workflow.py --input sample_invoices.json --output output/invoice-review.json --approval-threshold 2500.00
```

The generated report is written to the output path. The `output/` directory is excluded from version control.

## Tests

```bash
python -m unittest discover -s tests -v
```

The tests cover the sample routes, case-insensitive duplicate detection, missing purchase orders, threshold boundaries, invalid values, malformed rows, and report writing.

## Data and safety boundaries

- The sample records and supplier identifiers are synthetic.
- The tool does not collect bank details, tax identifiers, or personal contact data.
- It does not approve invoices, authorize payments, create accounting entries, contact suppliers, or write to an ERP or accounting platform.
- A route is a review recommendation, not a financial decision.
- The threshold is a demonstration rule and must be configured and approved by the business before any real use.

## Limitations

- JSON input only; no PDF, image, OCR, or email ingestion.
- No purchase-order matching against an external system.
- No currency conversion, tax calculation, accounting validation, or fraud detection.
- No authentication, access control, encryption, durable workflow state, or external audit service.
- The duplicate check is limited to the current input batch.
- This deterministic rule-based demo is not an AI model and is not production-ready.

## Next steps

A later workflow iteration could add persisted review state, explicit human-resolution records, and structured execution events by reusing the portfolio's state-store and observability components. Any live accounting integration would require a separate scope and authorization.
