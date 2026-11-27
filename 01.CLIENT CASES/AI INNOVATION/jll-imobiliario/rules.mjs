const territory = {
  "São Paulo": "Equipe comercial · SP",
  "Rio de Janeiro": "Equipe comercial · RJ",
  "Belo Horizonte": "Equipe comercial · MG",
};

export function classifyLead(input, existing = []) {
  const reference = String(input.reference || "")
    .trim()
    .toLowerCase();
  const email = String(input.email || "")
    .trim()
    .toLowerCase();
  const area = Number(input.area);
  const budget = Number(input.budget);
  const reasons = [];
  if (
    existing.some(
      (item) =>
        String(item.input?.reference || "")
          .trim()
          .toLowerCase() === reference ||
        String(item.input?.email || "")
          .trim()
          .toLowerCase() === email,
    )
  ) {
    reasons.push("Referência ou e-mail já registrado nesta demonstração.");
    return {
      route: "Revisão de duplicidade",
      priority: "atenção",
      reasons,
      meta: { score: 0 },
    };
  }
  if (
    !Number.isFinite(area) ||
    area <= 0 ||
    !Number.isFinite(budget) ||
    budget <= 0
  ) {
    reasons.push("Área e orçamento devem ser valores positivos.");
    return {
      route: "Revisão de dados",
      priority: "atenção",
      reasons,
      meta: { score: 0 },
    };
  }
  if (!territory[input.city]) {
    reasons.push("Região sem fila comercial configurada neste exemplo.");
    return {
      route: "Revisão de território",
      priority: "atenção",
      reasons,
      meta: { score: 0 },
    };
  }
  let score = 35;
  if (area >= 250) score += 20;
  if (budget >= 15000) score += 20;
  if (input.timeline === "Imediato" || input.timeline === "Até 30 dias")
    score += 15;
  if (input.propertyType === "Escritório" || input.propertyType === "Galpão")
    score += 10;
  reasons.push("Pontuação ilustrativa de adequação: " + score + "/100.");
  reasons.push("Encaminhamento sugerido por região informada.");
  return {
    route: score >= 60 ? territory[input.city] : "Revisão comercial",
    priority: input.timeline === "Imediato" ? "prioritário" : "normal",
    reasons,
    meta: { score },
  };
}
