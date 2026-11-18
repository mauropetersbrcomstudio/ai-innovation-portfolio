export const REQUIRED = ["campaign", "channel", "spend", "impressions", "clicks", "conversions", "revenue"];
const NUMERIC = ["spend", "impressions", "clicks", "conversions", "revenue"];
const DAY_MS = 86400000;

export function parseCsv(source) {
  const rows = [];
  let row = [], cell = "", quoted = false;
  for (let i = 0; i < source.length; i += 1) {
    const char = source[i];
    if (quoted) {
      if (char === '"' && source[i + 1] === '"') { cell += '"'; i += 1; }
      else if (char === '"') quoted = false;
      else cell += char;
    } else if (char === '"' && cell.length === 0) quoted = true;
    else if (char === ",") { row.push(cell); cell = ""; }
    else if (char === "\n" || char === "\r") {
      if (char === "\r" && source[i + 1] === "\n") i += 1;
      row.push(cell); cell = "";
      if (row.some(value => value.trim() !== "")) rows.push(row);
      row = [];
    } else cell += char;
  }
  if (quoted) throw new Error("CSV contains an unclosed quoted field.");
  row.push(cell);
  if (row.some(value => value.trim() !== "")) rows.push(row);
  if (!rows.length) throw new Error("The CSV file is empty.");
  const headers = rows.shift().map(value => value.trim().replace(/^\uFEFF/, ""));
  const missing = REQUIRED.filter(field => !headers.includes(field));
  if (missing.length) throw new Error("Missing required columns: " + missing.join(", "));
  return rows.map(values => Object.fromEntries(headers.map((header, i) => [header, (values[i] ?? "").trim()])))
    .filter(record => Object.values(record).some(value => value !== ""))
    .map((record, index) => ({ ...record, __row: index + 2, __hasDate: headers.includes("date") }));
}

export function isIsoDate(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value || "")) return false;
  const date = new Date(value + "T00:00:00.000Z");
  return Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value;
}
function number(value, field) {
  if (value === "") throw new Error(field + " is missing");
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed < 0) throw new Error(field + " must be a non-negative number");
  return parsed;
}
const divide = (a, b) => b === 0 ? null : a / b;

export function summarizeCampaigns(valid) {
  const totals = Object.fromEntries(NUMERIC.map(field => [field, valid.reduce((sum, item) => sum + item[field], 0)]));
  return {
    campaign_count: valid.length, ...totals,
    ctr: divide(totals.clicks, totals.impressions),
    conversion_rate: divide(totals.conversions, totals.clicks),
    cpc: divide(totals.spend, totals.clicks),
    cpa: divide(totals.spend, totals.conversions),
    roas: divide(totals.revenue, totals.spend)
  };
}

export function analyzeRows(rows) {
  const valid = [], exceptions = [];
  rows.forEach(row => {
    const campaign = (row.campaign || "").trim();
    const channel = (row.channel || "").trim();
    const date = (row.date || "").trim();
    if (!campaign || !channel) { exceptions.push({ row: row.__row, campaign, channel, date, reason: "campaign or channel is missing" }); return; }
    if (row.__hasDate && !isIsoDate(date)) {
      exceptions.push({ row: row.__row, campaign, channel, date, reason: "date must use a valid YYYY-MM-DD value" }); return;
    }
    const values = {};
    try { NUMERIC.forEach(field => { values[field] = number(row[field] ?? "", field); }); }
    catch (error) { exceptions.push({ row: row.__row, campaign, channel, date, reason: error.message }); return; }
    if (values.clicks > values.impressions) { exceptions.push({ row: row.__row, campaign, channel, date, reason: "clicks cannot exceed impressions" }); return; }
    if (values.conversions > values.clicks) { exceptions.push({ row: row.__row, campaign, channel, date, reason: "conversions cannot exceed clicks" }); return; }
    valid.push({ campaign, channel, ...(row.__hasDate ? { date } : {}), ...values,
      ctr: divide(values.clicks, values.impressions),
      conversion_rate: divide(values.conversions, values.clicks),
      cpc: divide(values.spend, values.clicks),
      cpa: divide(values.spend, values.conversions),
      roas: divide(values.revenue, values.spend)
    });
  });
  return { valid, exceptions, summary: summarizeCampaigns(valid), hasDate: rows.some(row => row.__hasDate) };
}

export function comparePeriods(rows, start, end) {
  if (!isIsoDate(start) || !isIsoDate(end) || start > end) throw new Error("Select a valid start and end date.");
  const startMs = Date.parse(start + "T00:00:00.000Z");
  const endMs = Date.parse(end + "T00:00:00.000Z");
  const durationDays = Math.round((endMs - startMs) / DAY_MS) + 1;
  const previousEnd = new Date(startMs - DAY_MS).toISOString().slice(0, 10);
  const previousStart = new Date(startMs - durationDays * DAY_MS).toISOString().slice(0, 10);
  const inRange = (item, from, to) => item.date >= from && item.date <= to;
  const current = rows.filter(item => inRange(item, start, end));
  const previous = rows.filter(item => inRange(item, previousStart, previousEnd));
  return {
    current: { start, end, summary: summarizeCampaigns(current) },
    previous: { start: previousStart, end: previousEnd, summary: summarizeCampaigns(previous) }
  };
}

export function summarizeByChannel(validRows) {
  const groups = new Map();
  validRows.forEach(item => {
    if (!groups.has(item.channel)) groups.set(item.channel, []);
    groups.get(item.channel).push(item);
  });
  return [...groups.entries()].map(([channel, items]) => {
    const totals = Object.fromEntries(NUMERIC.map(field => [
      field, items.reduce((sum, item) => sum + item[field], 0)
    ]));
    return {
      channel,
      campaign_count: items.length,
      ...totals,
      cpa: divide(totals.spend, totals.conversions),
      roas: divide(totals.revenue, totals.spend)
    };
  }).sort((a, b) => a.channel.localeCompare(b.channel));
}
