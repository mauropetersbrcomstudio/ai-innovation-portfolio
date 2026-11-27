const prefix = "ai-innovation-client-case:";

export function escapeHtml(value) {
  return String(value ?? "").replace(
    /[&<>"']/g,
    (character) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      })[character],
  );
}

export function formatNumber(value) {
  return new Intl.NumberFormat("pt-BR").format(Number(value) || 0);
}

export function formatMoney(value) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(Number(value) || 0);
}

export function startCase({
  key,
  formId = "intake-form",
  classify,
  render,
  examples,
}) {
  const form = document.getElementById(formId);
  const status = document.getElementById("live-status");
  const storageKey = prefix + key + ":v1";
  let records = [];
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || "[]");
    if (Array.isArray(saved)) records = saved;
  } catch {
    records = [];
  }

  function announce(message) {
    if (status) status.textContent = message;
  }

  function save() {
    try {
      localStorage.setItem(storageKey, JSON.stringify(records));
    } catch {
      announce(
        "Não foi possível salvar neste navegador. Exporte os dados antes de sair.",
      );
    }
  }

  function refresh() {
    render(records);
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const input = Object.fromEntries(new FormData(form).entries());
    form.querySelectorAll('input[type="checkbox"][name]').forEach((box) => {
      input[box.name] = box.checked;
    });
    const result = classify(input, records);
    const timestamp = new Date().toISOString();
    const record = {
      id:
        globalThis.crypto?.randomUUID?.() ||
        String(Date.now()) + "-" + Math.random().toString(36).slice(2),
      createdAt: timestamp,
      input,
      route: result.route,
      priority: result.priority || "normal",
      reasons: result.reasons || [],
      meta: result.meta || {},
      decision: null,
      history: [
        { at: timestamp, action: "Triagem automática", detail: result.route },
      ],
    };
    records.unshift(record);
    save();
    refresh();
    form.reset();
    announce("Solicitação registrada e encaminhada para revisão.");
  });

  document.addEventListener("click", (event) => {
    const sample = event.target.closest("[data-example-index]");
    if (sample) {
      const values = examples[Number(sample.dataset.exampleIndex)];
      if (!values) return;
      form.reset();
      for (const [name, value] of Object.entries(values)) {
        const field = form.elements.namedItem(name);
        if (!field) continue;
        if (field instanceof RadioNodeList) {
          field.value = String(value);
        } else if (field.type === "checkbox") {
          field.checked = Boolean(value);
        } else {
          field.value = String(value);
        }
      }
      announce("Cenário de demonstração carregado. Revise e registre.");
      form.querySelector("input, select, textarea")?.focus();
      return;
    }
    const decisionButton = event.target.closest("[data-decision]");
    if (decisionButton) {
      const wrapper = decisionButton.closest("[data-record-id]");
      const record = records.find(
        (item) => item.id === wrapper?.dataset.recordId,
      );
      if (!record || record.decision) return;
      const note =
        wrapper.querySelector("[data-decision-note]")?.value.trim() || "";
      if (note.length < 3) {
        announce("Escreva uma justificativa com pelo menos três caracteres.");
        wrapper.querySelector("[data-decision-note]")?.focus();
        return;
      }
      const timestamp = new Date().toISOString();
      record.decision = {
        label: decisionButton.dataset.decision,
        note,
        at: timestamp,
      };
      record.history.push({
        at: timestamp,
        action: "Decisão humana",
        detail: record.decision.label + ": " + note,
      });
      save();
      refresh();
      announce("Decisão registrada somente nesta demonstração local.");
      return;
    }
    if (event.target.closest("[data-export]")) {
      const blob = new Blob(
        [
          JSON.stringify(
            { case: key, exportedAt: new Date().toISOString(), records },
            null,
            2,
          ),
        ],
        { type: "application/json" },
      );
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = key + "-demonstracao.json";
      link.click();
      setTimeout(() => URL.revokeObjectURL(link.href), 1000);
      announce("Arquivo JSON exportado.");
      return;
    }
    if (event.target.closest("[data-reset]")) {
      if (!confirm("Apagar os registros desta demonstração neste navegador?"))
        return;
      records = [];
      save();
      refresh();
      announce("Demonstração reiniciada.");
    }
  });

  refresh();
  return {
    getRecords: () => structuredClone(records),
    clear: () => {
      records = [];
      save();
      refresh();
    },
  };
}
