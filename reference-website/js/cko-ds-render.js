/**
 * LYR-DS-001 / LYR-UI-001 — render the canonical design system from JSON.
 * HOLD / NOT_RELEASED. Nurse-PaLM operational: NOT_ASSERTED.
 */
const esc = (value) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");

function section(title, note, inner) {
  const id = "ds-" + String(title || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 48);
  return `<section class="cko-ds-section" ${id ? `id="${esc(id)}"` : ""}>
    <h2${id ? ` id="${esc(id)}-title"` : ""}>${esc(title)}</h2>
    ${note ? `<p class="cko-ds-help">${esc(note)}</p>` : ""}
    ${inner}
  </section>`;
}

function renderTokens(ds) {
  const colors = ds.tokens.color
    .map(
      (c) => `<div class="cko-ds-swatch">
        <i style="background:${esc(c.value)}"></i>
        <b>${esc(c.id)}</b>
        <small>${esc(c.token)} · ${esc(c.value)}</small>
      </div>`
    )
    .join("");
  const type = ds.tokens.typography
    .map((t) => {
      const cls = t.sampleClass ? ` class="${esc(t.sampleClass)}"` : "";
      return `<div${cls}><strong>${esc(t.id)}</strong> · ${esc(t.spec)}<div>${esc(t.sample)}</div></div>`;
    })
    .join("");
  const space = ds.tokens.space
    .map(
      (s) => `<div class="cko-ds-space-bar"><code>--cko-space-${esc(s.id)}</code>
        <i style="width:${esc(s.value)}"></i><span>${esc(s.value)}</span></div>`
    )
    .join("");
  const radius = ds.tokens.radius
    .map(
      (r) => `<div class="cko-ds-rad" style="border-radius:${esc(r.value)}">${esc(r.id)} ${esc(r.value)}</div>`
    )
    .join("");
  const shadow = ds.tokens.shadow
    .map(
      (s) => `<div class="cko-ds-elev" style="box-shadow:${esc(s.value)}">${esc(s.id)}</div>`
    )
    .join("");
  return (
    section("Cor", "Paleta institucional navy. Nenhuma cor de release clínico.", `<div class="cko-ds-swatch-grid">${colors}</div>`) +
    section("Tipografia", "Nunito Sans para títulos, Inter para leitura.", `<div class="cko-ds-type-stack">${type}</div>`) +
    section("Espaçamento", "Escala de 4px. Gaps de marca permanecem em hold.", `<div class="cko-ds-space-stack">${space}</div>`) +
    section("Raio", "", `<div class="cko-ds-radius-row">${radius}</div>`) +
    section("Elevação", "Sombras ainda com hold de proveniência.", `<div class="cko-ds-shadow-row">${shadow}</div>`)
  );
}

function renderThemes(ds) {
  const switcher = (ds.themes || [])
    .map(
      (t) =>
        `<button type="button" class="cko-ds-btn cko-ds-btn--secondary" data-cko-theme-set="${esc(t.id)}">${esc(t.name)}</button>`
    )
    .join("");
  const themes = ds.themes
    .map(
      (t) => `<article class="cko-ds-card" data-cko-theme="${esc(t.id)}">
        <span class="cko-ds-badge">${esc(t.id)}</span>
        <h3>${esc(t.name)}</h3>
        <p>${esc(t.note)}</p>
        <div class="cko-ds-stage">
          <button class="cko-ds-btn cko-ds-btn--primary" type="button">Primário</button>
          <button class="cko-ds-btn cko-ds-btn--ghost" type="button">Ghost</button>
        </div>
      </article>`
    )
    .join("");
  return section(
    "Temas (4)",
    "Troca visual via data-cko-theme. Não altera o estado de release.",
    `<div class="cko-ds-theme-switch" role="group" aria-label="Pré-visualizar tema">${switcher}</div><div class="cko-ds-theme-row">${themes}</div>`
  );
}

function renderSlots(ds) {
  const slots = ds.theme_slots
    .map(
      (s) => `<a class="cko-ds-slot" href="${esc(s.href)}" style="background:${esc(s.color)}">
        <span>${String(s.index).padStart(2, "0")} · <code>${esc(s.layer_id)}</code></span>
        <strong>${esc(s.name)}</strong>
        <small>${esc(s.token)}</small>
      </a>`
    )
    .join("");
  return section(
    "44 theme slots",
    "Um slot cromático por camada classificada. Cobertura 44/44. HOLD / NOT_RELEASED.",
    `<div class="cko-ds-slot-grid">${slots}</div>`
  );
}

