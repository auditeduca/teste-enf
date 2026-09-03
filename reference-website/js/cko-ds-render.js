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
  return `<section class="cko-ds-section">
    <h2>${esc(title)}</h2>
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
  return section("Temas (4)", "Troca visual via data-cko-theme. Não altera o estado de release.", `<div class="cko-ds-theme-row">${themes}</div>`);
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
  const cards = ds.templates
    .map(
      (t) => `<article class="cko-ds-comp" data-cko-template="${esc(t.id)}">
        <div class="cko-ds-comp-head"><h3>${esc(t.name)}</h3><span>${esc(t.id)}</span></div>
        <div class="cko-ds-wire" aria-hidden="true"><b></b><i></i><em></em></div>
        <p class="cko-ds-help">${esc(t.note)}</p>
      </article>`
    )
    .join("");
  return section("21 templates", "Molduras de página. Renderer LYR-RND-001 permanece NOT_ASSERTED como motor clínico.", `<div class="cko-ds-tpl-grid">${cards}</div>`);
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

function renderCatalog(ds, mode) {
  const hero = `<section class="cko-ds-hero">
    <span class="cko-ds-badge cko-ds-badge--hold">HOLD / NOT_RELEASED</span>
    <h1>Design system completo via render</h1>
    <p>Tudo inicia em <strong>policy-as-code</strong>. ${esc(ds.inventory.components)} componentes · ${esc(ds.inventory.templates)} templates · ${esc(ds.inventory.themes)} temas · ${esc(ds.inventory.theme_slots)} slots. Nurse-PaLM operacional NOT_ASSERTED.</p>
  </section>`;
  const spine = renderCascade(ds);
  if (mode === "cascade") return hero + spine;
  if (mode === "states") {
    return hero + spine + renderComponents(ds, "states") + renderThemes(ds);
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
      return;
    }
    el.innerHTML = renderCatalog(ds, mode);
  } catch (err) {
    el.innerHTML = `<article class="cko-ds-card cko-ds-card--warn"><p>Catálogo indisponível. ${esc(err.message)}</p></article>`;
  }
}

function boot() {
  document.querySelectorAll("[data-cko-ds-render]").forEach((node) => {
    mount(node);
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}

export { mount, renderCatalog };
