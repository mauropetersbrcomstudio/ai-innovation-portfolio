"use strict";

// Synthetic, illustrative rules. No client policy is represented here.
const SCENARIOS = {
  education: {
    title: "Educação profissional", workflow: "Triagem de matrículas", icon: "EDU",
    intro: "Organize pedidos de matrícula de cursos para adultos e encaminhe exceções para revisão.",
    fields: [
      { key: "reference", label: "Referência do pedido", type: "text", required: true },
      { key: "course", label: "Curso", type: "select", options: ["Dados", "Design", "Gestão"], required: true },
      { key: "schedule", label: "Turno desejado", type: "select", options: ["Manhã", "Noite", "Ainda não definido"], required: true },
      { key: "documents", label: "Documentação recebida?", type: "select", options: ["Sim", "Não"], required: true },
      { key: "seats", label: "Vagas disponíveis", type: "number", required: true, min: 0 },
    ],
    examples: [
      { reference: "EDU-101", course: "Dados", schedule: "Noite", documents: "Sim", seats: "4" },
      { reference: "EDU-102", course: "Design", schedule: "Ainda não definido", documents: "Não", seats: "0" },
    ],
    evaluate(x) {
      const reasons = [];
      if (x.documents !== "Sim") reasons.push("Documentação pendente");
      if (x.schedule === "Ainda não definido") reasons.push("Turno a confirmar");
      if (Number(x.seats) === 0) reasons.push("Sem vagas informadas");
      return { queue: reasons.length ? "Revisão de matrícula" : "Pré-matrícula", priority: reasons.length ? "Atenção" : "Normal", reasons };
    },
  },
  retail: {
    title: "Varejo", workflow: "Exceções de devolução", icon: "RTL",
    intro: "Avalie solicitações de devolução com regras demonstrativas e decisão humana.",
    fields: [
      { key: "reference", label: "Referência da devolução", type: "text", required: true },
      { key: "days", label: "Dias desde a compra", type: "number", required: true, min: 0 },
      { key: "receipt", label: "Comprovante disponível?", type: "select", options: ["Sim", "Não"], required: true },
      { key: "condition", label: "Condição informada", type: "select", options: ["Lacrado", "Aberto", "Avaria"], required: true },
      { key: "amount", label: "Valor demonstrativo (R$)", type: "number", required: true, min: 0 },
    ],
    examples: [
      { reference: "RTL-201", days: "5", receipt: "Sim", condition: "Lacrado", amount: "120" },
      { reference: "RTL-202", days: "18", receipt: "Não", condition: "Avaria", amount: "780" },
    ],
    evaluate(x) {
      const reasons = [];
      if (Number(x.days) > 7) reasons.push("Prazo ilustrativo excedido");
      if (x.receipt !== "Sim") reasons.push("Comprovante pendente");
      if (x.condition !== "Lacrado") reasons.push("Condição requer conferência");
      if (Number(x.amount) > 500) reasons.push("Valor acima do limite ilustrativo");
      return { queue: reasons.length ? "Revisão de devolução" : "Conferência padrão", priority: reasons.length ? "Atenção" : "Normal", reasons };
    },
  },
  hospitality: {
    title: "Hotelaria", workflow: "Manutenção de quartos", icon: "HSP",
    intro: "Registre ocorrências de manutenção e destaque bloqueios e riscos para a equipe.",
    fields: [
      { key: "reference", label: "Referência da ocorrência", type: "text", required: true },
      { key: "room", label: "Código fictício do quarto", type: "text", required: true },
      { key: "category", label: "Tipo", type: "select", options: ["Elétrica", "Hidráulica", "Climatização", "Outros"], required: true },
      { key: "occupied", label: "Quarto ocupado?", type: "select", options: ["Sim", "Não"], required: true },
      { key: "safety", label: "Risco de segurança informado?", type: "select", options: ["Sim", "Não"], required: true },
    ],
    examples: [
      { reference: "HSP-301", room: "A-12", category: "Climatização", occupied: "Não", safety: "Não" },
      { reference: "HSP-302", room: "B-07", category: "Elétrica", occupied: "Sim", safety: "Sim" },
    ],
    evaluate(x) {
      const reasons = [];
      if (x.safety === "Sim") reasons.push("Risco informado: avaliação imediata da equipe");
      if (x.occupied === "Sim") reasons.push("Quarto ocupado: coordenar atendimento");
      return { queue: x.safety === "Sim" ? "Escalação operacional" : "Manutenção", priority: x.safety === "Sim" ? "Urgente" : x.occupied === "Sim" ? "Atenção" : "Normal", reasons };
    },
  },
  manufacturing: {
    title: "Indústria", workflow: "Desvios de qualidade", icon: "MFG",
    intro: "Classifique desvios de lotes fictícios e registre uma decisão de contenção.",
    fields: [
      { key: "reference", label: "Referência do desvio", type: "text", required: true },
      { key: "batch", label: "Lote fictício", type: "text", required: true },
      { key: "severity", label: "Gravidade informada", type: "select", options: ["Baixa", "Média", "Alta"], required: true },
      { key: "evidence", label: "Evidência registrada?", type: "select", options: ["Sim", "Não"], required: true },
      { key: "released", label: "Lote liberado?", type: "select", options: ["Sim", "Não"], required: true },
    ],
    examples: [
      { reference: "MFG-401", batch: "L-004", severity: "Baixa", evidence: "Sim", released: "Não" },
      { reference: "MFG-402", batch: "L-009", severity: "Alta", evidence: "Não", released: "Sim" },
    ],
    evaluate(x) {
      const reasons = [];
      if (x.severity === "Alta") reasons.push("Gravidade alta informada");
      if (x.evidence !== "Sim") reasons.push("Evidência pendente");
      if (x.released === "Sim") reasons.push("Lote informado como liberado");
      return { queue: reasons.length ? "Qualidade: revisão" : "Qualidade: análise", priority: x.severity === "Alta" || x.released === "Sim" ? "Urgente" : reasons.length ? "Atenção" : "Normal", reasons };
    },
  },
};

function validate(scenario, data) {
  if (!Object.hasOwn(SCENARIOS, scenario)) throw new Error("Cenário inválido");
  const fields = SCENARIOS[scenario].fields;
  const record = {};
  for (const field of fields) {
    const value = String(data[field.key] ?? "").trim();
    if (field.required && !value) throw new Error(`${field.label}: campo obrigatório`);
    if (value.length > 100) throw new Error(`${field.label}: máximo de 100 caracteres`);
    if (field.options && !field.options.includes(value)) throw new Error(`${field.label}: opção inválida`);
    if (field.type === "number" && (!Number.isFinite(Number(value)) || Number(value) < field.min)) throw new Error(`${field.label}: número inválido`);
    record[field.key] = value;
  }
  return record;
}

function triage(scenario, data) {
  const record = validate(scenario, data);
  return { ...record, ...SCENARIOS[scenario].evaluate(record) };
}

if (typeof module !== "undefined") module.exports = { SCENARIOS, validate, triage };
