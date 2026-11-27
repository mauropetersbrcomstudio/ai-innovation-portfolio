export function classifyInvoice(input, existing = []) {
  const ref = String(input.invoiceRef || "")
    .trim()
    .toLowerCase();
  const supplier = String(input.supplier || "")
    .trim()
    .toLowerCase();
  const amount = Number(input.amount);
  const reasons = [];
  if (
    existing.some(
      (item) =>
        String(item.input?.invoiceRef || "")
          .trim()
          .toLowerCase() === ref &&
        String(item.input?.supplier || "")
          .trim()
          .toLowerCase() === supplier,
    )
  ) {
    return {
      route: "Revisão de duplicidade",
      priority: "atenção",
      reasons: [
        "Mesmo fornecedor e referência já presentes no histórico local.",
      ],
    };
  }
  if (
    !Number.isFinite(amount) ||
    amount <= 0 ||
    !/^\d{4}-\d{2}-\d{2}$/.test(input.issueDate || "") ||
    !/^\d{4}-\d{2}-\d{2}$/.test(input.dueDate || "") ||
    input.dueDate < input.issueDate
  ) {
    return {
      route: "Retenção por dados",
      priority: "atenção",
      reasons: ["Valor ou sequência de datas inválidos."],
    };
  }
  if (!String(input.purchaseOrder || "").trim()) {
    reasons.push("Referência de pedido de compra não informada.");
    return { route: "Complementação documental", priority: "atenção", reasons };
  }
  if (amount > 5000) {
    reasons.push("Valor acima do limite ilustrativo de revisão gerencial.");
    return {
      route: "Revisão gerencial",
      priority: "normal",
      reasons,
      meta: { amount },
    };
  }
  reasons.push(
    "Campos de demonstração completos; pronto para revisão de contas a pagar.",
  );
  return {
    route: "Revisão de contas a pagar",
    priority: "normal",
    reasons,
    meta: { amount },
  };
}
