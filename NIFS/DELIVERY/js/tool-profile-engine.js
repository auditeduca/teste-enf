/* ======================================================================
   tool-profile-engine.js — CKO: intro e recursos por perfil (motor clínico é global)
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

  function renderClinicalBridge() {
    return (
      '<p class="profile-clinical-bridge">' +
      '<svg class="icon icon-sm"><use href="#i-brain"/></svg> ' +
      "Após calcular, o raciocínio clínico integrado (NANDA · Nurse-PaLM · evidências) aparece na seção única abaixo dos perfis." +
      "</p>"
    );
  }

  function renderRelated(cko) {
    var tools = (cko.presentation && cko.presentation.related_tools) || [];
    if (!tools.length) return "";
    var inner = '<div class="related-tools-grid profile-related-compact">';
    tools.forEach(function (t) {
      var icon = t.icon || "i-clipboard";
      inner +=
        '<a class="related-tool-card" href="' + esc(t.href) + '">' +
        '<div class="icon-wrap"><svg class="icon"><use href="#' + esc(icon) + '"/></svg></div>' +
        '<div><h3>' + esc(t.title) + "</h3><p>" + esc(t.desc) + "</p></div></a>";
    });
    inner += "</div>";
    return card("Ferramentas relacionadas", inner);
  }

  function renderLearning(cko) {
    var pres = cko.presentation || {};
    var tracks = pres.learning_trail || pres.learning || [];
    if (!tracks.length) return "";
    var inner = '<div class="learning-track-grid profile-learning-compact">';
    tracks.forEach(function (item) {
      var icon = item.icon || "i-book";
      inner +=
        '<a class="learn-card" href="' + esc(item.href || "#") + '">' +
        '<div class="icon-wrap"><svg class="icon"><use href="#' + esc(icon) + '"/></svg></div>' +
        '<h3>' + esc(item.title) + "</h3>" +
        "<p>" + esc(item.desc || "") + "</p>" +
        '<span class="learn-cta">Abrir <svg class="icon icon-sm"><use href="#i-arrow"/></svg></span>' +
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
      renderClinicalBridge(),
      renderMedications(profileId),
      renderLearning(cko),
      renderRelated(cko),
      renderTags(cko),
      profileId === "gestor" ? renderKpi(cko) : ""
    ].join("");
  }

  function mountAll(cko) {
    ["urgencia", "gestor", "estudante", "academico"].forEach(function (profileId) {
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
