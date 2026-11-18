import { monthlyData } from "./data.js";
import { filterPeriod, summarize } from "./metrics.js";

const currency = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
const integer = new Intl.NumberFormat("en-US");
const percent = value => `${value.toFixed(1)}%`;
const periodLabels = {
  all: "JANUARY — JUNE 2026",
  q1: "JANUARY — MARCH 2026",
  q2: "APRIL — JUNE 2026"
};

function render(rows, period) {
  const totals = summarize(rows);
  document.querySelector("#revenue").textContent = currency.format(totals.revenue);
  document.querySelector("#orders").textContent = integer.format(totals.orders);
  document.querySelector("#aov").textContent = currency.format(totals.averageOrderValue);
  document.querySelector("#conversion").textContent = percent(totals.conversionRate);
  document.querySelector("#period-count").textContent = `${rows.length} MONTHS`;
  document.querySelector("#period-label").textContent = periodLabels[period];

  const maxRevenue = Math.max(1, ...rows.map(row => row.revenue));
  const peak = rows.reduce((best, row) => row.revenue > best.revenue ? row : best, rows[0]);
  document.querySelector("#peak-month").textContent = peak
    ? `Highest month: ${peak.month} · ${currency.format(peak.revenue)}`
    : "No records in this period";

  const chart = document.querySelector("#revenue-chart");
  chart.innerHTML = rows.map(row => {
    const height = (row.revenue / maxRevenue) * 100;
    const isPeak = peak && row.month === peak.month;
    return `<div class="bar-group${isPeak ? " is-peak" : ""}" role="listitem" aria-label="${row.month} 2026 revenue ${currency.format(row.revenue)}">
      <span class="bar-value">${currency.format(row.revenue)}</span>
      <div class="bar" style="height:${height}%" aria-hidden="true"></div>
      <span class="bar-label">${row.month}</span>
    </div>`;
  }).join("");

  document.querySelector("#monthly-rows").innerHTML = rows.map(row => {
    const conversion = row.visits ? (row.orders / row.visits) * 100 : 0;
    return `<tr><td>${row.month} 2026</td><td>${currency.format(row.revenue)}</td><td>${integer.format(row.orders)}</td><td>${integer.format(row.visits)}</td><td>${percent(conversion)}</td></tr>`;
  }).join("");
}

const filter = document.querySelector("#period-filter");
filter.addEventListener("change", event => {
  render(filterPeriod(monthlyData, event.target.value), event.target.value);
});
render(monthlyData, filter.value);