function renderComponents(ds, mode) {
  const states = mode === "states";
  const cards = ds.components
    .map((c) => {
      const extra = states
        ? `<div class="cko-ds-stage" data-state="focus"><span class="cko-ds-help">estado: foco / hover / disabled via CSS</span>${c.html}</div>`
        : "";
      return `<article class="cko-ds-comp" data-cko-component="${esc(c.id)}" data-cko-kind="${esc(c.kind)}">
        <div class="cko-ds-comp-head"><h3>${esc(c.name)}</h3><span>${esc(c.id)}</span></div>
        <div class="cko-ds-stage">${c.html}</div>
        ${extra}
      </article>`;
    })
    .join("");
  const title = states ? "37 componentes · estados de interação" : "37 componentes";
  return section(title, "HTML canónico injectado a partir do catálogo. Sem claim operacional.", `<div class="cko-ds-comp-grid${states ? " cko-ds-states" : ""}">${cards}</div>`);
}

function renderTemplates(ds) {
  const implemented = ds.templates_implemented_n ?? ds.templates.filter((t) => t.status === "implemented").length;
  const cards = ds.templates
    .map((t) => {
      const status = t.status || "wireframe";
      const link = t.html
        ? `<p class="cko-ds-help">HTML: <a class="cko-ds-link" href="/${esc(t.html)}">${esc(t.html)}</a></p>`
        : `<p class="cko-ds-help">Moldura apenas. Sem chrome HTML.</p>`;
      const gov = t.governed_by || {};
      const policyChip = gov.policy
        ? `<span class="cko-ds-badge cko-ds-badge--hold">${esc(gov.policy)}</span>`
        : `<span class="cko-ds-badge">${esc(gov.contract || "POLICY_MASTER_CONTRACT")}</span>`;
      return `<article class="cko-ds-comp" data-cko-template="${esc(t.id)}" data-cko-template-status="${esc(status)}" data-cko-governed-by="${esc(gov.policy || gov.contract || "")}">
        <div class="cko-ds-comp-head"><h3>${esc(t.name)}</h3><span>${esc(t.id)}</span></div>
        <span class="cko-ds-badge ${status === "implemented" ? "" : "cko-ds-badge--hold"}">${esc(status)}</span>
        ${policyChip}
        <div class="cko-ds-wire" aria-hidden="true"><b></b><i></i><em></em></div>
        <p class="cko-ds-help">${esc(t.note)}</p>
        <p class="cko-ds-help">Contrato ${esc(gov.contract || "—")} · ${esc((gov.utc || []).join(" ") || "UTC-046")} · ${esc(gov.status || "UNBOUND")}</p>
        ${link}
      </article>`;
    })
    .join("");
  const govRule = ds.template_governance?.rule || "Templates especializam POLICY_MASTER_CONTRACT. tool/scale também CKO-POL-UT-001.";
  return section(
    "21 templates",
    `${implemented} com chrome HTML. Restantes em wireframe. ${govRule} Renderer LYR-RND-001 permanece NOT_ASSERTED como motor clínico.`,
    `<div class="cko-ds-tpl-grid">${cards}</div>`
  );
}

function renderHolds(ds) {
  const items = ds.holds.map((h) => `<li><code>${esc(h)}</code></li>`).join("");
  return section(
    "Holds",
    "O catálogo renderizado não fecha B9 nem publica conteúdo clínico.",
    `<ul>${items}</ul><p class="cko-ds-help">Autoridade aceite: ${esc(ds.accepted_authority)}. Proposta em hold: ${esc(ds.proposal_hold)}.</p>`
  );
}

function renderCascade(ds) {
  const stages = Array.isArray(ds.cascade) ? ds.cascade : [];
  const items = stages
    .map((id, i) => {
      const pred = i === 0 ? "raiz" : stages[i - 1];
      const note = i === 0 ? "tudo inicia aqui" : `só corre se ${pred} PASS`;
      return `<li class="cko-ds-cascade-step" data-cko-stage="${esc(id)}">
        <span class="cko-ds-badge ${i === 0 ? "cko-ds-badge--hold" : ""}">${i === 0 ? "raiz" : "↓"}</span>
        <strong>${esc(id)}</strong>
        <small>${esc(note)}</small>
      </li>`;
    })
    .join("");
  return section(
    "Cascata de garantia",
    ds.rule || "tudo inicia em policy-as-code; estágio seguinte só corre se o predecessor PASS",
    `<ol class="cko-ds-cascade" data-cko-cascade-root="${esc(ds.root || "policy-as-code")}">${items}</ol>`
  );
}

