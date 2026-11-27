import {
  startCase,
  escapeHtml as esc,
  formatMoney,
} from "../workflow-core.mjs";
import { classifyRequest } from "./rules.mjs";

const examples = [
  {
    reference: "HNG-201",
    project: "Obra Alfa",
    category: "Material",
    costCode: "MAT-04",
    amount: 2300,
    remaining: 8000,
    urgency: "Normal",
    supplierVerified: true,
    evidenceAttached: true,
  },
  {
    reference: "HNG-202",
    project: "Obra Beta",
    category: "Equipamento",
    costCode: "EQP-09",
    amount: 12500,
    remaining: 9000,
    urgency: "Urgente",
    supplierVerified: false,
    evidenceAttached: false,
  },
];

function row(item) {
  const data = item.input;
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
      esc(data.reference) +
      '" placeholder="Justificativa obrigatória"><div><button type="button" data-decision="Encaminhado na simulação">Encaminhar</button><button type="button" data-decision="Solicitar complementação">Pedir dados</button></div></div>';
  return (
    '<article class="request ' +
    (item.priority === "atenção" ? "alert" : "") +
    '" data-record-id="' +
    esc(item.id) +
    '"><div class="request-top"><div><strong>' +
    esc(data.reference) +
    "</strong><small>" +
    esc(data.project) +
    " · " +
    esc(data.category) +
    " / " +
    esc(data.costCode) +
    '</small></div><span class="amount">' +
    esc(formatMoney(data.amount)) +
    '</span><span class="route">' +
    esc(item.route) +
    "</span></div><details><summary>Ver critérios e registrar decisão</summary><ul>" +
    reasons +
    "</ul>" +
    decision +
    "</details></article>"
  );
}

function render(records) {
  const exceptions = records.filter(
    (item) =>
      item.priority === "atenção" ||
      item.route.includes("Diligência") ||
      item.route.includes("Complementação"),
  );
  document.getElementById("total").textContent = String(
    records.length,
  ).padStart(2, "0");
  document.getElementById("pending").textContent = String(
    records.filter((item) => !item.decision).length,
  ).padStart(2, "0");
  document.getElementById("exceptions").textContent = String(
    exceptions.length,
  ).padStart(2, "0");
  document.getElementById("decided").textContent = String(
    records.filter((item) => item.decision).length,
  ).padStart(2, "0");
  document.getElementById("request-list").innerHTML = records.length
    ? records.map(row).join("")
    : '<p class="empty">Use um cenário de exemplo para iniciar a fila.</p>';
}

window.casePrototype = startCase({
  key: "hangar-construcao-civil",
  classify: classifyRequest,
  render,
  examples,
});
