# Local prototype shell

Requires Python 3. Run:

```bash
cd prototype
python server.py
```

Open http://127.0.0.1:8767.

This first increment provides a local-only interface and session-scoped document inventory. Selected file contents are not uploaded or persisted. Parsing, normalization, reconciliation, rule execution, persistent workflow state, and approval records are not implemented yet; they require the client's representative sample files and verified business rules.

The server binds to loopback only and does not call external services.
