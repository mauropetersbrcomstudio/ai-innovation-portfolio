# Security and Privacy — Prototype Controls

## 1. Current operating boundary

The prototype runs locally and has no external platform integrations. It must not connect to production ERP databases, shared production servers, banking portals, government portals, messaging platforms, or cloud drives.

## 2. Source data handling

- Keep source client files in a controlled local working directory outside the public repository.
- Do not commit raw documents, extracted personal data, tax identifiers, bank details, payroll data, credentials, or customer communications.
- Restrict local access to authorized project operators.
- Preserve source files as read-only inputs where possible.
- Store hashes and file references rather than copying sensitive source content into logs.
- Use sanitized fixtures for automated tests and public screenshots.
- Do not send confidential client data to public AI services. Any model use with client data requires an approved corporate environment and applicable contractual/privacy controls.

## 3. Secrets

Never store passwords, tokens, certificates, private keys, API credentials, or connection strings in source code, logs, fixtures, screenshots, or Git history.

## 4. Auditability

Record imports, parsing attempts, rule versions, check runs, exception changes, approvals, overrides, and exports. Audit records should identify actor/service, timestamp, correlation ID, object reference, action, and rationale where relevant.

The prototype audit log is not represented as tamper-proof or production-grade. Production deployment would require hardened access control, centralized monitoring, retention policy, backup, and integrity protection.

## 5. Human control

No autonomous tax filing, payment, legal response, payroll termination approval, tax regime change, or final professional judgment. Critical unresolved issues block the simulated release step.

## 6. Public disclosure

The public repository must remain anonymized. Client name, brand, logos, identifiable staff/client details, real source documents, operational baselines, screenshots, and client-specific outcomes require separate public-disclosure authorization before publication.

Authorization to use supplied data for project analysis or a private demonstration does not automatically authorize publication of that data.
