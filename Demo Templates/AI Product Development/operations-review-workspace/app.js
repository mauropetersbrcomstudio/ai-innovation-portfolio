const workflowId = "operations-review-demo";
let snapshot = null;
let selectedItemId = null;
const $ = selector => document.querySelector(selector);
const escapeHtml = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
const pretty = value => JSON.stringify(value ?? {}, null, 2);

async function request(url, options = {}) {
  const response = await fetch(url, { headers: { "Content-Type": "application/json" }, ...options });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}
function visibleItems() {
  const filter = $("#filter").value;
  return (snapshot?.items || []).filter(item => {
    if (filter === "all") return true;
    if (filter === "pending") return !item.decision;
    if (filter === "decided") return Boolean(item.decision);
    return item.source === filter;
  });
}
function renderQueue() {
  const items = visibleItems();
  $("#queue-list").innerHTML = items.length ? items.map(item => `
    <button class="queue-item" data-item-id="${escapeHtml(item.item_id)}" aria-pressed="${item.item_id === selectedItemId}">
      <span class="queue-meta">${escapeHtml(item.source.replace("_", " ").toUpperCase())} · ROW ${escapeHtml(item.row)} <span class="status">${item.decision ? "DECIDED" : "PENDING"}</span></span>
      <strong>${escapeHtml(item.reference)}</strong>
      <span class="queue-meta">${escapeHtml(item.reason)}</span>
    </button>`).join("") : '<p class="empty">No items match this filter.</p>';
  document.querySelectorAll(".queue-item").forEach(button => button.addEventListener("click", () => {
    selectedItemId = button.dataset.itemId; renderQueue(); renderDetail();
  }));
}
function renderDetail() {
  const item = snapshot?.items.find(row => row.item_id === selectedItemId);
  $("#detail").hidden = !item; $("#detail-empty").hidden = Boolean(item);
  if (!item) return;
  $("#detail-source").textContent = item.source.replace("_", " ").toUpperCase();
  $("#detail-reference").textContent = item.reference;
  $("#detail-reason").textContent = item.reason;
  $("#detail-extra").textContent = pretty(item.details || { row: item.row, item_id: item.item_id });
  const decided = Boolean(item.decision);
  $("#decision-form").hidden = decided;
  $("#existing-decision").hidden = !decided;
  $("#existing-decision").textContent = decided
    ? `Recorded: ${item.decision.outcome} · ${item.decision.reviewer_id} · ${item.decision.created_at}\n${item.decision.reason}`
    : "";
}
function renderHistory() {
  const entries = [...(snapshot?.decisions || [])].reverse();
  $("#history-list").innerHTML = entries.length ? entries.map(entry => `
    <div class="history-entry"><strong>${escapeHtml(entry.item_id)}</strong><span>${escapeHtml(entry.outcome)} · ${escapeHtml(entry.reviewer_id)}<br>${escapeHtml(entry.reason)}</span><time>${escapeHtml(entry.created_at)}</time></div>`).join("")
    : '<p class="empty">No review decisions recorded yet.</p>';
}
function render() {
  const items = snapshot?.items || [];
  $("#total-count").textContent = items.length;
  $("#pending-count").textContent = items.filter(item => !item.decision).length;
  $("#decided-count").textContent = items.filter(item => item.decision).length;
  $("#workflow-status").textContent = `STATUS: ${snapshot?.status || "UNKNOWN"}`;
  if (!items.some(item => item.item_id === selectedItemId)) selectedItemId = items.find(item => !item.decision)?.item_id || items[0]?.item_id || null;
  renderQueue(); renderDetail(); renderHistory();
}
async function refresh() {
  try { snapshot = await request(`/api/workflows/${encodeURIComponent(workflowId)}`); render(); }
  catch (error) { $("#workflow-status").textContent = "CONNECTION ERROR"; $("#queue-list").textContent = error.message; }
}
$("#filter").addEventListener("change", renderQueue);
$("#refresh").addEventListener("click", refresh);
$("#decision-form").addEventListener("submit", async event => {
  event.preventDefault();
  const item = snapshot?.items.find(row => row.item_id === selectedItemId);
  if (!item) return;
  const button = $("#submit"); button.disabled = true; $("#form-message").textContent = "Saving decision…";
  try {
    await request("/api/decisions", { method: "POST", body: JSON.stringify({
      workflow_id: workflowId, item_id: item.item_id,
      reviewer_id: $("#reviewer").value.trim(), outcome: $("#outcome").value,
      reason: $("#reason").value.trim()
    })});
    $("#form-message").textContent = "Decision persisted.";
    $("#reason").value = "";
    await refresh();
  } catch (error) { $("#form-message").textContent = error.message; }
  finally { button.disabled = false; }
});
refresh();
