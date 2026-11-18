import { analyzeRows, parseCsv, summarizeByChannel } from "./dashboard-logic.js";

const money = value => value === null ? "N/A" : new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 2 }).format(value);
const integer = value => new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(value);
const ratio = value => value === null ? "N/A" : value.toFixed(2) + "x";
const percent = value => value === null ? "N/A" : (value * 100).toFixed(2) + "%";
const $ = selector => document.querySelector(selector);

function showData(result, fileName) {
  const { valid, exceptions, summary } = result;
  $("#file-status").textContent = fileName;
  $("#campaign-count").textContent = summary.campaign_count + " VALID CAMPAIGNS";
  $("#valid-count").textContent = valid.length + " VALID";
  $("#roas").textContent = ratio(summary.roas);
  $("#spend").textContent = money(summary.spend);
  $("#conversions").textContent = integer(summary.conversions);
  $("#cpa").textContent = money(summary.cpa);
  $("#ctr").textContent = percent(summary.ctr);
  $("#conversion-rate").textContent = percent(summary.conversion_rate);
  $("#cpc").textContent = money(summary.cpc);
  $("#impressions").textContent = integer(summary.impressions);

  const ranked = [...valid].filter(item => item.roas !== null).sort((a, b) => b.roas - a.roas);
  const max = Math.max(1, ...ranked.map(item => item.roas));
  $("#chart").innerHTML = ranked.length ? ranked.map((item, index) => {
    const width = Math.max(2, item.roas / max * 100);
    return `<div class="bar-group" role="listitem" aria-label="${escapeHtml(item.campaign)} ROAS ${ratio(item.roas)}"><span class="bar-value">${ratio(item.roas)}</span><div class="bar ${index === 0 ? "best" : ""}" style="height:${width}%"></div><span class="bar-label" title="${escapeHtml(item.campaign)}">${escapeHtml(item.campaign)}</span></div>`;
  }).join("") : '<p class="empty">No non-zero spend records available to calculate ROAS.</p>';

  const channels = summarizeByChannel(valid);
  $("#channel-rows").innerHTML = channels.length ? channels.map(item =>
    `<tr><td>${escapeHtml(item.channel)}</td><td>${integer(item.campaign_count)}</td><td>${money(item.spend)}</td><td>${integer(item.conversions)}</td><td>${money(item.cpa)}</td><td>${ratio(item.roas)}</td></tr>`
  ).join("") : '<tr><td colspan="6" class="empty-cell">No valid channel data.</td></tr>';

  $("#campaign-rows").innerHTML = valid.length ? valid.map(item =>
    `<tr><td>${escapeHtml(item.campaign)}</td><td>${escapeHtml(item.channel)}</td><td>${money(item.spend)}</td><td>${percent(item.ctr)}</td><td>${percent(item.conversion_rate)}</td><td>${money(item.cpa)}</td><td>${ratio(item.roas)}</td></tr>`
  ).join("") : '<tr><td colspan="7" class="empty-cell">No valid campaign rows.</td></tr>';

  $("#exceptions").hidden = exceptions.length === 0;
  $("#exception-count").textContent = exceptions.length + " ROWS";
  $("#exception-list").innerHTML = exceptions.map(item =>
    `<li>Row ${item.row} · ${escapeHtml(item.campaign || "Unnamed campaign")} — ${escapeHtml(item.reason)}</li>`
  ).join("");
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
}

$("#csv-file").addEventListener("change", async event => {
  const file = event.target.files?.[0];
  if (!file) return;
  $("#file-status").textContent = "Reading " + file.name + "…";
  try {
    const rows = parseCsv(await file.text());
    showData(analyzeRows(rows), file.name + " · processed locally");
  } catch (error) {
    $("#file-status").textContent = "Could not process file: " + error.message;
  }
});
