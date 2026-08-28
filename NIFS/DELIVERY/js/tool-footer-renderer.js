/* ======================================================================
   tool-footer-renderer.js — Trilha, recursos adicionais, tags e relacionadas (perfil Padrão)
   Fonte: ToolCKO.data.presentation (CKO overlay) ou fallback via tool-config
   ====================================================================== */
(function () {
  "use strict";

  function esc(s) {
    var d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
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

  function fallbackPresentation(config) {
    config = config || {};
    var overview = config.overview || {};
    var specialty = (overview.specialty || []).slice(0, 4);
    var tags = specialty.map(function (label) {
      return { href: "index.html#calculadoras", label: "#" + String(label).replace(/\s+/g, "") };
    });
    if (overview.acronym) {
      tags.unshift({ href: "index.html#calculadoras", label: "#" + String(overview.acronym).replace(/\s+/g, "") });
    }
    var name = overview.name || overview.acronym || "esta ferramenta";
    return {
      learning_trail: [
        { title: "Biblioteca de Recursos", desc: "Literatura, protocolos e materiais de apoio para " + name + ".", href: "biblioteca.html", icon: "i-book" },
        { title: "Protocolos", desc: "Fluxos operacionais e padronização assistencial.", href: "protocolos.html", icon: "i-clipboard" },
        { title: "SAE", desc: "Diagnósticos, resultados e intervenções de enfermagem.", href: "sae.html", icon: "i-file" },
        { title: "Medicamentos", desc: "Base de referência para condutas farmacológicas.", href: "medicamentos.html", icon: "i-pills" }
      ],
      additional_resources: [
        { title: "NANDA-I", desc: "Diagnósticos de enfermagem padronizados.", href: "diagnosticosnanda.html", icon: "i-brain" },
        { title: "Nurse-PaLM", desc: "Dashboard de raciocínio clínico assistido.", href: "nurse-palm.html", icon: "i-brain" },
        { title: "Quiz & Provas", desc: "Teste seus conhecimentos com questões clínicas.", href: "biblioteca-provas.html", icon: "i-clipboard" }
      ],
      tags: tags,
      related_tools: config.related_tools || []
    };
  }

  function getPresentation(cko) {
    if (cko && cko.presentation) return cko.presentation;
    var config = (window.ToolCKO && window.ToolCKO.config) || parseInlineConfig() || {};
    return fallbackPresentation(config);
  }

  function learnCard(item) {
    var icon = item.icon || "i-book";
    var cta = item.cta || "Abrir";
    var ctaIcon = item.ctaIcon === "download" ? "#i-download" : "#i-arrow";
    return (
      '<a class="learn-card" href="' + esc(item.href || "#") + '">' +
      '<div class="icon-wrap"><svg class="icon"><use href="#' + esc(icon) + '"/></svg></div>' +
      "<h3>" + esc(item.title) + "</h3>" +
      "<p>" + esc(item.desc || "") + "</p>" +
      '<span class="learn-cta">' + esc(cta) + ' <svg class="icon icon-sm"><use href="' + ctaIcon + '"/></svg></span>' +
      "</a>"
    );
  }

  function gridSection(title, items) {
    if (!items || !items.length) return "";
    var cards = items.map(learnCard).join("");
    return (
      '<div class="flow-divider"><span>' + esc(title) + "</span></div>" +
      '<div class="learning-track-wrap"><div class="learning-track-grid">' + cards + "</div></div>"
    );
  }

  function renderFooter(pres) {
    pres = pres || {};
    var trail = pres.learning_trail || pres.learning || [];
    var extra = pres.additional_resources || [];
    var tags = pres.tags || [];
    var related = pres.related_tools || [];

    var html = gridSection("Trilha de Aprendizagem", trail);
    html += gridSection("Recursos Adicionais", extra);

    if (!tags.length && !related.length) return html;

    html += '<section class="tool-footer-zone">';
    if (tags.length) {
      html += '<div class="tool-tags">';
      tags.forEach(function (t) {
        html += '<a href="' + esc(t.href || "index.html#calculadoras") + '" class="tool-tag">' + esc(t.label) + "</a>";
      });
      html += "</div>";
    }
    if (related.length) {
      html += '<h2 class="related-tools-title">Ferramentas relacionadas</h2><div class="related-tools-grid">';
      related.forEach(function (t) {
        var icon = t.icon || "i-clipboard";
        html +=
          '<a class="related-tool-card" href="' + esc(t.href) + '">' +
          '<div class="icon-wrap"><svg class="icon"><use href="#' + esc(icon) + '"/></svg></div>' +
          "<div><h3>" + esc(t.title) + "</h3><p>" + esc(t.desc) + "</p></div></a>";
      });
      html += "</div>";
    }
    html += "</section>";
    return html;
  }

  function mount(cko) {
    var mountEl = document.getElementById("toolFooterMount");
    if (!mountEl || mountEl.childElementCount > 0) return;
    var pres = getPresentation(cko);
    var html = renderFooter(pres);
    if (!html) return;
    mountEl.innerHTML = html;
    document.dispatchEvent(new CustomEvent("tool-footer:ready", { detail: { cko: cko } }));
  }

  function init() {
    if (!document.getElementById("toolFooterMount")) return;
    if (window.ToolCKO && window.ToolCKO.ready) {
      window.ToolCKO.ready.then(function (cko) {
        mount(cko);
      });
    } else {
      mount(null);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
