const STORAGE_KEY = "supply-operations-prototype-v1";
const POLICY = { id: "DEMO-SUP-01", maxRequest: 20, standardResponse: "Revisão pela equipe antes de movimentar o estoque." };

const UNITS = [
  ...Array.from({ length: 6 }, (_, i) => ({ id: `sp-${String(i + 1).padStart(2, "0")}`, label: `São Paulo · Unidade ${String(i + 1).padStart(2, "0")}`, aliases: ["sao paulo", "sp"] })),
  ...Array.from({ length: 4 }, (_, i) => ({ id: `abc-${String(i + 1).padStart(2, "0")}`, label: `ABC · Unidade ${String(i + 1).padStart(2, "0")}`, aliases: ["abc", "santo andre", "sao bernardo", "sao caetano", "diadema"] })),
  ...Array.from({ length: 2 }, (_, i) => ({ id: `santos-${String(i + 1).padStart(2, "0")}`, label: `Santos · Unidade ${String(i + 1).padStart(2, "0")}`, aliases: ["santos"] })),
  { id: "jundiai-01", label: "Jundiaí · Unidade 01", aliases: ["jundiai"] },
  { id: "indaiatuba-01", label: "Indaiatuba · Unidade 01", aliases: ["indaiatuba"] },
  ...Array.from({ length: 3 }, (_, i) => ({ id: `campinas-${String(i + 1).padStart(2, "0")}`, label: `Campinas · Unidade ${String(i + 1).padStart(2, "0")}`, aliases: ["campinas"] }))
];

const CATALOG = [
  { id: "glove-small", name: "Luva nitrílica P", unit: "caixas", glyph: "◇", aliases: ["luva nitrilica p", "luvas p", "luva p", "luva pequena"], min: 12, target: 24, central: 26, max: 20 },
  { id: "bed-roll", name: "Lençol descartável", unit: "rolos", glyph: "▤", aliases: ["lencol descartavel", "lencol", "lençol"], min: 8, target: 18, central: 17, max: 20 },
  { id: "cotton", name: "Algodão", unit: "pacotes", glyph: "◌", aliases: ["algodao", "algodão"], min: 12, target: 24, central: 8, max: 20 },
  { id: "gauze", name: "Gaze", unit: "pacotes", glyph: "▧", aliases: ["gaze", "compressa de gaze"], min: 8, target: 18, central: 6, max: 20 },
  { id: "alcohol", name: "Álcool 70%", unit: "frascos", glyph: "◉", aliases: ["alcool 70", "alcool 70%", "alcool"], min: 10, target: 20, central: 22, max: 20 }
];

const STATUS = {
  pending_manager: { label: "Aguardando aprovação", className: "status-pending" },
  pending_purchase_approval: { label: "Aguardando compras", className: "status-purchase" },
  awaiting_receipt: { label: "Aguardando recebimento", className: "status-receipt" },
  fulfilled: { label: "Concluída na demo", className: "status-done" },
  rejected: { label: "Recusada", className: "status-rejected" }
};

let state = loadState();
let currentView = "dashboard";
let selectedRequestId = state.requests.find((r) => r.status !== "fulfilled" && r.status !== "rejected")?.id || state.requests[0]?.id || null;
let draft = null;
let toastTimer;

