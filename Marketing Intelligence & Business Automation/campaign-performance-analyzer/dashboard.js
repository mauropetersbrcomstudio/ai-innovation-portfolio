import { analyzeRows, comparePeriods, parseCsv, summarizeByChannel, summarizeCampaigns } from "./dashboard-logic.js";

const money = value => value === null ? "N/A" : new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 2 }).format(value);
const integer = value => new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(value);
const ratio = value => value === null ? "N/A" : value.toFixed(2) + "x";
const percent = value => value === null ? "N/A" : (value * 100).toFixed(2) + "%";
const $ = selector => document.querySelector(selector);
let loaded = null;

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
}
function changeText(current, previous, formatter) {
  if (previous === null || previous === 0 || current === null) return "Change: unavailable (previous value is zero or undefined)";
  const delta = (current - previous) / Math.abs(previous) * 100;
  return (delta > 0 ? "+" : "") + delta.toFixed(1) + "% vs previous";
}
function activeMatches(item) {
  const query = $("#campaign-search").value.trim().toLocaleLowerCase();
  const channel = $("#channel-filter").value;
  return (channel === "all" || item.channel === channel) &&
    (!query || item.campaign.toLocaleLowerCase().includes(query));
}
function applyFilters() {
  if (!loaded) return;
  const baseValid = loaded.valid.filter(activeMatches);
  const baseExceptions = loaded.exceptions.filter(activeMatches);
  const start = $("#period-start").value;
  const end = $("#period-end").value;
  const valid = loaded.hasDate && start && end
    ? baseValid.filter(item => item.date >= start && item.date <= end) : baseValid;
  const exceptions = loaded.hasDate && start && end
    ? baseExceptions.filter(item => item.date && item.date >= start && item.date <= end) : baseExceptions;
  const summary = summarizeCampaigns(valid);
  render({ valid, exceptions, summary }, loaded.fileName);
  renderPeriod(baseValid);
  $("#filter-note").textContent = valid.length + " valid campaign(s) and " + exceptions.length +
    " exception row(s) in this selection. KPIs and tables reflect campaign, channel and date filters.";
}
function renderPeriod(valid) {
  if (!loaded?.hasDate || !valid.length) { $("#period-panel").hidden = true; return; }
  const dates = valid.map(item => item.date).sort();
  const start = $("#period-start").value || dates[0];
  const end = $("#period-end").value || dates[dates.length - 1];
  if (start > end) { $("#period-panel").hidden = true; $("#filter-note").textContent = "Period start must not be after period end."; return; }
  const comparison = comparePeriods(valid, start, end);
  const current = comparison.current.summary;
  const previous = comparison.previous.summary;
  $("#period-panel").hidden = false;
  $("#period-label").textContent = comparison.previous.start + " → " + comparison.previous.end;
  $("#period-spend").textContent = money(current.spend);
  $("#period-spend-change").textContent = changeText(current.spend, previous.spend, money);
  $("#period-conversions").textContent = integer(current.conversions);
  $("#period-conversions-change").textContent = changeText(current.conversions, previous.conversions, integer);
  $("#period-roas").textContent = ratio(current.roas);
  $("#period-roas-change").textContent = changeText(current.roas, previous.roas, ratio);
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
  const valid = loaded.valid.filter(activeMatches);
  const exceptions = loaded.exceptions.filter(activeMatches);
  const report = {
    report_type: "campaign-performance-analyzer-filtered-report",
    source_file: loaded.fileName,
    exported_at: new Date().toISOString(),
    filters: { campaign_search: $("#campaign-search").value.trim(), channel: $("#channel-filter").value,
      period_start: $("#period-start").value || null, period_end: $("#period-end").value || null },
    definitions: { ctr: "clicks / impressions", conversion_rate: "conversions / clicks", cpc: "spend / clicks",
      cpa: "spend / conversions", roas: "attributed revenue / spend" },
    summary: summarizeCampaigns(valid), campaigns: valid, exceptions,
    period_comparison: loaded.hasDate && $("#period-start").value && $("#period-end").value
      ? comparePeriods(valid, $("#period-start").value, $("#period-end").value) : null,
    limitations: ["Metrics use only supplied CSV values.", "No advertising platform connection or attribution verification.",
      "ROAS is not profit or ROI.", "Exception rows are excluded from performance totals."]
  };
  const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url; link.download = "campaign-report-filtered.json";
  document.body.append(link); link.click(); link.remove(); URL.revokeObjectURL(url);
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
    $("#campaign-search").disabled = false; $("#channel-filter").disabled = false; $("#export-report").disabled = false;
    if (loaded.hasDate && loaded.valid.length) {
      const dates = loaded.valid.map(item => item.date).sort();
      $("#period-start").value = dates[0]; $("#period-end").value = dates[dates.length - 1];
      $("#period-start").min = dates[0]; $("#period-start").max = dates[dates.length - 1];
      $("#period-end").min = dates[0]; $("#period-end").max = dates[dates.length - 1];
      $("#period-controls").hidden = false;
    } else { $("#period-controls").hidden = true; $("#period-panel").hidden = true; }
    applyFilters();
  } catch (error) { loaded = null; $("#file-status").textContent = "Could not process file: " + error.message; }
});
$("#campaign-search").addEventListener("input", applyFilters);
$("#channel-filter").addEventListener("change", applyFilters);
$("#period-start").addEventListener("change", applyFilters);
$("#period-end").addEventListener("change", applyFilters);
$("#export-report").addEventListener("click", exportReport);