function renderHumanHolds(ledger) {
  const items = (ledger.items || [])
    .map(
      (item) => `<article class="cko-ds-card cko-ds-card--hold" data-cko-hold="${esc(item.id)}">
        <span class="cko-ds-badge cko-ds-badge--hold">${esc(item.status)}</span>
        <h3>${esc(item.id)}</h3>
        <p>${esc(item.decision)}</p>
        <p class="cko-ds-help">Código: ${esc(item.code_progress || "nenhum avanço automático")}. Humano: ${esc(item.next_human || "decisão pendente")}.</p>
      </article>`
    )
    .join("");
  return `<section class="cko-ds-hero">
      <span class="cko-ds-badge cko-ds-badge--hold">${esc(ledger.release || "HOLD / NOT_RELEASED")}</span>
      <h1>Holds humanos</h1>
      <p>${esc(ledger.rule)}. Não bloqueiam inspect/CI. Continuam a negar release. B9 permanece NOT_RELEASED.</p>
    </section>
    <div class="cko-ds-comp-grid">${items}</div>`;
}

function renderUniversalTool(policy) {
  const findings = (policy.evaluation?.findings || [])
    .map(
      (f) => `<li><code>${esc(f.id)}</code> <span class="cko-ds-badge">${esc(f.severity)}</span> ${esc(f.text)}</li>`
    )
    .join("");
  const chips = (policy.controls || [])
    .map((c) => `<li><code>${esc(c.id)}</code></li>`)
    .join("");
  const preview = (policy.controls || []).slice(0, 8);
  const last = (policy.controls || []).slice(-1)[0];
  const rows = [...preview, last]
    .filter(Boolean)
    .map(
      (c) => `<tr>
        <th scope="row"><code>${esc(c.id)}</code></th>
        <td>${esc(c.primary_layer)}</td>
        <td>${esc(c.requirement)}</td>
        <td><span class="cko-ds-badge cko-ds-badge--hold">${esc(c.status)}</span></td>
      </tr>`
    )
    .join("");
  return `<section class="cko-ds-hero">
      <span class="cko-ds-badge cko-ds-badge--hold">${esc(policy.release || "HOLD / NOT_RELEASED")}</span>
      <h1>${esc(policy.document_id)} v${esc(policy.document_version)}</h1>
      <p>Política Universal de Ferramentas. Veredito <strong>${esc(policy.evaluation?.verdict)}</strong>. DOCUMENTADO ≠ IMPLANTADO ≠ ASSURED. Calculadoras ${esc(policy.clinical_calculators)}; MD ${esc(policy.md_gate)}.</p>
    </section>
    <section class="cko-ds-section">
      <h2>Gate</h2>
      <ul class="cko-ds-ut-meta">
        <li>Controlos ${esc(policy.control_count)} · implementados ${esc(policy.implemented_n)}</li>
        <li>Especializa <code>${esc(policy.specializes || policy.parent || "")}</code></li>
        <li>Templates ${esc(policy.template_governance?.status || "UNBOUND")} · ${esc((policy.template_governance?.templates || []).map((t) => t.id).join(", "))}</li>
        <li>ABNT NBR 6023:${esc(policy.abnt?.nbr_6023?.edition)} clause ${esc(policy.abnt?.nbr_6023?.clause_level)}</li>
        <li>Linha de versão ${esc(policy.version_lineage?.status)}</li>
        <li>Promoção clínica ${esc(policy.evaluation?.clinical_promotion)}</li>
      </ul>
    </section>
    <section class="cko-ds-section">
      <h2>Achados da avaliação</h2>
      <ul class="cko-ds-ut-findings">${findings}</ul>
    </section>
    <section class="cko-ds-section">
      <h2>UTC-001 … UTC-098</h2>
      <p class="cko-ds-help">98 controlos DOCUMENTADO_HOLD. Nenhum PASS. A grelha identifica o catálogo; o detalhe abre em amostra (UTC-039).</p>
      <ul class="cko-ds-ut-chips">${chips}</ul>
      <div class="cko-ds-table-wrap"><table class="cko-ds-ut-table">
        <thead><tr><th>ID</th><th>Camada</th><th>Requisito</th><th>Estado</th></tr></thead>
        <tbody>${rows}</tbody>
      </table></div>
    </section>`;
}

