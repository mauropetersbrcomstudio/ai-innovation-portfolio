import {
  startCase,
  escapeHtml as esc,
  formatMoney,
} from "../workflow-core.mjs";
import { classifyLead } from "./rules.mjs";

const examples = [
  {
    reference: "JLL-101",
    company: "Empresa Horizonte",
    email: "contato.horizonte@example.com",
    purpose: "Locação",
    propertyType: "Escritório",
    city: "São Paulo",
    timeline: "Até 30 dias",
    area: 450,
    budget: 27000,
  },
  {
    reference: "JLL-102",
    company: "Grupo Exemplo",
    email: "grupo@example.com",
    purpose: "Compra",
    propertyType: "Galpão",
    city: "Outra região",
    timeline: "Imediato",
    area: 1200,
    budget: 45000,
  },
];

function card(item) {
  const data = item.input;
  const reasons = item.reasons
    .map((reason) => "<li>" + esc(reason) + "</li>")
    .join("");
  const decision = item.decision
    ? '<div class="decision"><strong>' +
      esc(item.decision.label) +
      "</strong><br>" +
      esc(item.decision.note) +
      "</div>"
    : '<div class="review-control"><input data-decision-note aria-label="Justificativa da decisão para ' +
      esc(data.reference) +
      '" placeholder="Justificativa obrigatória"><div><button type="button" data-decision="Encaminhado na simulação">Encaminhar</button><button type="button" data-decision="Solicitar dados">Solicitar dados</button></div></div>';
  return (
    '<article class="lead-card" data-record-id="' +
    esc(item.id) +
    '"><header><strong>' +
    esc(data.company) +
    "</strong><span>" +
    esc(item.priority.toUpperCase()) +
    "</span></header><small>" +
    esc(data.reference) +
    " · " +
    esc(data.email) +
    '</small><span class="route">' +
    esc(item.route) +
    '</span><div class="facts"><span>' +
    esc(data.propertyType) +
    "</span><span>" +
    esc(data.city) +
    "</span><span>" +
    esc(data.area) +
    " m²</span><span>" +
    esc(formatMoney(data.budget)) +
    "</span></div><ul>" +
    reasons +
    "</ul>" +
    decision +
    "</article>"
  );
}

function render(records) {
  const needsReview = (item) => item.route.startsWith("Revisão");
  const review = records.filter(needsReview);
  const routed = records.filter((item) => !needsReview(item));
  document.getElementById("total").textContent = String(records.length);
  document.getElementById("routed").textContent = String(routed.length);
  document.getElementById("review").textContent = String(review.length);
  document.getElementById("decided").textContent = String(
    records.filter((item) => item.decision).length,
  );
  document.getElementById("routed-count").textContent = String(routed.length);
  document.getElementById("review-count").textContent = String(review.length);
  document.getElementById("routed-list").innerHTML = routed.length
    ? routed.map(card).join("")
    : '<p class="empty">Carregue o exemplo padrão para começar.</p>';
  document.getElementById("review-list").innerHTML = review.length
    ? review.map(card).join("")
    : '<p class="empty">Nenhuma exceção registrada.</p>';
}

window.casePrototype = startCase({
  key: "jll-imobiliario",
  classify: classifyLead,
  render,
  examples,
});
