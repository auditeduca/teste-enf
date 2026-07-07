/* ======================================================================
   tool-profile-engine.js — Conteúdo CKO compartilhado em todos os perfis
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

  function renderCognitive(cko) {
    var sae = (cko.reasoning && cko.reasoning.sae) || {};
    var nanda = (sae.nanda || []).map(function (n) { return n.diagnosis; }).join("; ") || "—";
    var nic = (sae.nic || []).map(function (n) { return n.intervention; }).join("; ") || "—";
    var noc = (sae.noc || []).map(function (n) { return n.outcome; }).join("; ") || "—";
    return card("Raciocínio NANDA · NIC · NOC", (
      '<p class="flow-text"><strong>NANDA:</strong> ' + esc(nanda) + "</p>" +
      '<p class="flow-text"><strong>NIC:</strong> ' + esc(nic) + "</p>" +
      '<p class="flow-text"><strong>NOC:</strong> ' + esc(noc) + "</p>"
    ));
  }

  function renderAi(cko) {
    var ai = cko.ai || {};
    var html = "";
    if (ai.summary) html += '<p class="flow-text">' + esc(ai.summary) + "</p>";
    if (ai.clinicalPearls && ai.clinicalPearls.length) {
      html += "<h4 style=\"font-size:13px;margin:12px 0 6px\">Pérolas clínicas</h4>" + listItems(ai.clinicalPearls);
    }
    if (ai.commonErrors && ai.commonErrors.length) {
      html += "<h4 style=\"font-size:13px;margin:12px 0 6px\">Erros comuns</h4>" + listItems(ai.commonErrors);
    }
    if (ai.explainLikeResident) {
      html += '<p class="flow-text" style="margin-top:10px;font-style:italic">' + esc(ai.explainLikeResident) + "</p>";
    }
    return card("Inteligência clínica (GEO)", html);
  }

  function renderEvidence(cko) {
    var ev = cko.evidence || {};
    var html = "";
    if (ev.foundation) html += "<p>" + esc(ev.foundation) + "</p>";
    if (ev.validation) html += '<p style="margin-top:8px">' + esc(ev.validation) + "</p>";
    if (ev.limitations) html += '<p style="margin-top:8px"><strong>Limitações:</strong> ' + esc(ev.limitations) + "</p>";
    if (ev.references && ev.references.length) {
      html += '<ol class="ref-list" style="margin-top:10px;font-size:12px">';
      ev.references.forEach(function (ref, i) {
        var text = typeof ref === "string" ? ref : (ref.text || ref.title || "");
        html += '<li><span class="ref-num">' + (i + 1) + "</span>" + esc(text) + "</li>";
      });
      html += "</ol>";
    }
    return card("Evidências", html);
  }

  function renderKgLinks(cko) {
    var links = (cko.presentation && cko.presentation.kg_links) || [];
    if (!links.length) return "";
    var inner = '<div class="cip-kg-links-list">';
    links.forEach(function (l) {
      inner += '<a href="' + esc(l.href) + '" class="cip-kg-link"><i class="fa-solid ' + esc(l.icon) + '"></i> ' + esc(l.label) + "</a>";
    });
    inner += "</div>";
    return card("Recursos conectados", inner);
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
    var kpis = (cko.presentation && cko.presentation.kpis) || [
      "Avaliações registradas por unidade/período",
      "Percentual de escores na faixa esperada",
      "Casos de alto risco (Apgar ≤6) por semana"
    ];
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
      renderCognitive(cko),
      renderAi(cko),
      renderEvidence(cko),
      renderKgLinks(cko),
      renderRelated(cko),
      renderLearning(cko),
      renderTags(cko),
      renderKpi(cko),
      renderMedications(profileId)
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