function normalize(value) {
  return String(value || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
}

function ago(hours) {
  return new Date(Date.now() - hours * 60 * 60 * 1000).toISOString();
}

function createInitialState() {
  const unitStocks = (base, drift) => Object.fromEntries(UNITS.map((unit, i) => [unit.id, Math.max(0, base + ((i * 3 + drift) % 8) - 3)]));
  const inventory = CATALOG.map((product, i) => ({
    ...product,
    centralStock: product.central,
    unitStocks: unitStocks([8, 5, 7, 5, 9][i], i + 1)
  }));
  const historicalBedRollTransfer = inventory.find((item) => item.id === "bed-roll");
  historicalBedRollTransfer.unitStocks["sp-03"] += 4;
  const requests = [
    {
      id: "RQ-1042", unitId: "campinas-02", itemId: "glove-small", quantity: 14, message: "A unidade Campinas 02 precisa de 14 caixas de luva nitrílica P. O saldo está baixo.", urgency: "normal", status: "pending_manager", plan: { transfer: 14, purchase: 0, centralAtReview: 26 }, createdAt: ago(3), updatedAt: ago(3), exception: false,
      events: [{ at: ago(3), title: "Solicitação registrada", detail: "Entrada local da demonstração; regra e saldo simulados consultados." }]
    },
    {
      id: "RQ-1041", unitId: "abc-01", itemId: "cotton", quantity: 18, message: "ABC unidade 01 precisa de 18 pacotes de algodão, por favor.", urgency: "normal", status: "pending_manager", plan: { transfer: 8, purchase: 10, centralAtReview: 8 }, createdAt: ago(6), updatedAt: ago(6), exception: true,
      events: [{ at: ago(6), title: "Solicitação registrada", detail: "Saldo central insuficiente: a proposta precisa de aprovação humana e compra simulada." }]
    },
    {
      id: "RQ-1040", unitId: "sp-03", itemId: "bed-roll", quantity: 4, message: "São Paulo unidade 03 precisa repor 4 rolos de lençol descartável.", urgency: "normal", status: "fulfilled", plan: { transfer: 4, purchase: 0, centralAtReview: 21 }, createdAt: ago(24), updatedAt: ago(22), exception: false,
      events: [
        { at: ago(24), title: "Solicitação registrada", detail: "Pedido de exemplo criado com dados fictícios." },
        { at: ago(23), title: "Plano aprovado", detail: "Aprovação local simulada; nenhuma plataforma externa foi alterada." },
        { at: ago(22), title: "Transferência simulada", detail: "4 rolos transferidos do estoque central para a unidade." }
      ]
    }
  ];
  return { version: 1, nextNumber: 1043, inventory, requests };
}

function loadState() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (saved?.version === 1 && Array.isArray(saved.inventory) && Array.isArray(saved.requests)) return saved;
  } catch (error) {
    console.warn("Não foi possível ler a demonstração salva.", error);
  }
  return createInitialState();
}

function saveState() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch (error) {
    console.warn("O navegador não permitiu persistir esta demonstração.", error);
  }
}

function getUnit(id) { return UNITS.find((unit) => unit.id === id); }
function getProduct(id) { return state.inventory.find((item) => item.id === id); }
function getRequest(id) { return state.requests.find((request) => request.id === id); }
function activeRequests() { return state.requests.filter((request) => !["fulfilled", "rejected"].includes(request.status)); }
function statusMarkup(status) { const item = STATUS[status] || STATUS.pending_manager; return `<span class="status-badge ${item.className}">${item.label}</span>`; }

function calculatePlan(product, quantity) {
  const available = Math.max(0, Number(product.centralStock) || 0);
  const transfer = Math.min(quantity, available);
  const purchase = Math.max(0, quantity - transfer);
  return { transfer, purchase, centralAtReview: available };
}

function seedSelectors() {
  const unitOptions = UNITS.map((unit) => `<option value="${unit.id}">${escapeHtml(unit.label)}</option>`).join("");
  const itemOptions = state.inventory.map((item) => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join("");
  const unitSelect = document.getElementById("draft-unit");
  const itemSelect = document.getElementById("draft-item");
  if (unitSelect) unitSelect.innerHTML = `<option value="">Selecione a unidade</option>${unitOptions}`;
  if (itemSelect) itemSelect.innerHTML = `<option value="">Selecione o insumo</option>${itemOptions}`;
  const filterUnit = document.getElementById("filter-unit");
  if (filterUnit) filterUnit.innerHTML = `<option value="all">Todas as unidades</option>${unitOptions}`;
  const inventoryUnit = document.getElementById("inventory-unit");
  if (inventoryUnit) {
    const selected = inventoryUnit.value || UNITS[0].id;
    inventoryUnit.innerHTML = unitOptions;
    inventoryUnit.value = selected;
  }
}

function parseQuantity(text) {
  const patterns = [
    /\b(\d+)\s*(?:caixas?|cx|pacotes?|pct|rolos?|frascos?|unidades?|un|kits?)\b/,
    /(?:precisa(?:mos)?|solicito|pedir|repor|reposição|quantidade de|falta)\s+(?:de\s+)?(\d+)\b/
  ];
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) return Number(match[1]);
  }
  const candidates = [...text.matchAll(/\b\d+\b/g)];
  const valid = candidates.find((match) => !/unidade\s*$/i.test(text.slice(Math.max(0, match.index - 12), match.index)));
  return valid ? Number(valid[0]) : null;
}

