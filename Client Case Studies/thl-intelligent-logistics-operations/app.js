(() => {
  "use strict";
  const KEY = "thl-intelligent-logistics-mvp-v1";
  const emptyState = { shipments: [], systems: [], occurrences: [], documents: [], events: [], pods: [], collections: [], terminal: [], audit: [] };
  const shipmentStatuses = ["Solicitação registrada","Em cotação / planejamento","Coleta planejada","Coletada","Em triagem / armazenagem","Consolidada","Em transferência","Em distribuição","Entregue — aguardando comprovante","Concluída","Em ocorrência","Cancelada"];
  const occurrenceStatuses = ["Aberta","Em análise","Aguardando informação","Resolvida","Encerrada"];
  let state = loadState();
  const $ = (id) => document.getElementById(id);
  const now = () => new Date().toISOString();
  function loadState() {
    try {
      const saved = JSON.parse(localStorage.getItem(KEY) || "null");
      return saved && typeof saved === "object" ? { ...emptyState, ...saved } : structuredClone(emptyState);
    } catch { return structuredClone(emptyState); }
  }
  function persist() { localStorage.setItem(KEY, JSON.stringify(state)); render(); }
  function log(action, detail) {
    state.audit.unshift({ id: crypto.randomUUID(), at: now(), action, detail });
    state.audit = state.audit.slice(0, 500);
  }
  function esc(value) {
    return String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" }[c]));
  }
  function formData(form) { return Object.fromEntries(new FormData(form).entries()); }
  function dateLabel(value) {
    if (!value) return "Data não informada";
    const d = new Date(value);
    return Number.isNaN(d.getTime()) ? value : d.toLocaleString("pt-BR");
  }
  function openView(name) {
    document.querySelectorAll(".view").forEach(v => v.classList.toggle("active", v.id === "view-" + name));
    document.querySelectorAll(".nav-button").forEach(b => b.classList.toggle("active", b.dataset.view === name));
    const labels = { overview:"VISÃO GERAL", shipments:"CARGAS", discovery:"DESCOBERTA TECNOLÓGICA", occurrences:"OCORRÊNCIAS", documents:"DOCUMENTOS", tracking:"MOVIMENTAÇÕES", fleet:"COLETA E FROTA", terminal:"TERMINAL / CONSOLIDAÇÃO", audit:"AUDITORIA" };
    $("section-name").textContent = labels[name] || name.toUpperCase();
  }
  function render() {
    $("metric-loads").textContent = state.shipments.length;
    $("metric-transit").textContent = state.shipments.filter(x => x.status === "Em transferência" || x.status === "Em distribuição").length;
    $("metric-open-occurrences").textContent = state.occurrences.filter(x => !["Resolvida","Encerrada"].includes(x.status)).length;
    $("metric-systems").textContent = state.systems.length;
    $("metric-documents").textContent = state.documents.length;
    const today = new Date();
    const overdue = state.shipments.filter(x => x.dueDate && !["Concluída","Cancelada"].includes(x.status) && new Date(x.dueDate + "T23:59:59") < today);
    $("metric-overdue").textContent = overdue.length;
    $("metric-collections").textContent = state.collections.length;
    $("metric-terminal").textContent = state.terminal.length;
    $("metric-events").textContent = state.events.length;
    $("metric-pods").textContent = state.pods.length;
    const modalities = [...new Set(state.shipments.map(x => x.modality || "Não informada"))];
    $("modality-summary").className = modalities.length ? "record-list" : "record-list empty";
    $("modality-summary").innerHTML = modalities.length ? modalities.map(m => {
      const count = state.shipments.filter(x => (x.modality || "Não informada") === m).length;
      return '<article class="record"><div class="record-top"><strong>'+esc(m)+'</strong><span class="record-tag">'+count+' carga(s)</span></div></article>';
    }).join("") : "Nenhuma carga cadastrada.";
    const refs = [...new Set(state.shipments.map(x => x.reference).filter(Boolean))];
    $("shipment-reference-options").innerHTML = refs.map(ref => '<option value="'+esc(ref)+'"></option>').join("");
    $("nav-event-count").textContent = state.events.length;
    $("event-total").textContent = state.events.length;
    $("pod-total").textContent = state.pods.length;
    $("nav-collection-count").textContent = state.collections.length;
    $("collection-total").textContent = state.collections.length;
    $("nav-terminal-count").textContent = state.terminal.length;
    $("terminal-total").textContent = state.terminal.length;
    $("terminal-list").className = state.terminal.length ? "record-list" : "record-list empty";
    $("terminal-list").innerHTML = state.terminal.length ? state.terminal.map(terminalCard).join("") : "Nenhuma operação registrada.";
    $("collection-list").className = state.collections.length ? "record-list" : "record-list empty";
    $("collection-list").innerHTML = state.collections.length ? state.collections.map(collectionCard).join("") : "Nenhum checklist registrado.";
    $("event-list").className = state.events.length ? "record-list" : "record-list empty";
    $("event-list").innerHTML = state.events.length ? state.events.map(eventCard).join("") : "Nenhuma movimentação registrada.";
    $("pod-list").className = state.pods.length ? "record-list" : "record-list empty";
    $("pod-list").innerHTML = state.pods.length ? state.pods.map(podCard).join("") : "Nenhum POD registrado.";
    $("nav-document-count").textContent = state.documents.length;
    $("document-total").textContent = state.documents.length;
    $("nav-load-count").textContent = state.shipments.length;
    $("nav-occurrence-count").textContent = state.occurrences.filter(x => !["Resolvida","Encerrada"].includes(x.status)).length;
    $("shipment-total").textContent = state.shipments.length;
    $("system-total").textContent = state.systems.length;
    $("occurrence-total").textContent = state.occurrences.length;
    $("recent-loads").className = state.shipments.length ? "record-list" : "empty";
    $("recent-loads").innerHTML = state.shipments.length ? state.shipments.slice(0,5).map(shipmentCard).join("") : "Nenhuma carga cadastrada. Registre uma carga para iniciar o acompanhamento.";
    $("shipment-list").className = state.shipments.length ? "record-list" : "record-list empty";
    $("shipment-list").innerHTML = state.shipments.length ? state.shipments.map(shipmentCard).join("") : "Nenhuma carga registrada.";
    $("system-list").className = state.systems.length ? "record-list" : "record-list empty";
    $("system-list").innerHTML = state.systems.length ? state.systems.map(systemCard).join("") : "Nenhum sistema ou recurso cadastrado.";
    $("occurrence-list").className = state.occurrences.length ? "record-list" : "record-list empty";
    $("occurrence-list").innerHTML = state.occurrences.length ? state.occurrences.map(occurrenceCard).join("") : "Nenhuma ocorrência registrada.";
    $("document-list").className = state.documents.length ? "record-list" : "record-list empty";
    $("document-list").innerHTML = state.documents.length ? state.documents.map(documentCard).join("") : "Nenhum documento registrado.";
    $("audit-list").className = state.audit.length ? "record-list" : "record-list empty";
    $("audit-list").innerHTML = state.audit.length ? state.audit.map(auditCard).join("") : "Nenhum evento registrado.";
  }
  function shipmentCard(x) {
    const options = shipmentStatuses.map(status => '<option'+(status === x.status ? ' selected' : '')+'>'+esc(status)+'</option>').join("");
    const isOverdue = x.dueDate && !["Concluída","Cancelada"].includes(x.status) && new Date(x.dueDate + "T23:59:59") < new Date();
    const due = x.dueDate ? '<small>Previsão informada: '+dateLabel(x.dueDate)+(isOverdue ? ' · Data ultrapassada' : '')+'</small>' : '<small>Previsão não informada</small>';
    return '<article class="record"><div class="record-top"><div><strong>'+esc(x.reference)+'</strong><small>'+esc(x.modality)+' · '+esc(x.origin || "Origem não informada")+' → '+esc(x.destination || "Destino não informado")+'</small></div></div><p>'+esc(x.goods || "Mercadoria não informada")+' · '+esc(x.vehicle || "Veículo não definido")+'</p>'+due+'<label class="record-control">Atualizar status<select data-shipment-status="'+esc(x.id)+'">'+options+'</select></label><small>Registrada em '+dateLabel(x.createdAt)+'</small></article>';
  }
  function systemCard(x) {
    return '<article class="record"><div class="record-top"><div><strong>'+esc(x.name || "Sistema não identificado")+'</strong><small>'+esc(x.category)+' · '+esc(x.owner || "Área não informada")+'</small></div><span class="record-tag">'+esc(x.status)+'</span></div><p>'+esc(x.purpose || "Finalidade não informada")+'</p><small>Formato: '+esc(x.format)+' · Frequência: '+esc(x.frequency)+'</small>'+(x.limitations?'<small>Limitações: '+esc(x.limitations)+'</small>':"")+'</article>';
  }
  function occurrenceCard(x) {
    const alert = x.priority === "Crítica" || x.priority === "Alta";
    const done = ["Resolvida","Encerrada"].includes(x.status);
    const options = occurrenceStatuses.map(status => '<option'+(status === x.status ? ' selected' : '')+'>'+esc(status)+'</option>').join("");
    return '<article class="record"><div class="record-top"><div><strong>'+esc(x.category)+'</strong><small>'+esc(x.reference || "Carga não vinculada")+' · '+esc(x.owner || "Responsável não definido")+'</small></div><span class="record-tag '+(done?"done":alert?"alert":"")+'">'+esc(x.priority)+'</span></div><p>'+esc(x.description)+'</p><label class="record-control">Atualizar tratativa<select data-occurrence-status="'+esc(x.id)+'">'+options+'</select></label><small>Registrada em '+dateLabel(x.createdAt)+'</small></article>';
  }
  function documentCard(x) {
    return '<article class="record"><div class="record-top"><div><strong>'+esc(x.type)+'</strong><small>'+esc(x.reference || "Carga não vinculada")+' · '+esc(x.documentRef || "Referência não informada")+'</small></div><span class="record-tag">'+esc(x.status)+'</span></div>'+(x.notes?'<p>'+esc(x.notes)+'</p>':"")+'<small>Registrado em '+dateLabel(x.createdAt)+'</small></article>';
  }
  function eventCard(x) { return `<article class="record"><div class="record-top"><div><strong>${esc(x.stage)}</strong><small>${esc(x.reference)} · ${esc(x.location || "Local não informado")}</small></div><span class="record-tag">${esc(x.result)}</span></div><p>${esc(x.notes || "Sem observações")}</p><small>Evento: ${dateLabel(x.occurredAt)} · Registrado: ${dateLabel(x.createdAt)}</small></article>`; }
  function podCard(x) { return `<article class="record"><div class="record-top"><div><strong>${esc(x.reference)}</strong><small>${esc(x.evidenceType)} · Entrega: ${dateLabel(x.deliveryDate)}</small></div><span class="record-tag">${esc(x.status)}</span></div><small>Referência: ${esc(x.evidenceRef || "Não informada")}</small></article>`; }
  function collectionCard(x) { return `<article class="record"><div class="record-top"><div><strong>${esc(x.reference)}</strong><small>${esc(x.vehicle)} · ${esc(x.owner || "Responsável não informado")}</small></div><span class="record-tag">${esc(x.result)}</span></div><p>Volumes: ${esc(x.checkedPackages || "Não informado")} conferidos / ${esc(x.expectedPackages || "Não informado")} previstos</p><small>Integridade: ${esc(x.integrity)} · Etiquetas: ${esc(x.labeling)}</small>${x.notes ? `<p>${esc(x.notes)}</p>` : ""}<small>Registrado em ${dateLabel(x.createdAt)}</small></article>`; }
  function terminalCard(x) {
    return '<article class="record"><div class="record-top"><div><strong>'+esc(x.reference)+'</strong><small>'+esc(x.flow)+' · '+esc(x.applicability)+'</small></div><span class="record-tag">'+esc(x.stage)+'</span></div><p>Manifesto: '+esc(x.manifest)+' · Etiquetas: '+esc(x.labeling)+'</p><p>Armazenagem: '+esc(x.storage)+' · Consolidação: '+esc(x.consolidation)+'</p><small>Destino: '+esc(x.destination || "Não informado")+' · Janela: '+esc(x.dispatchWindow || "Não informada")+'</small><small>Evento: '+dateLabel(x.occurredAt)+' · Registrado: '+dateLabel(x.createdAt)+'</small>'+(x.notes?'<p>'+esc(x.notes)+'</p>':"")+'</article>';
  }
  function auditCard(x) {
    return '<article class="record"><div class="record-top"><strong>'+esc(x.action)+'</strong><small>'+dateLabel(x.at)+'</small></div><p>'+esc(x.detail)+'</p></article>';
  }
  document.addEventListener("change", e => {
    const shipmentId = e.target?.dataset?.shipmentStatus;
    const occurrenceId = e.target?.dataset?.occurrenceStatus;
    if (shipmentId) {
      const item = state.shipments.find(x => x.id === shipmentId);
      if (!item || !shipmentStatuses.includes(e.target.value)) return;
      item.status = e.target.value;
      log("Status da carga atualizado", item.reference + " → " + item.status);
      persist();
    }
    if (occurrenceId) {
      const item = state.occurrences.find(x => x.id === occurrenceId);
      if (!item || !occurrenceStatuses.includes(e.target.value)) return;
      item.status = e.target.value;
      log("Status da ocorrência atualizado", item.category + " → " + item.status);
      persist();
    }
  });
  $("shipment-form").addEventListener("submit", e => {
    e.preventDefault();
    const data = formData(e.currentTarget);
    data.id = crypto.randomUUID(); data.createdAt = now();
    state.shipments.unshift(data); log("Carga registrada", data.reference + " · " + data.modality);
    e.currentTarget.reset(); persist();
  });
  $("discovery-form").addEventListener("submit", e => {
    e.preventDefault();
    const data = formData(e.currentTarget);
    data.id = crypto.randomUUID(); data.createdAt = now();
    state.systems.unshift(data); log("Recurso tecnológico mapeado", data.category + " · " + (data.name || "Não identificado") + " · " + data.status);
    e.currentTarget.reset(); persist();
  });
  $("terminal-form").addEventListener("submit", e => {
    e.preventDefault();
    const data = formData(e.currentTarget);
    data.id = crypto.randomUUID(); data.createdAt = now();
    state.terminal.unshift(data);
    const terminalStatus = {
      "Consolidada":"Consolidada",
      "Pronto para expedição":"Consolidada",
      "Expedido":"Em transferência",
      "Com divergência":"Em ocorrência"
    }[data.stage];
    const terminalShipment = state.shipments.find(x => x.reference.trim().toLowerCase() === data.reference.trim().toLowerCase());
    if (terminalShipment && terminalStatus) {
      const previousStatus = terminalShipment.status;
      terminalShipment.status = terminalStatus;
      log("Status da carga atualizado por terminal", terminalShipment.reference + " · " + previousStatus + " → " + terminalStatus);
    }
    log("Operação de terminal registrada", data.reference + " · " + data.flow + " · " + data.stage);
    e.currentTarget.reset(); persist();
  });
  $("collection-form").addEventListener("submit", e => {
    e.preventDefault();
    const data = formData(e.currentTarget);
    data.id = crypto.randomUUID(); data.createdAt = now();
    state.collections.unshift(data);
    log("Checklist de coleta registrado", data.reference + " · " + data.vehicle + " · " + data.result);
    e.currentTarget.reset(); persist();
  });
  $("event-form").addEventListener("submit", e => {
    e.preventDefault(); const data = formData(e.currentTarget);
    data.id = crypto.randomUUID(); data.createdAt = now(); state.events.unshift(data);
    const eventStatus = {
      "Transferência rodoviária":"Em transferência",
      "Chegada ao terminal / filial":"Em triagem / armazenagem",
      "Triagem / desconsolidação":"Em triagem / armazenagem",
      "Em distribuição":"Em distribuição",
      "Entrega realizada":"Entregue — aguardando comprovante",
      "Retorno / insucesso":"Em ocorrência"
    }[data.stage];
    const linkedShipment = state.shipments.find(x => x.reference.trim().toLowerCase() === data.reference.trim().toLowerCase());
    if (linkedShipment && eventStatus) {
      const previousStatus = linkedShipment.status;
      linkedShipment.status = eventStatus;
      log("Status da carga atualizado por movimentação", linkedShipment.reference + " · " + previousStatus + " → " + eventStatus);
    }
    log("Movimentação registrada", data.reference + " · " + data.stage + " · " + data.result);
    e.currentTarget.reset(); persist();
  });
  $("pod-form").addEventListener("submit", e => {
    e.preventDefault(); const data = formData(e.currentTarget);
    data.id = crypto.randomUUID(); data.createdAt = now(); state.pods.unshift(data);
    const podShipment = state.shipments.find(x => x.reference.trim().toLowerCase() === data.reference.trim().toLowerCase());
    if (podShipment && data.status === "Conferido manualmente") {
      const previousStatus = podShipment.status;
      podShipment.status = "Concluída";
      log("Status da carga atualizado por conferência de POD", podShipment.reference + " · " + previousStatus + " → Concluída");
    }
    log("Status de POD registrado", data.reference + " · " + data.status);
    e.currentTarget.reset(); persist();
  });
  $("document-form").addEventListener("submit", e => {
    e.preventDefault();
    const data = formData(e.currentTarget);
    data.id = crypto.randomUUID(); data.createdAt = now();
    state.documents.unshift(data); log("Documento registrado", data.type + " · " + (data.documentRef || "Referência não informada"));
    e.currentTarget.reset(); persist();
  });
  $("occurrence-form").addEventListener("submit", e => {
    e.preventDefault();
    const data = formData(e.currentTarget);
    data.id = crypto.randomUUID(); data.createdAt = now();
    state.occurrences.unshift(data); log("Ocorrência registrada", data.category + " · " + data.priority + " · " + (data.reference || "Sem carga vinculada"));
    e.currentTarget.reset(); persist();
  });
  function download(filename, payload) {
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type:"application/json" });
    const url = URL.createObjectURL(blob); const a = document.createElement("a");
    a.href = url; a.download = filename; a.click(); URL.revokeObjectURL(url);
  }
  $("export-button").addEventListener("click", () => download("thl-logistics-data.json", { exportedAt:now(), ...state }));
  $("export-audit").addEventListener("click", () => download("thl-audit-log.json", { exportedAt:now(), audit:state.audit }));
  document.querySelectorAll("[data-view]").forEach(b => b.addEventListener("click", () => openView(b.dataset.view)));
  document.querySelectorAll("[data-go]").forEach(b => b.addEventListener("click", () => openView(b.dataset.go)));
  render();
})();