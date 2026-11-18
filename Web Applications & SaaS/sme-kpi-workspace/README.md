# SME KPI Workspace

**Status: DEMO**

A responsive, static business dashboard for exploring a small set of operational indicators. It uses a clearly labelled synthetic dataset and runs locally in a browser without a backend or external services.

## Explore

Open `index.html` in a modern browser. Use the reporting-period selector to switch between all six sample months, Q1 2026, and Q2 2026.

The dashboard displays:
- Revenue
- Completed orders
- Average order value (revenue divided by orders)
- Conversion rate (orders divided by visits)
- A responsive monthly revenue chart with the highest month highlighted
- A detailed monthly table and reporting-period label

The interface uses an editorial, off-white and charcoal visual system with restrained gold accents. It adapts to narrow screens and respects reduced-motion preferences.

## Run automated tests

Requires Node.js 20 or newer:

```bash
npm test
```

## Data and calculation notes

All six monthly records in `data.js` are synthetic. Currency is displayed in USD for demonstration purposes. Average order value is calculated as total revenue divided by total orders. Conversion rate is calculated as total orders divided by total visits. The demo does not represent a real company's performance.

## Scope and limitations

This is a static front-end demonstration. It has no login, database, live analytics connection, data import, persistence, or role-based access. It is not a production SaaS application. The figures and KPI definitions are illustrative and should be replaced and agreed with a business before operational use.
