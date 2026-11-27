export function classifyCampaign(input, existing = []) {
  const reasons = [];
  const campaignId = String(input.campaignId || "")
    .trim()
    .toLowerCase();
  if (
    existing.some(
      (item) =>
        String(item.input?.campaignId || "")
          .trim()
          .toLowerCase() === campaignId,
    )
  )
    reasons.push("ID de campanha duplicado neste navegador.");
  let url;
  try {
    url = new URL(input.destination);
    if (
      !["http:", "https:"].includes(url.protocol) ||
      url.username ||
      url.password
    )
      reasons.push("Destino deve ser HTTP(S) e não conter credenciais.");
    if (
      ["utm_source", "utm_medium", "utm_campaign"].some((key) =>
        url.searchParams.has(key),
      )
    )
      reasons.push(
        "Destino já contém UTMs que colidiriam com os valores informados.",
      );
  } catch {
    reasons.push("URL de destino inválida.");
  }
  if (
    !String(input.utmSource || "").trim() ||
    !String(input.utmMedium || "").trim() ||
    !String(input.utmCampaign || "").trim()
  )
    reasons.push("Fonte, meio e campanha UTM são obrigatórios.");
  if (
    !/^\d{4}-\d{2}-\d{2}$/.test(input.startDate || "") ||
    !/^\d{4}-\d{2}-\d{2}$/.test(input.endDate || "") ||
    input.endDate < input.startDate
  )
    reasons.push("Datas de início e fim inválidas ou invertidas.");
  const budget = Number(input.budget);
  if (!Number.isFinite(budget) || budget < 0)
    reasons.push("Orçamento deve ser um número não negativo.");
  if (reasons.length)
    return {
      route: "Correção necessária",
      priority: "atenção",
      reasons,
      meta: { trackingUrl: "" },
    };
  url.searchParams.set("utm_source", input.utmSource.trim());
  url.searchParams.set("utm_medium", input.utmMedium.trim());
  url.searchParams.set("utm_campaign", input.utmCampaign.trim());
  return {
    route: "Pronto para revisão",
    priority: "normal",
    reasons: ["Metadados passaram apenas nas verificações demonstrativas."],
    meta: { trackingUrl: url.toString() },
  };
}
