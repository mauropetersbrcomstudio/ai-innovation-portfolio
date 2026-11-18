# Portfolio Cross-Project Tests

This folder contains checks that exercise more than one portfolio project in a single presentation path.

## Browser end-to-end test

[`portfolio-demos.e2e.mjs`](./portfolio-demos.e2e.mjs) uses Playwright with Chromium to verify two local demonstrations:

1. **Operations Review Workspace** — loads the synthetic queue, records a human-review decision, checks queue counters, reloads the page, and confirms the decision remains in the SQLite-backed history.
2. **Campaign Performance Analyzer** — imports the included synthetic CSV in the browser, applies a channel filter, and renders the executive report.

The GitHub Actions workflow [Portfolio Demo Browser Tests](../.github/workflows/portfolio-demo-browser-tests.yml) installs the browser dependency, starts both services on loopback, and runs this script. The workflow uses an isolated temporary SQLite database and does not contact external business systems.

## Related checks

- [Portfolio Quality Gate](../.github/workflows/portfolio-quality.yml) validates the root/category indexes and project documentation, then discovers and runs the Python unit-test suites.
- [Campaign Launch QA Tests](../.github/workflows/campaign-launch-qa-tests.yml) runs the command-line demo's unit tests and checks its sample output files.
- Each project README remains the source of truth for its own setup, commands, dependencies, and limitations.

## Scope and limitations

These tests use synthetic records and loopback-only local servers. They verify selected workflows, not every visual state or browser/device combination. They do not test authentication, production security, external integrations, live customer data, or production deployment. A passing automated run does not mean a human has completed a local presentation review.
