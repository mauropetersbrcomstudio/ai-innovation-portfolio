(() => {
  "use strict";
  const sector = new URLSearchParams(location.search).get("sector");
  if (!Object.hasOwn(SCENARIOS, sector)) { document.body.textContent = "Protótipo não encontrado."; return; }
  document.body.classList.add(`layout-${sector}`);

  const brand = `<div class="brand-lockup"><div class="client-logo" id="client-logo" role="img"></div><div><strong id="client-name"></strong><small id="client-descriptor"></small></div></div>`;
  const actions = `<div class="utility"><button id="export" type="button">Exportar JSON</button><button id="reset" type="button">Reiniciar demonstração</button></div>`;
  const heading = `<div class="heading-copy"><span class="eyebrow" id="eyebrow"></span><h1 id="title"></h1><p id="intro"></p></div>`;
  const notice = `<p class="boundary">Protótipo local com dados sintéticos e regras ilustrativas. Nenhuma ação é enviada a sistemas externos.</p>`;
  const metrics = `<div class="metrics"><div><span>Solicitações</span><strong id="total">0</strong></div><div><span>Pendentes</span><strong id="pending">0</strong></div><div><span>Prioritárias</span><strong id="urgent">0</strong></div><div><span>Decididas</span><strong id="decided">0</strong></div></div>`;
  const intake = `<section class="intake"><div class="section-heading"><span>ENTRADA</span><h2>Nova solicitação</h2><p>Use somente exemplos sintéticos.</p></div><form id="intake"><div id="fields"></div><button class="submit" type="submit">Analisar e adicionar à fila</button></form><div class="examples"><span>Carregar:</span><button type="button" data-example="0">Fluxo padrão</button><button type="button" data-example="1">Exceção</button></div><p id="error" class="error" role="alert"></p></section>`;
  const queue = `<section class="review"><div class="section-heading"><span>REVISÃO HUMANA</span><h2>Fila de trabalho <b id="queue-count">0</b></h2><p>Veja os motivos da triagem e registre uma decisão.</p></div><div class="filters"><button type="button" data-filter="all" class="selected">Todos</button><button type="button" data-filter="pending">Pendentes</button><button type="button" data-filter="decided">Decididos</button></div><div id="queue" class="queue"></div></section>`;
  const history = `<section class="history-wrap"><div class="section-heading"><span>RASTRO LOCAL</span><h2>Histórico</h2></div><div id="history" class="history"></div></section>`;
  const footer = `<footer>Dados guardados apenas neste navegador · sem autenticação · sem integração externa</footer>`;
  const hiddenNav = `<nav id="scenario-nav" hidden aria-hidden="true"></nav>`;

  const layouts = {
    education: `<div class="school-shell"><header class="school-header"><div class="school-brand">FORMARE <span>LABORATÓRIO DE FLUXOS</span></div>${actions}</header><main><div class="school-hero"><div>${brand}${heading}</div><div class="school-path"><span>01 / PEDIDO</span><span>02 / TRIAGEM</span><span>03 / DECISÃO</span></div></div>${notice}${metrics}<div class="school-work">${intake}<div>${queue}${history}</div></div>${footer}</main></div>${hiddenNav}`,
    retail: `<div class="store-shell"><header class="store-header"><span>CASA VIVA / ATELIÊ DE OPERAÇÕES</span>${actions}</header><main><div class="store-hero"><div>${brand}${heading}</div><div class="store-seal">DEVOLUÇÕES<br><em>com revisão</em></div></div><div class="store-summary">${metrics}${notice}</div><div class="store-work"><div>${queue}${history}</div>${intake}</div>${footer}</main></div>${hiddenNav}`,
    hospitality: `<div class="hotel-shell"><header class="hotel-header"><span class="hotel-monogram">A</span><span>OPERAÇÕES DE HOSPEDAGEM</span>${actions}</header><main><div class="hotel-hero"><div class="hotel-orbit">${brand}</div><span class="hotel-kicker">AURORA / SERVIÇO E CUIDADO</span>${heading}${notice}</div><div class="hotel-stats">${metrics}</div><div class="hotel-work">${queue}<div>${intake}${history}</div></div>${footer}</main></div>${hiddenNav}`,
    manufacturing: `<div class="factory-shell"><aside class="factory-rail"><div class="factory-mark">TF</div><span>CONTROLE<br>OPERACIONAL</span>${brand}${metrics}<div class="factory-rail-actions">${actions}</div></aside><main><header class="factory-header"><span>SISTEMA DEMONSTRATIVO / QUALIDADE</span><b>LOCAL · 01</b></header><div class="factory-content">${heading}${notice}<div class="factory-work">${queue}${intake}</div>${history}${footer}</div></main></div>${hiddenNav}`,
  };
  document.body.innerHTML = layouts[sector];
})();