function parseMessage(message) {
  const normalized = normalize(message);
  let unitId = "";
  for (const unit of UNITS) {
    const [region, unitName] = unit.label.split(" · ");
    const regionText = escapeRegExp(normalize(region));
    const unitNumber = Number(unitName.match(/\d+/)?.[0]);
    const exactPatterns = [
      new RegExp(`\\b${regionText}\\s*(?:unidade|unid\\.?\\s*)?0?${unitNumber}\\b`),
      new RegExp(`\\bunidade\\s*0?${unitNumber}\\s*${regionText}\\b`)
    ];
    if (exactPatterns.some((pattern) => pattern.test(normalized))) { unitId = unit.id; break; }
  }
  if (!unitId) {
    const matchingRegion = UNITS.find((unit) => unit.aliases.some((alias) => normalized.includes(normalize(alias))));
    unitId = matchingRegion?.id || "";
  }
  const productsByAlias = state.inventory.flatMap((item) => item.aliases.map((alias) => ({ item, alias }))).sort((a, b) => b.alias.length - a.alias.length);
  const matchProduct = productsByAlias.find(({ alias }) => normalized.includes(normalize(alias)));
  const quantity = parseQuantity(normalized);
  const urgency = /\burgente\b|\bhoje\b|\bacabou\b|\binterrompe/.test(normalized) ? "urgent" : "normal";
  return { unitId, itemId: matchProduct?.item.id || "", quantity: Number.isFinite(quantity) ? quantity : null, urgency };
}

function analyzeDraft(message, preserveSelections = false) {
  const parsed = parseMessage(message);
  const unitSelect = document.getElementById("draft-unit");
  const itemSelect = document.getElementById("draft-item");
  const quantityInput = document.getElementById("draft-quantity");
  const prioritySelect = document.getElementById("draft-priority");
  if (!preserveSelections) {
    if (unitSelect) unitSelect.value = parsed.unitId;
    if (itemSelect) itemSelect.value = parsed.itemId;
    if (quantityInput) quantityInput.value = parsed.quantity || "";
    if (prioritySelect) prioritySelect.value = parsed.urgency;
  }
  draft = { message, urgency: prioritySelect?.value || parsed.urgency };
  renderAnalysis();
}

