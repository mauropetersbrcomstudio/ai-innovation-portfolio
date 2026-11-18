# Marketing Intelligence & Business Automation

This section explores how marketing information can support better decisions and more consistent execution. Projects may include campaign analysis, reporting, audience and channel insights, and automation of recurring marketing tasks.

## Campaign Performance Analyzer

The [Campaign Performance Analyzer](./campaign-performance-analyzer/) is an executable Python demo. It validates campaign-level CSV data, calculates CTR, conversion rate, CPC, CPA, and ROAS, and produces campaign-level and aggregate reports.

## Marketing Analytics Pipeline

The [Marketing Analytics Pipeline](./marketing-analytics-pipeline/) composes the reusable CSV Data Quality Profiler with the Campaign Performance Analyzer. It runs a structural preflight, blocks review-level files by default, and proceeds to metrics only when the preflight passes or an operator explicitly allows review-level input.

Both demonstrations use synthetic sample data and transparent arithmetic. They do not connect to advertising platforms, verify attribution, or claim causal performance results.


## Campaign Launch QA & UTM Builder

The [Campaign Launch QA & UTM Builder](./campaign-launch-qa/) checks campaign metadata, date ranges, budgets, duplicate campaign IDs, destination URL structure, and UTM collisions. It generates tracking URLs and separates approved rows from exceptions without changing the source file. It does not publish campaigns or verify live tracking.

## Verification and presentation

The [Selected Demo Guide](../../DEMO-GUIDE.md) documents the Campaign Performance Analyzer and Campaign Launch QA presentation paths. The Analyzer's browser checks cover local CSV import, filtering, executive-report rendering, a 375-pixel mobile viewport, and print-media behavior. The Marketing Analytics Pipeline and Campaign Launch QA are command-line demonstrations; their automated checks are maintained with the private internal validation materials.

All bundled campaign records are synthetic. Automated checks do not verify advertising-platform data, attribution, legal compliance, or live campaign behavior.
