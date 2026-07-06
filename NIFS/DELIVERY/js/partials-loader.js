/* ======================================================================
   partials-loader.js — Orquestrador de módulos via fetch()
   Calculadoras de Enfermagem — Global Platform

   Carrega header, footer, faixa de acessibilidade e sistema de cookies
   a partir de partials/*.html e injeta nos placeholders da página.
   Não altera nenhum CSS/layout — apenas onde o HTML já existente passa
   a ser injetado. Ao final, carrega os scripts que dependem desse HTML
   (mega-menu.js, lang-selector.js, site-widgets.js) e dispara um
   DOMContentLoaded sintético para que os `init()` desses scripts —
   que já esperam esse evento — rodem no momento certo, sem precisar
   alterar uma linha sequer desses arquivos.
   ====================================================================== */
(function () {
  "use strict";

  // Root-absolute paths so partials/scripts resolve from any subdirectory
  // (e.g. /biblioteca/, /en/, /es/) instead of relative to the current page.
  function rootPath(path) {
    return path.charAt(0) === "/" ? path : "/" + path;
  }

  var PARTIALS = [
    { url: rootPath("partials/header.html"), target: "site-header" },
    { url: rootPath("partials/accessibility-toolbar.html"), target: "site-a11y" },
    { url: rootPath("partials/footer.html"), target: "site-footer" },
    { url: rootPath("partials/cookie-system.html"), target: "site-cookie" }
  ];

  var DEPENDENT_SCRIPTS = [
    rootPath("js/global-scripts.js"),
    rootPath("js/mega-menu.js"),
    rootPath("js/i18n-loader.js"),
    rootPath("js/lang-selector.js"),
    rootPath("js/site-widgets.js")
  ];

  function fetchPartial(item) {
    var target = document.getElementById(item.target);
    if (!target) return Promise.resolve();
    return fetch(item.url)
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status + " ao buscar " + item.url);
        return res.text();
      })
      .then(function (html) {
        target.innerHTML = html;
      })
      .catch(function (err) {
        console.error("[partials-loader] Falha ao carregar", item.url, err);
        // Mantém o placeholder vazio em vez de quebrar a página inteira.
      });
  }

  function loadScriptSequentially(src) {
    return new Promise(function (resolve) {
      var script = document.createElement("script");
      script.src = src;
      script.defer = false; // já estamos pós-DOMContentLoaded real; carregar direto
      script.onload = function () { resolve(); };
      script.onerror = function () {
        console.error("[partials-loader] Falha ao carregar script", src);
        resolve(); // não trava os demais scripts por causa de 1 falha
      };
      document.body.appendChild(script);
    });
  }

  function loadDependentScriptsInOrder(index) {
    if (index >= DEPENDENT_SCRIPTS.length) {
      // Todos os scripts carregados: dispara um DOMContentLoaded sintético.
      // Os scripts legados (mega-menu.js/lang-selector.js/site-widgets.js)
      // registram seus init() via document.addEventListener("DOMContentLoaded", init).
      // Esse evento nativo já ocorreu antes do fetch terminar, então os
      // listeners recém-registrados nunca disparariam sozinhos — este
      // evento sintético reaproveita o mesmo listener sem exigir
      // nenhuma edição nesses arquivos.
      document.dispatchEvent(new Event("DOMContentLoaded"));
      document.dispatchEvent(new Event("partials:ready"));
      return;
    }
    loadScriptSequentially(DEPENDENT_SCRIPTS[index]).then(function () {
      loadDependentScriptsInOrder(index + 1);
    });
  }

  function init() {
    Promise.all(PARTIALS.map(fetchPartial)).then(function () {
      loadDependentScriptsInOrder(0);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