function renderAnalysis() {
  const card = document.getElementById("analysis-card");
  if (!card || !draft) return;
  const unitId = document.getElementById("draft-unit")?.value || "";
  const itemId = document.getElementById("draft-item")?.value || "";
  const quantity = Number(document.getElementById("draft-quantity")?.value || 0);
  const priority = document.getElementById("draft-priority")?.value || "normal";
  const unit = getUnit(unitId);
  const product = getProduct(itemId);
  const missing = [];
  if (!unit) missing.push("unidade");
  if (!product) missing.push("insumo");
  if (!Number.isInteger(quantity) || quantity <= 0) missing.push("quantidade inteira maior que zero");
  const plan = product && quantity > 0 ? calculatePlan(product, quantity) : null;
  const localBalance = product && unit ? product.unitStocks[unit.id] ?? 0 : null;
  const isException = Boolean(product && (quantity > POLICY.maxRequest || plan?.purchase > 0 || priority === "urgent"));
  const duplicate = unit && product ? activeRequests().find((request) => request.unitId === unit.id && request.itemId === product.id) : null;

  card.hidden = false;
  card.innerHTML = `
    <div class="analysis-head"><div><h3>Leitura do assistente</h3><p>Interpretação local por palavras-chave. Confira os campos antes de registrar.</p></div><span class="analysis-label">RASCUNHO</span></div>
    <div class="extracted-fields">
      <label>Unidade<select id="draft-unit"><option value="">Selecione a unidade</option>${UNITS.map((option) => `<option value="${option.id}" ${option.id === unitId ? "selected" : ""}>${escapeHtml(option.label)}</option>`).join("")}</select></label>
      <label>Insumo<select id="draft-item"><option value="">Selecione o insumo</option>${state.inventory.map((option) => `<option value="${option.id}" ${option.id === itemId ? "selected" : ""}>${escapeHtml(option.name)}</option>`).join("")}</select></label>
      <label>Quantidade (${escapeHtml(product?.unit || "unidades")})<input id="draft-quantity" type="number" min="1" max="999" step="1" value="${quantity || ""}" placeholder="Ex.: 8"></label>
      <label class="priority-field">Prioridade<select id="draft-priority"><option value="normal" ${priority === "normal" ? "selected" : ""}>Normal</option><option value="urgent" ${priority === "urgent" ? "selected" : ""}>Urgente · revisar</option></select></label>
    </div>
    ${missing.length ? `<div class="analysis-warning">Para analisar, informe: ${escapeHtml(missing.join(", "))}. Você pode preencher ou corrigir os campos acima.</div>` : `
      <div class="plan-box"><h4>Sugestão de atendimento · sem execução automática</h4>
        <div class="plan-row"><span>Saldo atual na unidade</span><strong>${localBalance} ${escapeHtml(product.unit)}</strong></div>
        <div class="plan-row"><span>Saldo no estoque central</span><strong>${product.centralStock} ${escapeHtml(product.unit)}</strong></div>
        <div class="plan-row"><span>Transferência sugerida</span><strong>${plan.transfer} ${escapeHtml(product.unit)}</strong></div>
        <div class="plan-row"><span>Compra necessária</span><strong>${plan.purchase} ${escapeHtml(product.unit)}</strong></div>
      </div>
      ${isException ? `<div class="analysis-warning">${priority === "urgent" ? "Pedido marcado como urgente. " : ""}${quantity > POLICY.maxRequest ? `Quantidade acima do limite demonstrativo de ${POLICY.maxRequest}. ` : ""}${plan.purchase > 0 ? "O saldo central não cobre tudo; a falta exigiria aprovação de compras." : ""} Uma pessoa autorizada precisa revisar e aprovar.</div>` : `<div class="analysis-success">O saldo central cobre o pedido. Ainda assim, a equipe deve aprovar a transferência simulada.</div>`}
      ${duplicate ? `<div class="analysis-warning">Já existe o pedido ${escapeHtml(duplicate.id)} para esta unidade e insumo. Acompanhe-o antes de abrir outro para evitar duplicidade.</div>` : ""}
      <p class="policy-reference">Consulta demonstrativa: política ${POLICY.id} · limites fictícios, não aprovados pela clínica.</p>
    `}
    <div class="analysis-footer"><span>Nenhum sistema, fornecedor ou colaborador foi contatado.</span>${duplicate ? `<button class="button button-outline" id="follow-duplicate" type="button">Abrir ${escapeHtml(duplicate.id)}</button>` : `<button class="button button-primary" id="save-request" type="button" ${missing.length ? "disabled" : ""}>Registrar na fila local <span>→</span></button>`}</div>`;

  card.querySelectorAll("#draft-unit, #draft-item, #draft-quantity, #draft-priority").forEach((field) => field.addEventListener("change", () => renderAnalysis()));
  card.querySelector("#save-request")?.addEventListener("click", createRequestFromDraft);
  card.querySelector("#follow-duplicate")?.addEventListener("click", () => openRequest(duplicate.id));
}

function createRequestFromDraft() {
  const unitId = document.getElementById("draft-unit")?.value;
  const itemId = document.getElementById("draft-item")?.value;
  const quantity = Number(document.getElementById("draft-quantity")?.value || 0);
  const urgency = document.getElementById("draft-priority")?.value || "normal";
  const item = getProduct(itemId);
  if (!getUnit(unitId) || !item || !Number.isInteger(quantity) || quantity < 1 || quantity > 999) {
    showToast("Complete unidade, insumo e quantidade para registrar.");
    return;
  }
  const plan = calculatePlan(item, quantity);
  const request = {
    id: `RQ-${state.nextNumber++}`, unitId, itemId, quantity,
    message: draft?.message || "Solicitação criada no formulário demonstrativo.",
    urgency, status: "pending_manager", plan, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(),
    exception: quantity > POLICY.maxRequest || plan.purchase > 0 || urgency === "urgent",
    events: [{ at: new Date().toISOString(), title: "Solicitação registrada", detail: `Assistente local classificou o pedido e consultou ${POLICY.id}. Aguardando aprovação humana.` }]
  };
  state.requests.unshift(request);
  saveState();
  draft = null;
  document.getElementById("analysis-card").hidden = true;
  document.getElementById("request-message").value = "";
  selectedRequestId = request.id;
  currentView = "requests";
  renderAll();
  showToast(`${request.id} entrou na fila local para revisão.`);
}