function renderPolicyMaster(policy) {
  const chips = (policy.fields || [])
    .map((f) => `<li><code>${esc(f.seq)}</code> ${esc(f.id)}</li>`)
    .join("");
  const rows = (policy.fields || [])
    .map(
      (f) => `<tr>
        <th scope="row"><code>${esc(f.seq)}</code> ${esc(f.id)}</th>
        <td>${esc(f.question)}</td>
        <td>${esc(f.meaning)}</td>
        <td><span class="cko-ds-badge">${esc(f.base_kind)}</span> ${esc(f.bases)}</td>
      </tr>`
    )
    .join("");
  const principles = (policy.principles || [])
    .map((p) => `<li><code>${esc(p.id)}</code> ${esc(p.name)}</li>`)
    .join("");
  return `<section class="cko-ds-hero">
      <span class="cko-ds-badge cko-ds-badge--hold">${esc(policy.status || "CONTROLLED_TEMPLATE_HOLD")}</span>
      <h1>${esc(policy.document_id)} v${esc(policy.document_version)}</h1>
      <p>Molde congelado. Políticas especializam estes 28 campos. Não é ACTIVE. DOCUMENTADO ≠ IMPLANTADO ≠ ASSURED.</p>
    </section>
    <section class="cko-ds-section">
      <h2>28 campos</h2>
      <p class="cko-ds-help">${esc(policy.golden_rule || "")}</p>
      <ul class="cko-ds-ut-chips">${chips}</ul>
      <div class="cko-ds-table-wrap"><table class="cko-ds-table">
        <thead><tr><th>Campo</th><th>Pergunta</th><th>O que é</th><th>Base normativa</th></tr></thead>
        <tbody>${rows}</tbody>
      </table></div>
    </section>
    <section class="cko-ds-section">
      <h2>P01–P20</h2>
      <ul class="cko-ds-ut-chips">${principles}</ul>
      <p class="cko-ds-help">${esc(policy.template_governance_rule || "")}</p>
    </section>`;
}

function renderVisualAssets(policy) {
  const fam = (policy.families || [])
    .map(
      (f) => `<article class="cko-ds-card"><span class="cko-ds-badge">${esc(f.id)}</span><h3>${esc(f.name)}</h3><p>${esc(f.purpose)}</p></article>`
    )
    .join("");
  const langs = (policy.object_languages || [])
    .map((o) => `<li><code>${esc(o.code)}</code> ${esc(o.object_type)}</li>`)
    .join("");
  return `<section class="cko-ds-hero">
      <span class="cko-ds-badge cko-ds-badge--hold">${esc(policy.release || "HOLD / NOT_RELEASED")}</span>
      <h1>Visual Asset System</h1>
      <p>Não é uma imagem por página. O objeto canônico gera projeções Web, Social e File. Não é 45ª camada. Gerador ${esc(policy.generator?.operational)}. Word/PPT não gerados.</p>
    </section>
    <section class="cko-ds-section">
      <h2>Três famílias</h2>
      <div class="cko-ds-theme-row">${fam}</div>
    </section>
    <section class="cko-ds-section">
      <h2>Linguagens de objeto</h2>
      <ul class="cko-ds-ut-chips">${langs}</ul>
      <p class="cko-ds-help">OG ${esc(policy.dimensions?.og?.width)}×${esc(policy.dimensions?.og?.height)} · LinkedIn ${esc(policy.dimensions?.linkedin?.width)}×${esc(policy.dimensions?.linkedin?.height)} · uma fonte, múltiplas projeções.</p>
    </section>`;
}

