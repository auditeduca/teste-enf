/* ======================================================================
   tool-footer-renderer.js — Trilha, recursos adicionais, tags e relacionadas (perfil Padrão)
   Fonte: ToolCKO.data.presentation (CKO overlay)
   ====================================================================== */
(function () {
  "use strict";

  function esc(s) {
    var d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
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
    if (!mountEl || !cko) return;
    var pres = (cko.presentation || {});
    mountEl.innerHTML = renderFooter(pres);
    document.dispatchEvent(new CustomEvent("tool-footer:ready", { detail: { cko: cko } }));
  }

  function init() {
    if (window.ToolCKO && window.ToolCKO.ready) {
      window.ToolCKO.ready.then(function (cko) {
        if (cko) mount(cko);
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