function renderMetrics() {
  const waiting = state.requests.filter((request) => request.status === "pending_manager").length;
  const buying = state.requests.filter((request) => request.status === "pending_purchase_approval").length;
  const receiving = state.requests.filter((request) => request.status === "awaiting_receipt").length;
  const completed = state.requests.filter((request) => request.status === "fulfilled").length;
  const lowStock = state.inventory.filter((item) => item.centralStock < item.min).length;
  const metrics = [
    ["Aguardando aprovação", waiting, "pedidos", "◷"],
    ["Etapa de compras", buying, "pedidos", "↗"],
    ["Aguardando recebimento", receiving, "pedidos", "⇣"],
    ["Insumos abaixo do mínimo", lowStock, "itens", "!"],
  ];
  document.getElementById("metrics-grid").innerHTML = metrics.map(([label, value, unit, icon]) => `<article class="metric-card"><div class="metric-top"><span>${label}</span><span class="metric-icon">${icon}</span></div><div class="metric-value">${value}<small>${unit}</small></div></article>`).join("");
  document.getElementById("nav-pending").textContent = String(waiting + buying + receiving);
  document.getElementById("queue-summary").innerHTML = `<span class="queue-pill"><strong>${waiting}</strong> aprovação</span><span class="queue-pill"><strong>${buying}</strong> compras</span><span class="queue-pill"><strong>${completed}</strong> concluídas</span>`;
}

function renderCompactQueue() {
  const container = document.getElementById("compact-queue");
  const rows = state.requests.slice(0, 4);
  if (!rows.length) {
    container.innerHTML = `<div class="empty-state">A fila está vazia.<br>Analise uma solicitação para começar.</div>`;
    return;
  }
  container.innerHTML = rows.map((request) => {
    const item = getProduct(request.itemId);
    const unit = getUnit(request.unitId);
    return `<button class="compact-row" type="button" data-request-id="${request.id}"><span class="item-glyph">${item?.glyph || "▦"}</span><span class="compact-row-main"><strong>${escapeHtml(item?.name || "Insumo")}</strong><span>${escapeHtml(unit?.label || "Unidade")} · ${request.quantity} ${escapeHtml(item?.unit || "un.")}</span></span>${statusMarkup(request.status)}</button>`;
  }).join("");
  container.querySelectorAll("[data-request-id]").forEach((button) => button.addEventListener("click", () => openRequest(button.dataset.requestId)));
}

function renderRequestList() {
  const list = document.getElementById("request-list");
  const statusFilter = document.getElementById("filter-status")?.value || "all";
  const unitFilter = document.getElementById("filter-unit")?.value || "all";
  const search = normalize(document.getElementById("filter-search")?.value || "");
  const filtered = state.requests.filter((request) => {
    const product = getProduct(request.itemId);
    const unit = getUnit(request.unitId);
    return (statusFilter === "all" || request.status === statusFilter) &&
      (unitFilter === "all" || request.unitId === unitFilter) &&
      (!search || normalize(`${request.id} ${product?.name} ${unit?.label} ${request.message}`).includes(search));
  });
  if (!filtered.some((request) => request.id === selectedRequestId)) selectedRequestId = filtered[0]?.id || null;
  list.innerHTML = `<div class="request-list-head"><span>${filtered.length} solicitações</span><span>Mais recentes</span></div>${filtered.length ? filtered.map((request) => {
    const item = getProduct(request.itemId);
    const unit = getUnit(request.unitId);
    return `<button class="request-card ${request.id === selectedRequestId ? "is-selected" : ""}" type="button" data-request-id="${request.id}">
      <span class="item-glyph">${item?.glyph || "▦"}</span><span class="request-card-content"><span class="request-card-title"><strong>${escapeHtml(item?.name || "Insumo")}</strong></span><span>${escapeHtml(unit?.label || "Unidade")} · ${request.quantity} ${escapeHtml(item?.unit || "un.")}</span><span class="request-card-meta">${statusMarkup(request.status)}<small>${formatDate(request.createdAt)}</small></span></span>
    </button>`;
  }).join("") : `<div class="empty-state">Nenhuma solicitação corresponde aos filtros.</div>`}`;
  list.querySelectorAll("[data-request-id]").forEach((button) => button.addEventListener("click", () => {
    selectedRequestId = button.dataset.requestId;
    renderRequestList();
    renderRequestDetail();
  }));
}

