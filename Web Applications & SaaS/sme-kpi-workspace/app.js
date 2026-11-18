import { monthlyData } from "./data.js";
import { filterPeriod, summarize } from "./metrics.js";

const currency = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
const integer = new Intl.NumberFormat("en-US");
const percent = value => `${value.toFixed(1)}%`;

function render(rows) {
  const totals = summarize(rows);
  document.querySelector("#revenue").textContent = currency.format(totals.revenue);
  document.querySelector("#orders").textContent = integer.format(totals.orders);
  document.querySelector("#aov").textContent = currency.format(totals.averageOrderValue);
  document.querySelector("#conversion").textContent = percent(totals.conversionRate);
  document.querySelector("#period-count").textContent = `${rows.length} months`;

  const maxRevenue = Math.max(1, ...rows.map(row => row.revenue));
  document.querySelector("#revenue-chart").innerHTML = rows.map(row => {
    const height = (row.revenue / maxRevenue) * 100;
    return `<div class="bar-group"><span class="bar-value">${currency.format(row.revenue)}</span><div class="bar" style="height:${height}%" title="${row.month}: ${currency.format(row.revenue)}"></div><span class="bar-label">${row.month}</span></div>`;
  }).join("");

  document.querySelector("#monthly-rows").innerHTML = rows.map(row => {
    const conversion = row.visits ? (row.orders / row.visits) * 100 : 0;
    return `<tr><td>${row.month} 2026</td><td>${currency.format(row.revenue)}</td><td>${integer.format(row.orders)}</td><td>${integer.format(row.visits)}</td><td>${percent(conversion)}</td></tr>`;
  }).join("");
}

document.querySelector("#period-filter").addEventListener("change", event => {
  render(filterPeriod(monthlyData, event.target.value));
});
render(monthlyData);