function renderIdentityManual(ds) {
  const identity = ds.identity_manual || {};
  const typeRows = (ds.tokens.typography || [])
    .map(
      (t) => `<tr>
        <th scope="row">${esc(t.id)}</th>
        <td>${esc(t.spec)}</td>
        <td>${esc(t.sample)}</td>
      </tr>`
    )
    .join("");
  const chrome = [
    ["Header global", "#global-header-container · partials/header.html"],
    ["Idioma", "#language-selector-placeholder · lang-selector.js"],
    ["Acessibilidade", "partials/accessibility-toolbar.html"],
    ["Hero do cluster", ".cko-cart-hero via shell · um H1"],
    ["Grid", ".cko-layout = main + sidebar 280px"],
    ["Footer", "#footer-placeholder · partials/footer.html"],
    ["Escala", "templates/scale.html · " + (identity.scale_specimen || "escala-padrao.html")],
  ]
    .map((row) => `<tr><th scope="row">${esc(row[0])}</th><td>${esc(row[1])}</td></tr>`)
    .join("");
  const buttons = (ds.components || [])
    .filter((c) => c.kind === "button")
    .map((c) => `<div class="cko-ds-stage">${c.html}</div>`)
    .join("");
  return (
    `<nav class="cko-ds-manual-toc" aria-label="Secções do manual">
      <a href="#ds-manual-tokens">Cor e tipo</a>
      <a href="#ds-manual-chrome">Chrome do cluster</a>
      <a href="#ds-manual-buttons">Botões</a>
      <a href="#ds-manual-scale">Escala</a>
    </nav>` +
    `<section class="cko-ds-section" id="ds-manual-tokens">
      <h2>Identidade v10 no catálogo</h2>
      <p class="cko-ds-help">${esc(identity.rule || "Manual v10 ingerido. Sem HTML solto. HOLD / NOT_RELEASED.")}</p>
      <p class="cko-ds-help">Estado <code>${esc(identity.status || "INGESTED_HOLD")}</code> · versão ${esc(identity.version || "v10")}. Tokens <code>--navy</code> / <code>--navy-light</code> / <code>--navy-dark</code> aliasam <code>--cko-navy-*</code>.</p>
    </section>` +
    renderTokens(ds) +
    `<section class="cko-ds-section" id="ds-manual-type-table">
      <h2>Tipografia (tabela)</h2>
      <div class="cko-ds-table-wrap"><table class="cko-ds-table">
        <thead><tr><th>Papel</th><th>Spec</th><th>Amostra</th></tr></thead>
        <tbody>${typeRows}</tbody>
      </table></div>
    </section>` +
    `<section class="cko-ds-section" id="ds-manual-chrome">
      <h2>Chrome do cluster</h2>
      <p class="cko-ds-help">O manual v10 demonstrava header, idioma, a11y e footer com HTML próprio. No padrão CKO esses blocos vêm dos partials e do shell — um de cada, sem cópia inline.</p>
      <div class="cko-ds-table-wrap"><table class="cko-ds-table">
        <thead><tr><th>Peça</th><th>Fonte canónica</th></tr></thead>
        <tbody>${chrome}</tbody>
      </table></div>
    </section>` +
    `<section class="cko-ds-section" id="ds-manual-buttons">
      <h2>Botões</h2>
      <div class="cko-ds-button-grid">${buttons}</div>
    </section>` +
    `<section class="cko-ds-section" id="ds-manual-scale">
      <h2>Espécime de escala</h2>
      <p class="cko-ds-help">Template <code>scale</code> no cluster. Sem hero navy local. Sem promoção clínica.</p>
      <p><a class="cko-ds-link" href="/escala-padrao.html">Abrir escala padrão</a> · <a class="cko-ds-link" href="/templates/scale.html">HTML do template</a></p>
    </section>` +
    renderThemes(ds) +
    renderHolds(ds)
  );
}

function renderCatalog(ds, mode) {
  const hero = `<section class="cko-ds-hero">
    <span class="cko-ds-badge cko-ds-badge--hold">HOLD / NOT_RELEASED</span>
    <h1>Design system completo via render</h1>
    <p>Tudo inicia em <strong>policy-as-code</strong>. ${esc(ds.inventory.components)} componentes · ${esc(ds.inventory.templates)} templates · ${esc(ds.inventory.themes)} temas · ${esc(ds.inventory.theme_slots)} slots. Nurse-PaLM operacional NOT_ASSERTED.</p>
  </section>`;
  const spine = renderCascade(ds);
  if (mode === "manual") return renderIdentityManual(ds);
  if (mode === "cascade") return hero + spine;
  if (mode === "states") {
    return hero + spine + renderComponents(ds, "states") + renderThemes(ds);
  }
  if (mode === "templates") {
    return hero + spine + renderTemplates(ds);
  }
  return hero + spine + renderTokens(ds) + renderThemes(ds) + renderSlots(ds) + renderComponents(ds, mode) + renderTemplates(ds) + renderHolds(ds);
}