function formatDate(iso) {
  try { return new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }).format(new Date(iso)); }
  catch { return ""; }
}

function renderRequestDetail() {
  const panel = document.getElementById("request-detail");
  const request = getRequest(selectedRequestId);
  if (!request) {
    panel.innerHTML = `<div class="empty-state">Selecione uma solicitação para revisar os dados, a recomendação e o histórico.</div>`;
    return;
  }
  const item = getProduct(request.itemId);
  const unit = getUnit(request.unitId);
  const plan = request.plan || calculatePlan(item, request.quantity);
  const actionButtons = request.status === "pending_manager"
    ? `<button class="button button-primary" data-action="approve-plan" data-request-id="${request.id}">Aprovar plano simulado</button><button class="button button-danger" data-action="reject" data-request-id="${request.id}">Recusar pedido</button>`
    : request.status === "pending_purchase_approval"
      ? `<button class="button button-primary" data-action="approve-purchase" data-request-id="${request.id}">Aprovar compra simulada</button><button class="button button-danger" data-action="reject" data-request-id="${request.id}">Recusar compra</button>`
      : request.status === "awaiting_receipt"
        ? `<button class="button button-primary" data-action="receive" data-request-id="${request.id}">Registrar recebimento simulado</button>`
        : `<span class="muted">${request.status === "fulfilled" ? "Etapas desta solicitação concluídas na demonstração." : "Nenhuma ação disponível."}</span>`;
  panel.innerHTML = `
    <div class="detail-top"><div><div class="detail-code">${escapeHtml(request.id)} · ${formatDate(request.createdAt)}</div><h2>${escapeHtml(item?.name || "Insumo")}</h2><p class="detail-unit">${escapeHtml(unit?.label || "Unidade")}</p></div>${statusMarkup(request.status)}</div>
    <div class="detail-body">
      <div class="detail-message">“${escapeHtml(request.message)}”</div>
      <div class="detail-grid"><div class="detail-field"><span>Quantidade solicitada</span><strong>${request.quantity} ${escapeHtml(item?.unit || "unidades")}</strong></div><div class="detail-field"><span>Prioridade</span><strong>${request.urgency === "urgent" ? "Urgente · revisão humana" : "Normal"}</strong></div></div>
      <div class="detail-plan"><h3>Plano demonstrativo · ${escapeHtml(POLICY.id)}</h3><p>Saldo central no momento do pedido: <strong>${plan.centralAtReview ?? item?.centralStock ?? 0} ${escapeHtml(item?.unit || "unidades")}</strong>.</p><p>Transferir da central: <strong>${plan.transfer} ${escapeHtml(item?.unit || "unidades")}</strong> · Compra simulada: <strong>${plan.purchase} ${escapeHtml(item?.unit || "unidades")}</strong>.</p>${request.exception ? `<p class="analysis-warning">Exceção sujeita a justificativa e decisão de uma pessoa autorizada.</p>` : ""}</div>
      <div class="detail-actions">${actionButtons}</div>
      <div><div class="audit-heading">Histórico local</div><div class="audit-list">${[...(request.events || [])].reverse().map((event) => `<div class="audit-entry"><div><strong>${escapeHtml(event.title)}</strong> · ${escapeHtml(formatDate(event.at))}<br>${escapeHtml(event.detail)}</div></div>`).join("")}</div></div>
      <p class="detail-disclaimer">Registro local não prova identidade do operador e não atualiza estoque real, sistema da clínica nem fornecedor.</p>
    </div>`;
  panel.querySelectorAll("[data-action]").forEach((button) => button.addEventListener("click", () => handleRequestAction(button.dataset.action, button.dataset.requestId)));
}

