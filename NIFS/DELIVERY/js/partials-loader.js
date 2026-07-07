/* ======================================================================
   partials-loader.js — Orquestrador de módulos via fetch()
   Calculadoras de Enfermagem — Global Platform
   ====================================================================== */
(function () {
  "use strict";

  var SCRIPT = document.currentScript;

  function detectBasePath() {
    if (SCRIPT && SCRIPT.src) {
      try {
        var url = new URL(SCRIPT.src, window.location.href);
        return url.pathname.replace(/js\/partials-loader\.js.*$/, "");
      } catch (e) { /* fall through */ }
    }
    var scripts = document.getElementsByTagName("script");
    for (var i = 0; i < scripts.length; i++) {
      var src = scripts[i].getAttribute("src") || "";
      if (src.indexOf("partials-loader.js") !== -1) {
        try {
          var u = new URL(src, window.location.href);
          return u.pathname.replace(/js\/partials-loader\.js.*$/, "");
        } catch (e2) { /* fall through */ }
      }
    }
    if (/\/html\//.test(window.location.pathname)) return "../";
    return "";
  }

  var BASE = detectBasePath();

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
      if (href && href.indexOf(BASE) !== 0 && BASE) el.href = assetPath(href);
    });
  }

  function showA11yBar() {
    var bar = document.getElementById("barraAcessibilidade");
    if (bar) bar.classList.add("show");
  }

  function injectFallbackHeader(target) {
    target.innerHTML =
      '<header class="rd-header"><div class="rd-container rd-header-inner">' +
      '<a href="' + assetPath("index.html") + '" class="rd-logo">' +
      '<span>Calculadoras de Enfermagem</span></a></div></header>';
  }

  var PARTIALS = [
    { url: assetPath("partials/header.html"), target: "site-header", fallback: injectFallbackHeader },
    { url: assetPath("partials/accessibility-toolbar.html"), target: "site-a11y" },
    { url: assetPath("partials/footer.html"), target: "site-footer" },
    { url: assetPath("partials/cookie-system.html"), target: "site-cookie" }
];;

  var DEPENDENT_SCRIPTS = [
    assetPath("js/global-scripts.js"),
    assetPath("js/mega-menu.js"),
    assetPath("js/i18n-loader.js"),
    assetPath("js/lang-selector.js"),
    assetPath("js/site-widgets.js")
  ];

  var COGNITIVE_SCRIPTS = [
    assetPath("js/nurse-palm.js"),
    assetPath("js/cognitive-ui.js")
  ];

  function ckoScripts() {
    var body = document.body;
    if (!body) return [];
    if (body.getAttribute("data-tool-cko") || body.getAttribute("data-page") === "apgar") {
      return [
        assetPath("js/tool-cko-loader.js"),
        assetPath("js/tool-profile-engine.js")
      ];
    }
    return [];
  }

  var CALC_ENGINE = assetPath("js/calc-engine-v2.js");

  function fetchPartial(item) {
    var target = document.getElementById(item.target);
    if (!target) return Promise.resolve();
    return fetch(item.url, { credentials: "same-origin" })
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status + " ao buscar " + item.url);
        return res.text();
      })
      .then(function (html) {
        mountPartialHtml(target, html);
        if (item.target === "site-a11y") showA11yBar();
      })
      .catch(function (err) {
        console.error("[partials-loader] Falha ao carregar", item.url, err);
        if (item.fallback) item.fallback(target);
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
    showA11yBar();
    document.dispatchEvent(new Event("partials:ready"));
  }

  function loadDependentScriptsInOrder(index) {
    if (index >= DEPENDENT_SCRIPTS.length) {
      if (document.getElementById("tool-config")) {
        loadCkoThenCognitive();
        return;
      }
      finishPartialsReady();
      return;
    }
    loadScriptSequentially(DEPENDENT_SCRIPTS[index]).then(function () {
      loadDependentScriptsInOrder(index + 1);
    });
  }

  function loadScriptsList(list, idx, onDone) {
    idx = idx || 0;
    if (idx >= list.length) {
      onDone();
      return;
    }
    loadScriptSequentially(list[idx]).then(function () {
      loadScriptsList(list, idx + 1, onDone);
    });
  }

  function loadCognitiveScriptsThenCalcEngine(idx) {
    idx = idx || 0;
    if (idx >= COGNITIVE_SCRIPTS.length) {
      loadScriptSequentially(CALC_ENGINE).then(finishPartialsReady);
      return;
    }
    loadScriptSequentially(COGNITIVE_SCRIPTS[idx]).then(function () {
      loadCognitiveScriptsThenCalcEngine(idx + 1);
    });
  }

  function loadCkoThenCognitive() {
    var list = ckoScripts();
    loadScriptsList(list, 0, function () {
      loadCognitiveScriptsThenCalcEngine(0);
    });
  }

  function loadPrintTemplate() {
    if (document.getElementById("printTemplate")) return Promise.resolve();
    var mount = document.getElementById("printTemplateMount");
    if (!mount) return Promise.resolve();
    return fetch(assetPath("partials/relatorio-fiel.html"), { credentials: "same-origin" })
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status + " ao buscar relatorio-fiel");
        return res.text();
      })
      .then(function (html) {
        mount.innerHTML = html;
      })
      .catch(function (err) {
        console.error("[partials-loader] Falha ao carregar relatorio-fiel", err);
      });
  }

  function init() {
    ensureChromeStyles();
    fixAssetLinks();
    Promise.all(PARTIALS.map(fetchPartial))
      .then(function () { return loadPrintTemplate(); })
      .then(function () {
        document.body.classList.add("has-site-chrome");
        loadDependentScriptsInOrder(0);
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
