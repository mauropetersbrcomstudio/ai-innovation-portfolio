(() => {
  "use strict";
  const names = Object.keys(SCENARIOS);
  const $ = id => document.getElementById(id);
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  const key = s => `mp-sector-prototype-${s}-v1`;
  const params = new URLSearchParams(location.search);
  const presentation = params.get("presentation") === "1";
  let sector = names.includes(params.get("sector")) ? params.get("sector") : names[0];
  let filter = "all";
  let state;
  function load() {
    try {
      const x = JSON.parse(localStorage.getItem(key(sector)) || "null");
      if (x && Array.isArray(x.items) && Array.isArray(x.history)) return x;
    } catch { /* Restore a clean demo state. */ }
    return { items: [], history: [] };
  }
  function save() { localStorage.setItem(key(sector), JSON.stringify(state)); render(); }
  function log(message) { state.history.unshift({ at: new Date().toISOString(), message }); state.history = state.history.slice(0, 100); }
  function field(f) {
    const common = `name="${esc(f.key)}" id="f-${esc(f.key)}" required`;
    const input = f.type === "select" ? `<select ${common}><option value="">Selecione</option>${f.options.map(o => `<option>${esc(o)}</option>`).join("")}</select>` : `<input ${common} type="${f.type}" ${f.type === "number" ? `min="${f.min}" step="1"` : 'maxlength="100"'} autocomplete="off">`;
    return `<label for="f-${esc(f.key)}">${esc(f.label)}${input}</label>`;
  }
  function setup() {
    const cfg = SCENARIOS[sector];
    document.body.classList.toggle("presentation", presentation);
    document.title = `${cfg.workflow} · Protótipo`;
    $("scenario-nav").innerHTML = names.map(s => `<button type="button" data-sector="${s}" class="${s === sector ? "active" : ""}"><span>${SCENARIOS[s].icon}</span>${esc(SCENARIOS[s].client)}</button>`).join("");
    $("eyebrow").textContent = cfg.title.toUpperCase() + " / " + cfg.workflow.toUpperCase();
    $("client-name").textContent = cfg.client;
    $("client-descriptor").textContent = cfg.descriptor;
    $("client-logo").className = `client-logo logo-${sector}`;
    $("client-logo").setAttribute("aria-label", `Logo ${cfg.client}`);
    $("title").textContent = cfg.workflow;
    $("intro").textContent = cfg.intro;
    $("fields").innerHTML = cfg.fields.map(field).join("");
    $("intake").reset();
    $("error").textContent = "";
    state = load(); render();
  }
  function render() {
    const items = state.items;
    $("total").textContent = items.length;
    $("pending").textContent = items.filter(x => x.status === "Pendente").length;
    $("urgent").textContent = items.filter(x => x.status === "Pendente" && x.priority !== "Normal").length;
    $("decided").textContent = items.filter(x => x.status !== "Pendente").length;
    const shown = items.filter(x => filter === "all" || (filter === "pending" ? x.status === "Pendente" : x.status !== "Pendente"));
    $("queue-count").textContent = shown.length;
    $("queue").innerHTML = shown.length ? shown.map(x => `<article class="item"><div class="item-top"><div><strong>${esc(x.reference)}</strong><br><small>${new Date(x.createdAt).toLocaleString("pt-BR")}</small></div><div class="tags"><span class="tag ${x.priority !== "Normal" ? "urgent" : ""}">${esc(x.priority)}</span><span class="tag">${esc(x.status)}</span></div></div><div class="item-meta">${esc(x.queue)} · ${SCENARIOS[sector].fields.slice(1, 3).map(f => esc(x[f.key])).join(" · ")}</div>${x.reasons.length ? `<ul>${x.reasons.map(r => `<li>${esc(r)}</li>`).join("")}</ul>` : '<small>Sem exceções nas regras demonstrativas.</small>'}${x.status === "Pendente" ? `<div class="actions"><button type="button" data-decision="Aprovado na simulação" data-id="${esc(x.id)}">Aprovar</button><button type="button" data-decision="Devolvido para ajuste" data-id="${esc(x.id)}">Solicitar ajuste</button><button type="button" data-decision="Recusado na simulação" data-id="${esc(x.id)}">Recusar</button></div>` : `<small>Decisão registrada: ${esc(x.status)}${x.note ? " · " + esc(x.note) : ""}</small>`}</article>`).join("") : '<div class="empty">Nenhum registro neste filtro. Use os exemplos ou crie uma solicitação.</div>';
    $("history").innerHTML = state.history.length ? state.history.map(x => `<div>${esc(new Date(x.at).toLocaleString("pt-BR"))} · ${esc(x.message)}</div>`).join("") : '<div class="empty">Nenhum evento registrado.</div>';
    document.querySelectorAll("[data-filter]").forEach(b => b.classList.toggle("selected", b.dataset.filter === filter));
  }
  $("scenario-nav").addEventListener("click", e => {
    const button = e.target.closest("[data-sector]");
    if (!button) return;
    if (presentation) return;
    sector = button.dataset.sector; filter = "all";
    history.replaceState(null, "", `?sector=${sector}`); setup();
  });
  $("intake").addEventListener("submit", e => {
    e.preventDefault();
    try {
      const data = Object.fromEntries(new FormData(e.currentTarget));
      const record = triage(sector, data);
      if (state.items.some(x => x.reference.toLocaleLowerCase() === record.reference.toLocaleLowerCase())) throw new Error("Referência já registrada neste setor");
      record.id = crypto.randomUUID(); record.createdAt = new Date().toISOString(); record.status = "Pendente";
      state.items.unshift(record); log(`Solicitação ${record.reference} enviada para ${record.queue}`); save();
      e.currentTarget.reset(); $("error").textContent = "";
    } catch (err) { $("error").textContent = err.message; }
  });
  document.querySelector(".examples").addEventListener("click", e => {
    const b = e.target.closest("[data-example]"); if (!b) return;
    const example = SCENARIOS[sector].examples[Number(b.dataset.example)];
    for (const [name, value] of Object.entries(example)) $("intake").elements[name].value = value;
    $("error").textContent = "";
  });
  document.querySelector(".filters").addEventListener("click", e => { const b = e.target.closest("[data-filter]"); if (b) { filter = b.dataset.filter; render(); } });
  $("queue").addEventListener("click", e => {
    const b = e.target.closest("[data-decision]"); if (!b) return;
    const item = state.items.find(x => x.id === b.dataset.id && x.status === "Pendente"); if (!item) return;
    const note = window.prompt("Justificativa da decisão (obrigatória, até 200 caracteres):");
    if (!note || !note.trim()) return;
    if (note.trim().length > 200) { window.alert("A justificativa deve ter até 200 caracteres."); return; }
    item.status = b.dataset.decision; item.note = note.trim(); item.decidedAt = new Date().toISOString();
    log(`${item.reference}: ${item.status}`); save();
  });
  $("reset").addEventListener("click", () => { if (!window.confirm("Apagar os registros locais deste setor?")) return; state = { items: [], history: [] }; save(); });
  $("export").addEventListener("click", () => {
    const blob = new Blob([JSON.stringify({ scenario: sector, exportedAt: new Date().toISOString(), ...state }, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob); const a = document.createElement("a"); a.href = url; a.download = `prototipo-${sector}.json`; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  setup();
})();