function renderInventory() {
  seedSelectors();
  const unitId = document.getElementById("inventory-unit")?.value || UNITS[0].id;
  const unit = getUnit(unitId);
  const grid = document.getElementById("inventory-grid");
  grid.innerHTML = state.inventory.map((item) => {
    const local = item.unitStocks[unitId] ?? 0;
    const low = item.centralStock < item.min;
    const ratio = Math.max(3, Math.min(100, Math.round((item.centralStock / Math.max(item.target, 1)) * 100)));
    return `<article class="stock-card"><div class="stock-card-top"><h3>${escapeHtml(item.name)}</h3>${low ? `<span class="status-badge status-pending">Abaixo do mínimo</span>` : `<span class="status-badge status-done">Saldo normal</span>`}</div><p class="stock-unit">Unidade de medida: ${escapeHtml(item.unit)}</p><div class="stock-levels"><div class="stock-level"><span>Estoque central</span><strong>${item.centralStock}</strong></div><div class="stock-level"><span>${escapeHtml(unit?.label.split(" · ")[0] || "Unidade")}</span><strong>${local}</strong></div><div class="stock-level"><span>Mínimo central</span><strong>${item.min}</strong></div></div><div class="stock-meter ${low ? "is-low" : ""}"><span style="width:${ratio}%"></span></div><div class="stock-foot"><span>Meta demo: ${item.target} ${escapeHtml(item.unit)}</span><span>Máx. por pedido: ${item.max} ${escapeHtml(item.unit)}</span></div></article>`;
  }).join("");
  document.getElementById("inventory-count").textContent = `${state.inventory.length} itens · saldo local de ${unit?.label || "unidade"}`;
}

function addEvent(request, title, detail) {
  request.events ||= [];
  request.events.push({ at: new Date().toISOString(), title, detail });
  request.updatedAt = new Date().toISOString();
}

function handleRequestAction(action, requestId) {
  const request = getRequest(requestId);
  const item = request && getProduct(request.itemId);
  if (!request || !item) return;

  if (action === "approve-plan") {
    if (request.exception) {
      const reason = window.prompt("Esta solicitação é uma exceção. Informe uma justificativa para aprovar na demonstração (mínimo 5 caracteres):", "");
      if (!reason || reason.trim().length < 5) { showToast("A aprovação da exceção exige uma justificativa."); return; }
      request.reviewReason = reason.trim();
    }
    const plan = calculatePlan(item, request.quantity);
    request.plan = plan;
    if (plan.transfer > 0) {
      item.centralStock -= plan.transfer;
      item.unitStocks[request.unitId] = (item.unitStocks[request.unitId] || 0) + plan.transfer;
    }
    if (plan.purchase > 0) {
      request.status = "pending_purchase_approval";
      request.exception = true;
      addEvent(request, "Plano aprovado localmente", `${plan.transfer} ${item.unit} reservados na demonstração. ${plan.purchase} ${item.unit} aguardam aprovação da compra simulada.`);
      showToast("Plano local aprovado; a compra continua aguardando outra decisão humana.");
    } else {
      request.status = "fulfilled";
      addEvent(request, "Transferência simulada concluída", `${plan.transfer} ${item.unit} movimentados somente no estoque demonstrativo.`);
      showToast("Transferência registrada apenas na demonstração local.");
    }
  } else if (action === "approve-purchase") {
    const reason = window.prompt("A compra só será registrada neste protótipo. Informe a justificativa de aprovação (mínimo 5 caracteres):", "");
    if (!reason || reason.trim().length < 5) { showToast("Informe uma justificativa para aprovar a compra simulada."); return; }
    request.reviewReason = reason.trim();
    request.status = "awaiting_receipt";
    addEvent(request, "Compra simulada aprovada", `${request.plan.purchase} ${item.unit} aguardam recebimento manual de demonstração. Nenhum fornecedor foi contatado.`);
    showToast("Aprovação anotada localmente; nenhum pedido foi enviado.");
  } else if (action === "receive") {
    const quantity = request.plan.purchase;
    item.centralStock += quantity;
    addEvent(request, "Recebimento simulado", `${quantity} ${item.unit} adicionados ao estoque central fictício.`);
    item.centralStock -= quantity;
    item.unitStocks[request.unitId] = (item.unitStocks[request.unitId] || 0) + quantity;
    request.status = "fulfilled";
    addEvent(request, "Transferência para unidade simulada", `${quantity} ${item.unit} registrados para ${getUnit(request.unitId)?.label || "unidade"}.`);
    showToast("Recebimento e transferência atualizados somente na demonstração.");
  } else if (action === "reject") {
    const reason = window.prompt("Motivo para registrar a recusa na demonstração:", "");
    if (!reason || reason.trim().length < 3) { showToast("Informe um motivo curto para recusar."); return; }
    request.status = "rejected";
    request.rejectionReason = reason.trim();
    addEvent(request, "Solicitação recusada", reason.trim());
    showToast("Decisão registrada apenas na fila local.");
  }

  saveState();
  renderAll();
}

