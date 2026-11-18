import { analyzeRows, parseCsv, summarizeByChannel, summarizeCampaigns } from "./dashboard-logic.js";

const money = value => value === null ? "N/A" : new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 2 }).format(value);
const integer = value => new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(value);
const ratio = value => value === null ? "N/A" : value.toFixed(2) + "x";
const percent = value => value === null ? "N/A" : (value * 100).toFixed(2) + "%";
const $ = selector => document.querySelector(selector);
let loaded = null;

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
}

function applyFilters() {
  if (!loaded) return;
  const query = $("#campaign-search").value.trim().toLocaleLowerCase();
  const channel = $("#channel-filter").value;
  const matches = item => (channel === "all" || item.channel === channel) &&
    (!query || item.campaign.toLocaleLowerCase().includes(query));
  const valid = loaded.valid.filter(matches);
  const exceptions = loaded.exceptions.filter(matches);
  const summary = summarizeCampaigns(valid);
  render({ valid, exceptions, summary }, loaded.fileName);
  $("#filter-note").textContent = valid.length + " valid campaign(s) and " + exceptions.length +
    " exception row(s) in this selection. KPIs and tables reflect the current filters.";
}

function render(result, fileName) {
  const { valid, exceptions, summary } = result;
  $("#file-status").textContent = fileName + " · processed locally";
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

function exportReport() {
  if (!loaded) return;
  const query = $("#campaign-search").value.trim();
  const channel = $("#channel-filter").value;
  const matches = item => (channel === "all" || item.channel === channel) &&
    (!query || item.campaign.toLocaleLowerCase().includes(query.toLocaleLowerCase()));
  const valid = loaded.valid.filter(matches);
  const exceptions = loaded.exceptions.filter(matches);
  const report = {
    report_type: "campaign-performance-analyzer-filtered-report",
    source_file: loaded.fileName,
    exported_at: new Date().toISOString(),
    filters: { campaign_search: query, channel },
    definitions: {
      ctr: "clicks / impressions",
      conversion_rate: "conversions / clicks",
      cpc: "spend / clicks",
      cpa: "spend / conversions",
      roas: "attributed revenue / spend"
    },
    summary: summarizeCampaigns(valid),
    campaigns: valid,
    exceptions,
    limitations: [
      "Metrics are calculated only from values in the supplied CSV.",
      "No advertising platform connection or attribution verification.",
      "ROAS is not profit or ROI.",
      "Exception rows are excluded from performance totals."
    ]
  };
  const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "campaign-report-filtered.json";
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

$("#csv-file").addEventListener("change", async event => {
  const file = event.target.files?.[0];
  if (!file) return;
  $("#file-status").textContent = "Reading " + file.name + "…";
  try {
    const rows = parseCsv(await file.text());
    loaded = { ...analyzeRows(rows), fileName: file.name };
    const channels = [...new Set([...loaded.valid, ...loaded.exceptions].map(item => item.channel).filter(Boolean))]
      .sort((a, b) => a.localeCompare(b));
    $("#channel-filter").innerHTML = '<option value="all">All channels</option>' +
      channels.map(value => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`).join("");
    $("#campaign-search").disabled = false;
    $("#channel-filter").disabled = false;
    $("#export-report").disabled = false;
    applyFilters();
  } catch (error) {
    loaded = null;
    $("#file-status").textContent = "Could not process file: " + error.message;
  }
});
$("#campaign-search").addEventListener("input", applyFilters);
$("#channel-filter").addEventListener("change", applyFilters);
$("#export-report").addEventListener("click", exportReport);
