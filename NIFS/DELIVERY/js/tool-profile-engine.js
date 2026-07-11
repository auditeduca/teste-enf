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

  function parseInlineConfig() {
    var el = document.getElementById("tool-config");
    if (!el) return null;
    try {
      return JSON.parse(el.textContent);
    } catch (e) {
      return null;
    }
  }

  function firstLine(text) {
    return String(text || "").split("\n").map(function (line) {
      return line.replace(/^[•\-\s]+/, "").trim();
    }).filter(Boolean)[0] || "";
  }

  function fallbackPresentation(config) {
    config = config || {};
    var overview = config.overview || {};
    var evidence = config.evidence || {};
    var learning = config.learning || {};
    var interpretation = config.interpretation || {};
    var ranges = interpretation.ranges || [];
    var specialty = (overview.specialty || []).slice(0, 4);
    var tags = specialty.map(function (label) {
      return { href: "index.html#calculadoras", label: "#" + String(label).replace(/\s+/g, "") };
    });
    if (overview.acronym) {
      tags.unshift({ href: "index.html#calculadoras", label: "#" + String(overview.acronym).replace(/\s+/g, "") });
    }

    return {
      tags: tags,
      kpis: [
        overview.averageTime ? "Tempo médio de aplicação: " + overview.averageTime : "",
        overview.complexity ? "Complexidade: " + overview.complexity : "",
        overview.evidenceLevel ? "Nível de evidência: " + overview.evidenceLevel : "",
        ranges.length ? "Faixas clínicas: " + ranges.map(function (r) { return r.label; }).join(" • ") : ""
      ].filter(Boolean),
      profileContent: {
        urgencia: {
          title: "Modo Urgência",
          intro: (overview.objective || "Visão rápida para priorização clínica.") + " Use o resultado para estratificação inicial e escalonamento do cuidado.",
          sections: ranges.length ? [{
            heading: "Condutas por faixa",
            items: ranges.slice(0, 4).map(function (r) {
              return (r.label || "Faixa") + ": " + firstLine(r.recommendations || r.clinicalImplications || "");
            }).filter(Boolean)
          }] : []
        },
        gestor: {
          title: "Visão Gestor",
          intro: "Painel orientado a qualidade assistencial, padronização do registro e acompanhamento institucional.",
          sections: [{
            heading: "Indicadores de referência",
            items: [
              overview.averageTime ? "Tempo de aplicação estimado: " + overview.averageTime : "",
              "Registro padronizado do resultado no prontuário",
              "Monitoramento de distribuição por faixa de risco",
              "Reavaliação conforme protocolo institucional"
            ].filter(Boolean)
          }]
        },
        estudante: {
          title: "Visão Estudante",
          intro: "Resumo de aprendizado com foco nos critérios de pontuação, interpretação e pegadinhas frequentes.",
          sections: learning.tips && learning.tips.length ? [{
            heading: "Dicas de estudo",
            items: learning.tips.slice(0, 4)
          }] : []
        },
        academico: {
          title: "Visão Acadêmica",
          intro: "Síntese acadêmica com fundamento teórico, validade clínica e limitações de uso.",
          sections: [{
            heading: "Pérolas de evidência",
            items: [
              firstLine(evidence.foundation),
              firstLine(evidence.history),
              firstLine(evidence.validation),
              firstLine(evidence.limitations)
            ].filter(Boolean)
          }]
        }
      }
    };
  }

  function getPresentation(cko) {
    if (cko && cko.presentation) return cko.presentation;
    var config = (window.ToolCKO && window.ToolCKO.config) || parseInlineConfig() || {};
    return fallbackPresentation(config);
  }

  function renderProfileIntro(profileId, cko) {
    var pres = getPresentation(cko);
    var pc = pres && pres.profileContent && pres.profileContent[profileId];
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
    var tools = (getPresentation(cko).related_tools) || [];
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
    var pres = getPresentation(cko) || {};
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
    var tags = (getPresentation(cko).tags) || [];
    if (!tags.length) return "";
    var inner = '<div class="tool-tags">';
    tags.forEach(function (t) {
      inner += '<a href="' + esc(t.href || "index.html#calculadoras") + '" class="tool-tag">' + esc(t.label) + "</a>";
    });
    inner += "</div>";
    return card("Hashtags clínicas", inner);
  }

  function renderKpi(cko) {
    var kpis = (getPresentation(cko).kpis) || [];
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
      if (!mount || mount.childElementCount > 0) return;
      mount.innerHTML = '<div class="profile-shared-stack">' + blocksForProfile(profileId, cko) + "</div>";
    });
  }

  function init() {
    whenReady(function (cko) {
      if (!document.getElementById("tool-config")) return;
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
