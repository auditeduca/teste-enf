/* ======================================================================
   partials-loader.js — Orquestrador de módulos via fetch()
   Calculadoras de Enfermagem — Global Platform

   Carrega header, footer, faixa de acessibilidade e sistema de cookies
   a partir de partials/*.html e injeta nos placeholders da página.
   Resolve caminhos relativos à raiz do site (funciona em html/ ou na raiz).
   Ao final, carrega os scripts dependentes e dispara partials:ready.
   ====================================================================== */
(function () {
  "use strict";

  var BASE = detectBasePath();

  function detectBasePath() {
    var scripts = document.getElementsByTagName("script");
    for (var i = 0; i < scripts.length; i++) {
      var src = scripts[i].getAttribute("src") || "";
      if (src.indexOf("partials-loader.js") !== -1) {
        try {
          var url = new URL(src, window.location.href);
          return url.pathname.replace(/js\/partials-loader\.js.*$/, "");
        } catch (e) { /* fall through */ }
      }
    }
    if (/\/html\//.test(window.location.pathname)) return "../";
    return "";
  }

  function assetPath(path) {
    if (/^(https?:|\/|data:|#)/.test(path)) return path;
    return BASE + path.replace(/^\.\//, "");
  }

  function rewritePartialPaths(html) {
    var base = BASE || "/";
    if (base.charAt(base.length - 1) !== "/") base += "/";
    return html.replace(
      /(\s(?:href|src|action)=["'])((?!\/|https?:|mailto:|#|javascript:|data:)[^"']*)/gi,
      function (_match, prefix, url) {
        return prefix + base + url.replace(/^\.\//, "");
      }
    );
  }

  function mountPartialHtml(target, html) {
    target.innerHTML = rewritePartialPaths(html);
    var modals = target.querySelectorAll(".ck-modal-overlay");
    for (var i = 0; i < modals.length; i++) {
      document.body.appendChild(modals[i]);
    }
  }

  function ensureChromeStyles() {
    var hasSiteStyles = document.querySelector(
      'link[rel="stylesheet"][href*="site-styles.css"]'
    );
    if (!hasSiteStyles) {
      var siteCss = document.createElement("link");
      siteCss.rel = "stylesheet";
      siteCss.href = assetPath("css/site-styles.css");
      document.head.appendChild(siteCss);
    }
  }

  function fixAssetLinks() {
    document.querySelectorAll('link[rel="stylesheet"][href^="css/"]').forEach(function (el) {
      var href = el.getAttribute("href");
      if (href && href.indexOf(BASE) !== 0) el.href = assetPath(href);
    });
  }

  var PARTIALS = [
    { url: assetPath("partials/header.html"), target: "site-header" },
    { url: assetPath("partials/accessibility-toolbar.html"), target: "site-a11y" },
    { url: assetPath("partials/footer.html"), target: "site-footer" },
    { url: assetPath("partials/cookie-system.html"), target: "site-cookie" }
  ];

  var DEPENDENT_SCRIPTS = [
    assetPath("js/global-scripts.js"),
    assetPath("js/mega-menu.js"),
    assetPath("js/i18n-loader.js"),
    assetPath("js/lang-selector.js"),
    assetPath("js/site-widgets.js")
  ];

  var CALC_ENGINE = assetPath("js/calc-engine-v2.js");

  function fetchPartial(item) {
    var target = document.getElementById(item.target);
    if (!target) return Promise.resolve();
    return fetch(item.url)
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status + " ao buscar " + item.url);
        return res.text();
      })
      .then(function (html) {
        mountPartialHtml(target, html);
      })
      .catch(function (err) {
        console.error("[partials-loader] Falha ao carregar", item.url, err);
      });
  }

  function loadScriptSequentially(src) {
    return new Promise(function (resolve) {
      if (document.querySelector('script[src="' + src + '"]')) {
        resolve();
        return;
      }
      var script = document.createElement("script");
      script.src = src;
      script.defer = false;
      script.onload = function () { resolve(); };
      script.onerror = function () {
        console.error("[partials-loader] Falha ao carregar script", src);
        resolve();
      };
      document.body.appendChild(script);
    });
  }

  function finishPartialsReady() {
    document.dispatchEvent(new Event("DOMContentLoaded"));
    document.dispatchEvent(new Event("partials:ready"));
  }

  function loadDependentScriptsInOrder(index) {
    if (index >= DEPENDENT_SCRIPTS.length) {
      if (document.getElementById("tool-config")) {
        loadScriptSequentially(CALC_ENGINE).then(finishPartialsReady);
        return;
      }
      finishPartialsReady();
      return;
    }
    loadScriptSequentially(DEPENDENT_SCRIPTS[index]).then(function () {
      loadDependentScriptsInOrder(index + 1);
    });
  }

  function init() {
    ensureChromeStyles();
    fixAssetLinks();
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
