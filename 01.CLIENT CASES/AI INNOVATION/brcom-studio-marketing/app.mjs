import {
  startCase,
  escapeHtml as esc,
  formatMoney,
} from "../workflow-core.mjs";
import { classifyCampaign } from "./rules.mjs";

const examples = [
  {
    campaignId: "CMP-401",
    campaignName: "Horizontes 2027",
    destination: "https://example.com/horizontes",
    utmSource: "newsletter",
    utmMedium: "email",
    utmCampaign: "horizontes_2027",
    startDate: "2026-12-01",
    endDate: "2026-12-20",
    budget: 5000,
  },
  {
    campaignId: "CMP-402",
    campaignName: "Lançamento Exemplo",
    destination: "https://example.com/lancamento?utm_source=antigo",
    utmSource: "social",
    utmMedium: "paid",
    utmCampaign: "lancamento_exemplo",
    startDate: "2026-12-05",
    endDate: "2026-12-18",
    budget: 8000,
  },
];

function card(item) {
  const data = item.input;
  const day = String(data.startDate || "").slice(8, 10);
  const month = String(data.startDate || "").slice(5, 7);
  const reasons = item.reasons
    .map((reason) => "<li>" + esc(reason) + "</li>")
    .join("");
  const decision = item.decision
    ? '<p class="decision"><strong>' +
      esc(item.decision.label) +
      "</strong> · " +
      esc(item.decision.note) +
      "</p>"
    : '<div class="review-control"><input data-decision-note aria-label="Justificativa para ' +
      esc(data.campaignId) +
      '" placeholder="Justificativa obrigatória"><div><button type="button" data-decision="Revisado na simulação">Registrar revisão</button><button type="button" data-decision="Solicitar ajustes">Solicitar ajustes</button></div></div>';
  const link = item.meta?.trackingUrl
    ? '<span class="url">' + esc(item.meta.trackingUrl) + "</span>"
    : '<span class="url">Link de acompanhamento indisponível até corrigir as pendências.</span>';
  return (
    '<article class="campaign ' +
    (item.priority === "atenção" ? "blocked" : "") +
    '" data-record-id="' +
    esc(item.id) +
    '"><div class="campaign-date"><strong>' +
    esc(day) +
    "." +
    esc(month) +
    '</strong><span>INÍCIO</span></div><div class="campaign-main"><h3>' +
    esc(data.campaignName) +
    "</h3><p>" +
    esc(data.campaignId) +
    " · " +
    esc(formatMoney(data.budget)) +
    "</p>" +
    link +
    '</div><div class="campaign-status"><strong>' +
    esc(item.route) +
    "</strong><small>" +
    esc(data.utmSource) +
    " / " +
    esc(data.utmMedium) +
    "</small></div><details><summary>Checklist e decisão</summary><ul>" +
    reasons +
    "</ul>" +
    decision +
    "</details></article>"
  );
}

function render(records) {
  document.getElementById("total").textContent = String(
    records.length,
  ).padStart(2, "0");
  document.getElementById("ready").textContent = String(
    records.filter((item) => item.route === "Pronto para revisão").length,
  ).padStart(2, "0");
  document.getElementById("blocked").textContent = String(
    records.filter((item) => item.priority === "atenção").length,
  ).padStart(2, "0");
  document.getElementById("decided").textContent = String(
    records.filter((item) => item.decision).length,
  ).padStart(2, "0");
  document.getElementById("campaign-list").innerHTML = records.length
    ? records.map(card).join("")
    : '<p class="empty">Carregue um exemplo para ver o release board.</p>';
}

window.casePrototype = startCase({
  key: "brcom-studio-marketing",
  classify: classifyCampaign,
  render,
  examples,
});