function switchView(view) {
  currentView = view;
  document.querySelectorAll(".view").forEach((section) => section.classList.toggle("is-visible", section.id === `view-${view}`));
  document.querySelectorAll(".nav-link").forEach((button) => button.classList.toggle("is-active", button.dataset.view === view));
  const labels = {
    dashboard: ["Operações da rede", "O assistente consulta regras e estoque demonstrativos, prepara o plano e deixa as decisões com a equipe."],
    requests: ["Solicitações", "Revise cada proposta, aprove etapas locais ou acompanhe o que aguarda compras."],
    inventory: ["Estoque e política", "Consulte saldos sintéticos e regras ilustrativas usadas pelo assistente."],
  };
  document.getElementById("page-title").textContent = labels[view][0];
  document.getElementById("page-subtitle").textContent = labels[view][1];
  if (view === "requests") { renderRequestList(); renderRequestDetail(); }
  if (view === "inventory") renderInventory();
}

function renderAll() {
  saveState();
  seedSelectors();
  renderMetrics();
  renderCompactQueue();
  switchView(currentView);
}

function openRequest(requestId) {
  selectedRequestId = requestId;
  switchView("requests");
}

function showToast(message) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.classList.add("is-visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("is-visible"), 3200);
}

function resetDemo() {
  if (!window.confirm("Reiniciar os dados fictícios desta demonstração neste navegador?")) return;
  state = createInitialState();
  selectedRequestId = state.requests[0].id;
  draft = null;
  document.getElementById("request-message").value = "";
  document.getElementById("analysis-card").hidden = true;
  renderAll();
  showToast("Demonstração reiniciada com os dados fictícios iniciais.");
}

function exportData() {
  const data = { exportedAt: new Date().toISOString(), disclaimer: "Dados sintéticos e locais; não representam o sistema da clínica.", state };
  const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "supply-operations-demo-local.json";
  anchor.click();
  URL.revokeObjectURL(url);
  showToast("Cópia local dos dados de demonstração exportada.");
}

document.querySelectorAll(".nav-link").forEach((button) => button.addEventListener("click", () => switchView(button.dataset.view)));
document.querySelectorAll("[data-open-view]").forEach((button) => button.addEventListener("click", () => switchView(button.dataset.openView)));
document.querySelectorAll("[data-example]").forEach((button) => button.addEventListener("click", () => {
  const message = button.dataset.example;
  document.getElementById("request-message").value = message;
  analyzeDraft(message);
}));
document.getElementById("request-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const message = document.getElementById("request-message").value.trim();
  if (!message) return;
  seedSelectors();
  analyzeDraft(message);
});
document.getElementById("filter-status").addEventListener("change", () => { renderRequestList(); renderRequestDetail(); });
document.getElementById("filter-unit").addEventListener("change", () => { renderRequestList(); renderRequestDetail(); });
document.getElementById("filter-search").addEventListener("input", () => { renderRequestList(); renderRequestDetail(); });
document.getElementById("inventory-unit").addEventListener("change", renderInventory);
document.getElementById("reset-demo").addEventListener("click", resetDemo);
document.getElementById("export-data").addEventListener("click", exportData);

renderAll();

