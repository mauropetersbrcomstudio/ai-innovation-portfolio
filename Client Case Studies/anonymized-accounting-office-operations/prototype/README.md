# Local accounting prototype

Requires Python 3. Run:

```bash
cd prototype
python server.py
```

Open http://127.0.0.1:8767.

## Implemented in this increment

- Browser-local file selection; files are read with the browser File API and are not uploaded to the local server or external services.
- CSV: delimiter detection for comma, semicolon, or tab; header-based extraction only when date, amount, and description columns can be identified. Original values are retained as text.
- OFX: extraction of STMTTRN date, amount, and NAME/MEMO text.
- XML: well-formedness check only; DTD/ENTITY declarations are rejected. No fiscal schema or tax-field interpretation is claimed.
- 10 MB per-file limit; unsupported formats are listed without being read.
- Session-only preview; clearing the session removes the in-memory selection and normalized preview.

## Explicit limitations

No persistence, PDF/OCR, XLSX parsing, tax calculation, accounting classification, bank reconciliation, payroll processing, checklist evaluation, or filing/transmission. CSV layouts with unrecognized headers fail closed. OFX support is limited to basic STMTTRN blocks; bank-specific variants may require adapters. Monetary values are preserved as strings and are not converted to numbers or used in calculations.

The first MVP workflow scope remains Simples Nacional and Lucro Presumido. Lucro Real and other services remain outside the current MVP. Use only authorized, sanitized samples for testing; real client documents must remain outside the public repository.

The server binds to 127.0.0.1 and does not call external services.
