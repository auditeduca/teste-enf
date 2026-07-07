/* ======================================================================
   tool-profile-engine.js — CKO + mounts do motor clínico em todos os perfis
   ====================================================================== */
(function () {
  "use strict";

  function esc(s) {
    var d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function whenReady(fn) {
    if (window.ToolCKO && window.ToolCKO.ready) {
      window.ToolCKO.ready.then(fn);
    } else {
      document.addEventListener("DOMContentLoaded", function () {
        if (window.ToolCKO && window.ToolCKO.ready) window.ToolCKO.ready.then(fn);
      });
    }
  }

  function card(title, bodyHtml) {
    return (
      '<section class="calc-card profile-cko-card">' +
      '<div class="calc-card-header"><span class="bar" aria-hidden="true"></span><h2 style="font-size:15px">' +
      esc(title) +
      "</h2></div>" +
      bodyHtml +
      "</section>"
    );
  }

  function listItems(items) {
    if (!items || !items.length) return "";
    return '<ul class="tips-list">' + items.map(function (t) {
      return '<li><svg class="icon"><use href="#i-clipcheck"/></svg> ' + esc(t) + "</li>";
    }).join("") + "</ul>";
  }

  function renderProfileIntro(profileId, cko) {
    var pc = cko.presentation && cko.presentation.profileContent && cko.presentation.profileContent[profileId];
    if (!pc) return "";
    var html = '<p class="flow-text">' + esc(pc.intro || "") + "</p>";
    if (pc.sections) {
      pc.sections.forEach(function (sec) {
        html += "<h4 style=\"font-size:13px;margin:14px 0 6px\">" + esc(sec.heading) + "</h4>" + listItems(sec.items);
      });
    }
    return card(pc.title || "Perfil", html);
  }

  /** Trilha lógica: cálculo → NANDA/NIC/NOC → CIP → Nurse-PaLM → recursos */
  function renderClinicalEngineLane(profileId) {
    return (
      '<div class="clinical-intelligence-lane" data-profile-clinical-flow hidden>' +
      '<div class="flow-divider"><span>Motor clínico integrado</span></div>' +
      '<section class="calc-card flow-card profile-cko-card">' +
      '<div class="calc-card-header"><span class="bar" aria-hidden="true"></span>' +
      '<h2 style="font-size:15px"><svg class="icon icon-sm"><use href="#i-brain"/></svg> Raciocínio NANDA · NIC · NOC</h2></div>' +
      '<div class="nnn-grid">' +
      '<div><span class="nnn-label">Diagnóstico (NANDA-I)</span><p class="nnn-value" data-nnn-nanda>—</p></div>' +
      '<div><span class="nnn-label">Intervenção (NIC)</span><p class="nnn-value" data-nnn-nic>—</p></div>' +
      '<div><span class="nnn-label">Resultado (NOC)</span><p class="nnn-value" data-nnn-noc>—</p></div>' +
      "</div></section>" +
      '<section class="cip-section cip-hidden" data-cip-section>' +
      '<h2 class="cip-section-title">Clinical Intelligence Package</h2>' +
      '<p class="cip-section-intro">6 dimensões de inteligência clínica alimentadas pelo resultado do cálculo</p>' +
      '<div class="cip-mount cip-hidden" data-cip-mount data-profile="' + esc(profileId) + '"></div>' +
      "</section>" +
      '<section class="cog-section-wrapper cip-hidden" data-cog-section>' +
      '<div class="cognitive-panel cip-hidden" data-cognitive-mount data-profile="' + esc(profileId) + '">' +
      '<div class="cognitive-panel-header">' +
      '<h3><i class="fa-solid fa-brain"></i> Análise Cognitiva — Nurse-PaLM</h3>' +
      '<span class="cognitive-badge">Motor Clínico</span></div>' +
      '<div data-cognitive-panel-content></div></div></section>' +
      "</div>"
    );
  }

  function renderKgLinks(cko) {
    var links = (cko.presentation && cko.presentation.kg_links) || [];
    if (!links.length) return "";
    var inner = '<div class="cip-kg-links-list">';
    links.forEach(function (l) {
      inner += '<a href="' + esc(l.href) + '" class="cip-kg-link"><i class="fa-solid ' + esc(l.icon) + '"></i> ' + esc(l.label) + "</a>";
    });
    inner += "</div>";
    return (
      '<section class="cip-kg-links profile-kg-links" data-kg-section>' +
      "<h3><i class=\"fa-solid fa-link\"></i> Recursos conectados</h3>" +
      inner +
      "</section>"
    );
  }

  function renderRelated(cko) {
    var tools = (cko.presentation && cko.presentation.related_tools) || [];
    if (!tools.length) return "";
    var inner = '<div class="related-tools-grid profile-related-compact">';
    tools.forEach(function (t) {
      inner +=
        '<a class="related-tool-card" href="' + esc(t.href) + '">' +
        '<div><h3>' + esc(t.title) + "</h3><p>" + esc(t.desc) + "</p></div></a>";
    });
    inner += "</div>";
    return card("Ferramentas relacionadas", inner);
  }

  function renderLearning(cko) {
    var tracks = (cko.presentation && cko.presentation.learning) || [];
    if (!tracks.length) return "";
    var inner = '<div class="learning-track-grid profile-learning-compact">';
    tracks.forEach(function (item) {
      inner +=
        '<a class="learn-card" href="' + esc(item.href || "#") + '">' +
        '<h3>' + esc(item.title) + "</h3>" +
        "<p>" + esc(item.desc || "") + "</p>" +
        "</a>";
    });
    inner += "</div>";
    return card("Trilha de aprendizagem", inner);
  }

  function renderTags(cko) {
    var tags = (cko.presentation && cko.presentation.tags) || [];
    if (!tags.length) return "";
    var inner = '<div class="tool-tags">';
    tags.forEach(function (t) {
      inner += '<a href="' + esc(t.href || "index.html#calculadoras") + '" class="tool-tag">' + esc(t.label) + "</a>";
    });
    inner += "</div>";
    return card("Hashtags clínicas", inner);
  }

  function renderKpi(cko) {
    var kpis = (cko.presentation && cko.presentation.kpis) || [];
    if (!kpis.length) return "";
    return card("Indicadores (referência NKOS)", listItems(kpis));
  }

  function renderMedications(profileId) {
    return (
      '<section class="calc-card profile-cko-card profile-med-card" data-profile-med-mount="' +
      esc(profileId) +
      '" hidden>' +
      '<div class="calc-card-header"><span class="bar" aria-hidden="true"></span>' +
      '<h2 style="font-size:15px"><svg class="icon icon-sm"><use href="#i-pills"/></svg> Medicamentos — Base de Dados</h2></div>' +
      '<p class="med-link-band" data-profile-med-band="' + esc(profileId) + '"></p>' +
      '<p class="flow-text" data-profile-med-summary="' + esc(profileId) + '"></p>' +
      '<div class="med-links-grid" data-profile-med-grid="' + esc(profileId) + '"></div>' +
      '<p class="med-link-disclaimer">Referência da base NKOS. Prescrição e administração dependem de avaliação médica e protocolo institucional.</p>' +
      "</section>"
    );
  }

  function blocksForProfile(profileId, cko) {
    return [
      renderProfileIntro(profileId, cko),
      renderClinicalEngineLane(profileId),
      renderMedications(profileId),
      renderKgLinks(cko),
      renderLearning(cko),
      renderRelated(cko),
      renderTags(cko),
      profileId === "gestor" ? renderKpi(cko) : ""
    ].join("");
  }

  function mountAll(cko) {
    var profiles = (cko.presentation && cko.presentation.profiles) ||
      ["padrao", "urgencia", "gestor", "estudante", "academico"];

    profiles.forEach(function (profileId) {
      if (profileId === "padrao") return;
      var mount = document.querySelector('[data-profile-shared="' + profileId + '"]');
      if (!mount) return;
      mount.innerHTML = '<div class="profile-shared-stack">' + blocksForProfile(profileId, cko) + "</div>";
    });
  }

  function init() {
    whenReady(function (cko) {
      if (!cko) return;
      mountAll(cko);
      document.dispatchEvent(new CustomEvent("tool-profile:ready", { detail: { cko: cko } }));
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