function renderLayers(ds, layers) {
  const rows = (layers.layers || [])
    .map((layer) => {
      const slot = ds.theme_slots.find((s) => s.layer_id === layer.id);
      const color = slot ? slot.color : "var(--cko-navy-900)";
      return `<a class="cko-ds-slot" href="${esc(layer.href)}" style="background:${esc(color)}">
        <span>${esc(layer.seq)} · <code>${esc(layer.id)}</code></span>
        <strong>${esc(layer.name)}</strong>
        <small>${esc(layer.release)} · holds ${esc(layer.holds_n)}</small>
      </a>`;
    })
    .join("");
  return `<section class="cko-ds-hero">
      <span class="cko-ds-badge cko-ds-badge--hold">${esc(layers.release || "HOLD / NOT_RELEASED")}</span>
      <h1>44 camadas classificadas do PDF</h1>
      <p>Grelha pintada a partir de <code>layers.json</code> e dos 44 theme slots. Cobertura 44/44. Sem publicação.</p>
    </section>
    <div class="cko-ds-slot-grid">${rows}</div>`;
}

async function loadJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`CKO DS fetch failed ${res.status} ${url}`);
  return res.json();
}

function refreshShellToc() {
  if (window.CKOPageShell && typeof window.CKOPageShell.refreshToc === "function") {
    window.CKOPageShell.refreshToc();
  }
}

async function mount(el) {
  const mode = el.dataset.ckoDsRender || "catalog";
  const src = el.dataset.ckoDsSrc || "/data/cko/design-system.json";
  try {
    const ds = await loadJson(src);
    if (ds.published === true || ds.release === "RELEASED") {
      el.innerHTML = `<article class="cko-ds-card cko-ds-card--warn"><p>Fail-closed: catálogo recusou estado RELEASED.</p></article>`;
      return;
    }
    if (mode === "layers") {
      const layersSrc = el.dataset.ckoLayersSrc || "/data/cko/layers.json";
      const layers = await loadJson(layersSrc);
      el.innerHTML = renderLayers(ds, layers);
      refreshShellToc();
      return;
    }
    if (mode === "universal-tool") {
      const policy = src.includes("universal-tool") ? ds : await loadJson("/data/cko/universal-tool.json");
      el.innerHTML = renderUniversalTool(policy);
      refreshShellToc();
      return;
    }
    if (mode === "policy-master") {
      const policy = src.includes("policy-master") ? ds : await loadJson("/data/cko/policy-master.json");
      el.innerHTML = renderPolicyMaster(policy);
      refreshShellToc();
      return;
    }
    if (mode === "visual-assets") {
      const policy = src.includes("visual-assets") ? ds : await loadJson("/data/cko/visual-assets.json");
      el.innerHTML = renderVisualAssets(policy);
      refreshShellToc();
      return;
    }
    if (mode === "human-holds") {
      const ledger = src.includes("human-decisions") ? ds : await loadJson("/data/cko/human-decisions.json");
      el.innerHTML = renderHumanHolds(ledger);
      refreshShellToc();
      return;
    }
    if (mode === "manual") {
      el.innerHTML = renderIdentityManual(ds);
      refreshShellToc();
      return;
    }
    el.innerHTML = renderCatalog(ds, mode);
    refreshShellToc();
  } catch (err) {
    el.innerHTML = `<article class="cko-ds-card cko-ds-card--warn"><p>Catálogo indisponível. ${esc(err.message)}</p></article>`;
  }
}

function bindThemeSwitch() {
  document.addEventListener("click", (event) => {
    const btn = event.target.closest("[data-cko-theme-set]");
    if (!btn) return;
    const theme = btn.getAttribute("data-cko-theme-set");
    document.documentElement.setAttribute("data-cko-theme", theme);
    document.body.setAttribute("data-cko-theme", theme);
  });
}

function boot() {
  bindThemeSwitch();
  document.querySelectorAll("[data-cko-ds-render]").forEach((node) => {
    mount(node);
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}

export { mount, renderCatalog, renderUniversalTool, renderPolicyMaster, renderVisualAssets };
