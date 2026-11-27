import {
  startCase,
  escapeHtml as esc,
  formatMoney,
} from "../workflow-core.mjs";
import { classifyInvoice } from "./rules.mjs";

const examples = [
  {
    invoiceRef: "NF-301",
    supplier: "Fornecedor Horizonte",
    purchaseOrder: "OC-301",
    amount: 3200,
    issueDate: "2026-11-18",
    dueDate: "2026-12-10",
  },
  {
    invoiceRef: "NF-302",
    supplier: "Fornecedor Exemplo",
    purchaseOrder: "",
    amount: 7800,
    issueDate: "2026-11-20",
    dueDate: "2026-12-15",
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
      esc(data.invoiceRef) +
      '" placeholder="Justificativa obrigatória"><div><button type="button" data-decision="Revisado na simulação">Registrar revisão</button><button type="button" data-decision="Solicitar documento">Pedir documento</button></div></div>';
  return (
    '<article class="invoice ' +
    (item.priority === "atenção" ? "exception" : "") +
    '" data-record-id="' +
    esc(item.id) +
    '"><div class="invoice-top"><div><strong>' +
    esc(data.invoiceRef) +
    "</strong><small>" +
    esc(data.supplier) +
    " · Pedido " +
    esc(data.purchaseOrder || "não informado") +
    '</small></div><span class="money">' +
    esc(formatMoney(data.amount)) +
    '</span><span><span class="badge">' +
    esc(item.route) +
    "</span></span></div><details><summary>Motivos e decisão humana</summary><ul>" +
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
  document.getElementById("ap").textContent = String(
    records.filter(
      (item) =>
        item.route === "Revisão de contas a pagar" ||
        item.route === "Revisão gerencial",
    ).length,
  ).padStart(2, "0");
  document.getElementById("exceptions").textContent = String(
    records.filter((item) => item.priority === "atenção").length,
  ).padStart(2, "0");
  document.getElementById("decided").textContent = String(
    records.filter((item) => item.decision).length,
  ).padStart(2, "0");
  document.getElementById("invoice-list").innerHTML = records.length
    ? records.map(row).join("")
    : '<p class="empty">Use um exemplo para iniciar a conferência.</p>';
}

window.casePrototype = startCase({
  key: "dimensa-bpo-financeiro",
  classify: classifyInvoice,
  render,
  examples,
});
