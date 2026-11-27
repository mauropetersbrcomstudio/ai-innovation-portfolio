export function classifyRequest(input, existing = []) {
  const reference = String(input.reference || "")
    .trim()
    .toLowerCase();
  const amount = Number(input.amount);
  const remaining = Number(input.remaining);
  const reasons = [];
  if (
    existing.some(
      (item) =>
        String(item.input?.reference || "")
          .trim()
          .toLowerCase() === reference,
    )
  ) {
    return {
      route: "Revisão de duplicidade",
      priority: "atenção",
      reasons: ["Referência já registrada neste navegador."],
    };
  }
  if (
    !Number.isFinite(amount) ||
    amount <= 0 ||
    !Number.isFinite(remaining) ||
    remaining < 0
  ) {
    return {
      route: "Revisão de dados",
      priority: "atenção",
      reasons: ["Valor solicitado ou saldo informado inválido."],
    };
  }
  if (amount > remaining)
    reasons.push("Valor acima do saldo informado para esta demonstração.");
  if (!input.supplierVerified)
    reasons.push("Fornecedor ainda não verificado no exemplo.");
  if (!input.evidenceAttached)
    reasons.push("Documento de suporte não informado.");
  if (input.urgency === "Urgente")
    reasons.push("Urgência declarada requer revisão prioritária.");
  let route = "Gestor da obra";
  if (amount > remaining) route = "Diretoria · exceção orçamentária";
  else if (!input.supplierVerified) route = "Diligência de fornecedor";
  else if (!input.evidenceAttached) route = "Complementação documental";
  else if (amount > 5000) route = "Financeiro";
  else if (amount > 1500) route = "Compras";
  if (!reasons.length)
    reasons.push(
      "Campos de exemplo completos; encaminhamento por limite ilustrativo.",
    );
  return {
    route,
    priority:
      amount > remaining || input.urgency === "Urgente" ? "atenção" : "normal",
    reasons,
    meta: { amount, remaining },
  };
}
