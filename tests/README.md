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

## Latest CI evidence

- [Portfolio Demo Browser Tests — run 44242143780](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44242143780): passed; persisted decision, 375-pixel responsive checks, and report print-media behavior.
- [Portfolio Quality Gate — run 44242143819](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44242143819): passed; 36 project READMEs, eight category indexes, and 224 Python tests across 35 suites.

## Responsive and print smoke checks

The same Chromium workflow includes narrow viewport checks at 375 CSS pixels:

- **Operations Review Workspace:** verifies that the queue and detail panels stack into one column, fit within the viewport, and do not cause page-level horizontal overflow after the persisted-decision reload.
- **Campaign Performance Analyzer:** verifies the two-column KPI layout, channel-filter fit, and absence of page-level horizontal overflow after report generation.
- **Print media:** verifies that the Analyzer's executive report remains visible while the dashboard masthead and print control are hidden.

These checks target specific layout contracts. They do not replace manual visual review, test every device size, or establish cross-browser visual consistency.

## Public repository hygiene

Run the standard-library check from the repository root:

```bash
python scripts/check_public_content.py
```

The Portfolio Quality Gate runs this check before project documentation validation and unit tests. It scans Git-tracked UTF-8 text files for selected high-confidence credential formats and non-example environment-file names. Findings contain only a repository path and rule identifier; matched values are never printed.

This is a heuristic guard, not a comprehensive secret scanner. It does not inspect Git history, binary or oversized files, every credential format, or all forms of confidential/client information. A clean result does not replace code review, access controls, or credential rotation.

## Scope and limitations

These tests use synthetic records and loopback-only local servers. They verify selected workflows, not every visual state or browser/device combination. They do not test authentication, production security, external integrations, live customer data, or production deployment. A passing automated run does not mean a human has completed a local presentation review.

## Client Case Publication Gate

The [Client Case Publication Gate](../demo-templates/client-case-publication-gate/) is a standard-library Python preflight for a future authorized case package. Its dedicated workflow runs unit tests and the synthetic sample manifest.

The sample manifest is intentionally incomplete and must report `BLOCKED`; it does not represent a client, engagement, outcome, or publication approval. A complete manifest can reach only `READY_FOR_HUMAN_REVIEW`. The tool never returns publication authorization and does not verify underlying evidence or legal permissions.

Latest evidence:
- [Client Case Publication Gate Tests — run 44298660386](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44298660386): passed; 18 tests and the intentionally blocked sample command.
- [Portfolio Quality Gate — run 44298765167](https://github.com/mauropetersbrcomstudio/ai-innovation-portfolio/actions/runs/44298765167): passed; 37 project READMEs, eight category indexes, 275 Python tests across 36 suites, and the public-content scan of 215 tracked UTF-8 files with zero skips.
